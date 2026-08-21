"""
Workout Player module for Cycling Performance Studio Lab.

Provides:
- ZWO workout file parsing (XML-based structured workout format)
- Real-time power target timeline generation
- Playback state management (start/stop/pause/skip)
- Trainer control abstraction (ANT+ / BLE smart trainers)
- Integration hooks for real power meter data

Architecture:
- WorkoutPlayerSession: Manages playback state for a single workout
- ZWOParser: Parses .zwo XML files into interval timelines
- TrainerController: Abstract base + ANT+/BLE implementations
- WorkoutRegistry: Central session store for the running app
"""

import json
import logging
import math
import os
import threading
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("cpsl.workout_player")


class IntervalType(Enum):
    WARMUP = "warmup"
    STEADY = "steady"
    COOLDOWN = "cooldown"
    INTERVAL = "interval"
    RAMP = "ramp"
    FREE_RIDE = "freeride"
    REST = "rest"


@dataclass
class Interval:
    """A single interval segment within a workout."""
    index: int
    start_time: float
    duration: float
    power_low: float = 0.0
    power_high: float = 0.0
    power: float = 0.0
    interval_type: IntervalType = IntervalType.STEADY
    name: str = ""
    ramp_rate: float = 0.0


@dataclass
class WorkoutTimeline:
    """Complete timeline of power targets for a parsed workout."""
    name: str
    description: str
    author: str
    duration_total: float
    ftp: float
    intervals: list[Interval] = field(default_factory=list)

    def get_target_at_time(self, elapsed: float) -> tuple[float, Optional[Interval]]:
        for interval in self.intervals:
            if interval.start_time <= elapsed < interval.start_time + interval.duration:
                if interval.interval_type == IntervalType.WARMUP or interval.interval_type == IntervalType.COOLDOWN:
                    frac = (elapsed - interval.start_time) / interval.duration if interval.duration > 0 else 0
                    target = interval.power_low + (interval.power_high - interval.power_low) * frac
                    return target, interval
                elif interval.interval_type == IntervalType.RAMP:
                    frac = (elapsed - interval.start_time) / interval.duration if interval.duration > 0 else 0
                    target = interval.power_low + (interval.power_high - interval.power_low) * frac
                    return target, interval
                else:
                    return interval.power, interval
        return 0.0, None

    def get_intervals_summary(self) -> list[dict[str, Any]]:
        return [
            {
                "index": i.index,
                "name": i.name or i.interval_type.value,
                "start_time": round(i.start_time, 1),
                "duration": round(i.duration, 1),
                "power_low": round(i.power_low, 4),
                "power_high": round(i.power_high, 4),
                "power": round(i.power, 4),
                "type": i.interval_type.value,
            }
            for i in self.intervals
        ]


class ZWOParser:
    """Parses .zwo XML workout files into WorkoutTimeline objects."""

    @staticmethod
    def parse(file_path: str | Path, ftp: float = 250.0) -> WorkoutTimeline:
        path = Path(file_path)
        tree = ET.parse(path)
        root = tree.getroot()

        name_elem = root.find(".//name")
        desc_elem = root.find(".//description")
        author_elem = root.find(".//author")

        name = name_elem.text if name_elem is not None else path.stem
        description = desc_elem.text if desc_elem is not None else ""
        author = author_elem.text if author_elem is not None else "Unknown"

        workout_elem = root.find(".//workout")
        if workout_elem is None:
            raise ValueError("No <workout> element found in ZWO file")

        intervals: list[Interval] = []
        current_time = 0.0
        interval_index = 0

        for child in workout_elem:
            tag = child.tag.lower()
            attrs = child.attrib

            if tag in ("warmup", "cooldown"):
                duration = float(attrs.get("Duration", attrs.get("duration", 60)))
                power_low = float(attrs.get("PowerLow", attrs.get("power_low", 0.55)))
                power_high = float(attrs.get("PowerHigh", attrs.get("power_high", 0.65)))
                interval_type = IntervalType.WARMUP if tag == "warmup" else IntervalType.COOLDOWN

                intervals.append(Interval(
                    index=interval_index,
                    start_time=current_time,
                    duration=duration,
                    power_low=power_low,
                    power_high=power_high,
                    interval_type=interval_type,
                    name=f"{'Warmup' if tag == 'warmup' else 'Cooldown'} ({duration/60:.1f} min)"
                ))
                interval_index += 1
                current_time += duration

            elif tag in ("steady", "steadystate"):
                duration = float(attrs.get("Duration", attrs.get("duration", 60)))
                power = float(attrs.get("Power", attrs.get("power", 1.0)))

                intervals.append(Interval(
                    index=interval_index,
                    start_time=current_time,
                    duration=duration,
                    power=power,
                    power_low=power,
                    power_high=power,
                    interval_type=IntervalType.STEADY,
                    name=str(attrs.get("name", f"Steady ({duration/60:.1f} min @ {power*100:.0f}% FTP)"))
                ))
                interval_index += 1
                current_time += duration

            elif tag in ("interval",):
                duration = float(attrs.get("Duration", attrs.get("duration", 60)))
                power = float(attrs.get("Power", attrs.get("power", 1.0)))

                intervals.append(Interval(
                    index=interval_index,
                    start_time=current_time,
                    duration=duration,
                    power=power,
                    power_low=power,
                    power_high=power,
                    interval_type=IntervalType.INTERVAL,
                    name=str(attrs.get("name", f"Interval ({duration/60:.1f} min @ {power*100:.0f}% FTP)"))
                ))
                interval_index += 1
                current_time += duration

            elif tag in ("ramp",):
                duration = float(attrs.get("Duration", attrs.get("duration", 60)))
                power_low = float(attrs.get("PowerLow", attrs.get("power_low", 0.5)))
                power_high = float(attrs.get("PowerHigh", attrs.get("power_high", 1.0)))
                ramp_rate = (power_high - power_low) / (duration / 60.0) if duration > 0 else 0.0

                intervals.append(Interval(
                    index=interval_index,
                    start_time=current_time,
                    duration=duration,
                    power_low=power_low,
                    power_high=power_high,
                    interval_type=IntervalType.RAMP,
                    ramp_rate=ramp_rate,
                    name=f"Ramp ({duration/60:.1f} min, {power_low*100:.0f}%->{power_high*100:.0f}% FTP)"
                ))
                interval_index += 1
                current_time += duration

            elif tag in ("freeride", "free"):
                duration = float(attrs.get("Duration", attrs.get("duration", 300)))
                intervals.append(Interval(
                    index=interval_index,
                    start_time=current_time,
                    duration=duration,
                    power=0.0,
                    power_low=0.0,
                    power_high=1.2,
                    interval_type=IntervalType.FREE_RIDE,
                    name=f"Free Ride ({duration/60:.1f} min)"
                ))
                interval_index += 1
                current_time += duration

        total_duration = current_time
        timeline = WorkoutTimeline(
            name=name,
            description=description,
            author=author,
            duration_total=total_duration,
            ftp=ftp,
            intervals=intervals,
        )
        return timeline


class PlaybackState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class PlaybackStatus:
    state: PlaybackState = PlaybackState.IDLE
    elapsed: float = 0.0
    current_power: float = 0.0
    target_power: float = 0.0
    interval_index: int = 0
    intensity_pct: float = 1.0
    started_at: Optional[float] = None
    paused_at: Optional[float] = None
    total_duration: float = 0.0
    target_interval_name: str = "None"
    power_history: list[dict] = field(default_factory=list)
    target_history: list[dict] = field(default_factory=list)
    last_interval_change: float = 0.0


class WorkoutPlayerSession:
    """Manages playback state and real-time targets for a single workout."""

    def __init__(self, timeline: WorkoutTimeline, rider_power: Optional[float] = None):
        self.timeline = timeline
        self.rider_power = rider_power
        self.status = PlaybackStatus(total_duration=timeline.duration_total)
        self._lock = threading.RLock()
        self._timer: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._trainer: Optional["TrainerController"] = None
        self._update_interval = 1.0

    def set_trainer(self, trainer: "TrainerController"):
        self._trainer = trainer

    def start(self):
        with self._lock:
            if self.status.state == PlaybackState.RUNNING:
                return
            self.status.state = PlaybackState.RUNNING
            self.status.started_at = time.time()
            self.status.paused_at = None
            if self.status.elapsed == 0:
                self.status.elapsed = 0.0
            self._stop_flag.clear()
            self._timer = threading.Thread(target=self._run_loop, daemon=True)
            self._timer.start()

    def stop(self):
        with self._lock:
            self._stop_flag.set()
            self.status.state = PlaybackState.IDLE
            self.status.elapsed = 0.0
            self.status.current_power = 0.0
            self.status.target_power = 0.0
            self.status.interval_index = 0

    def pause(self):
        with self._lock:
            if self.status.state != PlaybackState.RUNNING:
                return
            self._stop_flag.set()
            self.status.state = PlaybackState.PAUSED
            self.status.paused_at = time.time()

    def resume(self):
        with self._lock:
            if self.status.state != PlaybackState.PAUSED:
                return
            self._stop_flag.clear()
            self.status.state = PlaybackState.RUNNING
            self.status.started_at = time.time() - self.status.elapsed
            self._timer = threading.Thread(target=self._run_loop, daemon=True)
            self._timer.start()

    def set_intensity(self, pct: float):
        with self._lock:
            self.status.intensity_pct = pct

    def skip_to_time(self, target_time: float):
        with self._lock:
            self.status.elapsed = max(0.0, min(target_time, self.timeline.duration_total))
            self._update_target()

    def skip_interval(self, direction: int = 1):
        with self._lock:
            current_idx = self.status.interval_index
            new_idx = current_idx + direction
            if 0 <= new_idx < len(self.timeline.intervals):
                self.status.interval_index = new_idx
                self.status.elapsed = self.timeline.intervals[new_idx].start_time

    def report_power(self, power: float):
        with self._lock:
            self.status.current_power = power
            now = time.time()
            if len(self.status.power_history) > 3600:
                self.status.power_history = self.status.power_history[-3600:]
            self.status.power_history.append({
                "t": round(now, 1),
                "power": round(power, 1),
                "target": round(self.status.target_power, 1),
            })

    def _run_loop(self):
        # v1.3.1 DEADLOCK FIX: the loop used to time.sleep(1) WHILE holding
        # self._lock, so every user-facing call (skip_interval, report_power,
        # pause, stop) queued behind a full tick — under concurrent load this
        # livelocked the session (pytest-timeout stack: skip_interval blocked
        # on _lock at line 315). The lock is now held only for the state
        # snapshot; the trainer BLE write and the wait happen OUTSIDE it, and
        # the wait uses _stop_flag.wait() so stop() reacts instantly.
        while not self._stop_flag.is_set():
            target_power = None
            with self._lock:
                if self.status.state != PlaybackState.RUNNING:
                    break

                elapsed_since_start = time.time() - self.status.started_at if self.status.started_at else self.status.elapsed
                self.status.elapsed = elapsed_since_start

                if self.status.elapsed >= self.timeline.duration_total:
                    self.status.state = PlaybackState.COMPLETED
                    self._stop_flag.set()
                    break

                self._update_target()
                target_power = self.status.target_power

            # Trainer I/O outside the lock: a slow BLE write must never block
            # user interactions for the duration of the transfer.
            if self._trainer is not None and target_power is not None:
                try:
                    self._trainer.set_target_power(target_power)
                except Exception as e:
                    log.debug(f"Trainer update failed: {e}")

            # Interruptible wait OUTSIDE the lock (replaces time.sleep).
            self._stop_flag.wait(self._update_interval)

    def _update_target(self):
        target_power, interval = self.timeline.get_target_at_time(self.status.elapsed)
        target_power *= self.status.intensity_pct

        if interval is not None:
            if interval.index != self.status.interval_index:
                self.status.interval_index = interval.index
                self.status.last_interval_change = self.status.elapsed
                self.status.target_interval_name = interval.name or interval.interval_type.value
            self.status.target_power = target_power
        else:
            self.status.target_power = 0.0
            self.status.target_interval_name = "Cooldown/Recovery"

        if len(self.status.target_history) > 3600:
            self.status.target_history = self.status.target_history[-3600:]
        self.status.target_history.append({
            "t": round(self.status.elapsed, 1),
            "target": round(target_power, 1),
            "interval_idx": self.status.interval_index,
        })

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "state": self.status.state.value,
                "elapsed": round(self.status.elapsed, 1),
                "current_power": round(self.status.current_power, 1),
                "target_power": round(self.status.target_power, 1),
                "interval_index": self.status.interval_index,
                "intensity_pct": self.status.intensity_pct,
                "total_duration": round(self.status.total_duration, 1),
                "target_interval_name": self.status.target_interval_name,
                "ftp": self.timeline.ftp,
                "workout_name": self.timeline.name,
                "workout_description": self.timeline.description,
                "power_smoothing": 5,
                "intervals": self.timeline.get_intervals_summary(),
            }


class TrainerController:
    """Abstract base for trainer control. Implementations use ANT+ or BLE."""

    def __init__(self, trainer_id: str = ""):
        self.trainer_id = trainer_id
        self.is_connected = False
        self._target_power = 0.0
        self._resistance = 0.0
        self._slope = 0.0

    def connect(self) -> bool:
        raise NotImplementedError

    def disconnect(self):
        self.is_connected = False

    def set_target_power(self, power: float, duration: float = 0.0):
        self._target_power = power

    def set_resistance(self, resistance: float):
        self._resistance = resistance

    def set_slope(self, slope: float, gradient: float = 0.0):
        self._slope = slope

    def get_status(self) -> dict[str, Any]:
        return {
            "connected": self.is_connected,
            "trainer_id": self.trainer_id,
            "target_power": round(self._target_power, 1),
            "resistance": round(self._resistance, 2),
            "slope": round(self._slope, 2),
        }


class ANTPlusTrainer(TrainerController):
    """ANT+ FE-C trainer control (requires openant library)."""

    def __init__(self, trainer_id: str = "", device_number: int = 0):
        super().__init__(trainer_id)
        self.device_number = device_number
        self._node = None

    def connect(self) -> bool:
        try:
            from openant import bls, easy
            self._node = easy.Node()
            self._node.start()
            self.is_connected = True
            return True
        except ImportError:
            log.warning("openant library not available for ANT+ trainer control")
            return False
        except Exception as e:
            log.error(f"ANT+ trainer connection failed: {e}")
            return False


class BLETrainer(TrainerController):
    """BLE (Bluetooth Low Energy) trainer control via bleak."""

    def __init__(self, trainer_id: str = "", address: str = ""):
        super().__init__(trainer_id)
        self.address = address
        self._client = None
        self._write_chr = None

    def connect(self) -> bool:
        try:
            from bleak import BleakClient
            self._client = BleakClient(self.address)
            # In headless environments, we can't actually connect, so simulate
            self.is_connected = True
            return True
        except ImportError:
            log.warning("bleak library not available for BLE trainer control")
            return False
        except Exception as e:
            log.error(f"BLE trainer connection failed: {e}")
            return False

    def set_target_power(self, power: float, duration: float = 0.0):
        self._target_power = power
        # Would send to trainer here via write characteristic
        # For now, just store the target


class WorkoutRegistry:
    """Singleton-style registry for workout player sessions."""

    _instance: Optional["WorkoutRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._active_sessions: dict[str, WorkoutPlayerSession] = {}
                    cls._instance._connected_trainers: dict[str, TrainerController] = {}
        return cls._instance

    @classmethod
    def get(cls) -> "WorkoutRegistry":
        return cls()

    def create_session(self, timeline: WorkoutTimeline, session_id: Optional[str] = None) -> WorkoutPlayerSession:
        if session_id is None:
            session_id = f"session_{int(time.time() * 1000)}"
        session = WorkoutPlayerSession(timeline)
        self._active_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[WorkoutPlayerSession]:
        return self._active_sessions.get(session_id)

    def end_session(self, session_id: str):
        session = self._active_sessions.pop(session_id, None)
        if session:
            session.stop()

    def list_sessions(self) -> list[str]:
        return list(self._active_sessions.keys())

    def register_trainer(self, trainer: TrainerController) -> str:
        trainer_id = trainer.trainer_id or f"trainer_{int(time.time() * 1000)}"
        self._connected_trainers[trainer_id] = trainer
        return trainer_id

    def get_trainer(self, trainer_id: str) -> Optional[TrainerController]:
        return self._connected_trainers.get(trainer_id)

    def list_trainers(self) -> list[dict[str, Any]]:
        return [t.get_status() for t in self._connected_trainers.values()]


def get_workout_files(works_dir: Optional[str | Path] = None) -> list[Path]:
    """Find all .zwo workout files in the workouts directory."""
    from user_home import cpsl_home
    if works_dir is None:
        works_dir = cpsl_home() / "workouts"
    works_path = Path(works_dir)
    if not works_path.exists():
        return []
    return sorted(works_path.rglob("*.zwo"))


def load_workout_by_name(name: str, works_dir: Optional[str | Path] = None, ftp: float = 250.0) -> Optional[WorkoutTimeline]:
    """Load a workout timeline by name from the workouts directory."""
    for f in get_workout_files(works_dir):
        if f.stem == name:
            timeline = ZWOParser.parse(f, ftp)
            return timeline
    return None


def resolve_workout_path(filename: str, works_dir: Optional[str | Path] = None) -> Optional[Path]:
    """Resolve a workout filename to its full path. Supports nested directories."""
    if works_dir is None:
        works_dir = Path("workouts")
    works_path = Path(works_dir)
    if not works_path.exists():
        from user_home import cpsl_home
        works_path = cpsl_home() / "workouts"
    for f in works_path.rglob("*.zwo"):
        if f.name == filename or f.stem == filename:
            return f
    return None
