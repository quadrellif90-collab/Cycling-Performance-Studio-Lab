"""v0.9.0 — Custom Formula Alerts (Ride Cave-style).

Allows users to define custom alert conditions based on ride metrics.
Alerts fire when conditions are met during or after a ride.

References:
  - Ride Cave: "Custom Widgets & Alerts — Build custom data tiles with a
    formula language, plus alerts that fire on any live metric: power,
    heart rate, cadence, W/kg, W'bal, and more."

Supported metrics for alerts:
  - power_w, power_wkg, power_pct_ftp
  - hr_bpm, hr_pct_max, hr_zones
  - cadence_rpm
  - speed_kmh
  - tss, if_avg, np_w
  - wbal_j, wbal_pct
  - decoupling_pct
  - distance_km, elevation_m
  - duration_min
  - kilojoules

Operators: >, <, >=, <=, ==, !=, between

Alert types:
  - threshold:  fire when metric crosses a value
  - zone:       fire when metric enters/exits a zone
  - streak:     fire after N consecutive seconds meeting condition
  - summary:    fire at ride end if condition was met during ride
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable


# Supported metrics with descriptions
SUPPORTED_METRICS = {
    "power_w": {"label": "Power (W)", "unit": "watts", "type": "float"},
    "power_wkg": {"label": "Power (W/kg)", "unit": "W/kg", "type": "float"},
    "power_pct_ftp": {"label": "Power (% FTP)", "unit": "%", "type": "float"},
    "hr_bpm": {"label": "Heart Rate (bpm)", "unit": "bpm", "type": "float"},
    "hr_pct_max": {"label": "Heart Rate (% max)", "unit": "%", "type": "float"},
    "cadence_rpm": {"label": "Cadence (rpm)", "unit": "rpm", "type": "float"},
    "speed_kmh": {"label": "Speed (km/h)", "unit": "km/h", "type": "float"},
    "tss": {"label": "Training Stress Score", "unit": "TSS", "type": "float"},
    "if_avg": {"label": "Intensity Factor", "unit": "IF", "type": "float"},
    "np_w": {"label": "Normalized Power (W)", "unit": "watts", "type": "float"},
    "wbal_j": {"label": "W' Balance (J)", "unit": "J", "type": "float"},
    "wbal_pct": {"label": "W' Balance (%)", "unit": "%", "type": "float"},
    "decoupling_pct": {"label": "Aerobic Decoupling (%)", "unit": "%", "type": "float"},
    "distance_km": {"label": "Distance (km)", "unit": "km", "type": "float"},
    "elevation_m": {"label": "Elevation (m)", "unit": "m", "type": "float"},
    "duration_min": {"label": "Duration (min)", "unit": "min", "type": "float"},
    "kilojoules": {"label": "Energy (kJ)", "unit": "kJ", "type": "float"},
}

OPERATORS = [">", "<", ">=", "<=", "==", "!=", "between"]


@dataclass
class AlertRule:
    """A single alert rule definition."""
    id: str
    name: str
    metric: str              # e.g. "power_w", "hr_bpm"
    operator: str            # e.g. ">", "<", "between"
    value: float             # Threshold value
    value2: Optional[float] = None  # For "between" operator
    streak_seconds: int = 0  # 0 = immediate, >0 = require N consecutive seconds
    enabled: bool = True
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "metric": self.metric,
            "operator": self.operator,
            "value": self.value,
            "value2": self.value2,
            "streak_seconds": self.streak_seconds,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }


@dataclass
class AlertEvent:
    """An alert that was triggered."""
    rule_id: str
    rule_name: str
    metric: str
    operator: str
    threshold: float
    actual_value: float
    timestamp_s: float       # Seconds into the ride
    message: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "metric": self.metric,
            "operator": self.operator,
            "threshold": self.threshold,
            "actual_value": round(self.actual_value, 2),
            "timestamp_s": round(self.timestamp_s, 1),
            "message": self.message,
        }


@dataclass
class AlertEvaluation:
    """Result of evaluating all alert rules against a ride."""
    events: list[AlertEvent] = field(default_factory=list)
    rules_evaluated: int = 0
    rules_triggered: int = 0

    def to_dict(self) -> dict:
        return {
            "events": [e.to_dict() for e in self.events],
            "rules_evaluated": self.rules_evaluated,
            "rules_triggered": self.rules_triggered,
        }


class AlertEngine:
    """Engine for evaluating custom alert rules against ride data."""

    def __init__(self, rules: list[AlertRule] | None = None):
        self.rules = rules or []
        self._streak_counters: dict[str, int] = {}  # rule_id -> consecutive seconds
        self._triggered_ids: set[str] = set()  # Already triggered this ride

    def _check_condition(self, metric_val: float, operator: str,
                         value: float, value2: Optional[float] = None) -> bool:
        """Check if a metric value meets the alert condition."""
        if operator == ">":
            return metric_val > value
        elif operator == "<":
            return metric_val < value
        elif operator == ">=":
            return metric_val >= value
        elif operator == "<=":
            return metric_val <= value
        elif operator == "==":
            return abs(metric_val - value) < 0.01
        elif operator == "!=":
            return abs(metric_val - value) >= 0.01
        elif operator == "between" and value2 is not None:
            lo, hi = min(value, value2), max(value, value2)
            return lo <= metric_val <= hi
        return False

    def evaluate_snapshot(self, metrics: dict, timestamp_s: float) -> list[AlertEvent]:
        """Evaluate all rules against a single point-in-time metrics snapshot.

        Args:
            metrics:     Dict of metric_name -> value at this moment.
            timestamp_s: Seconds elapsed in the ride.

        Returns:
            List of AlertEvent for any rules that fired.
        """
        events = []
        for rule in self.rules:
            if not rule.enabled:
                continue
            self.rules_evaluated_count = getattr(self, '_eval_count', 0) + 1

            metric_val = metrics.get(rule.metric)
            if metric_val is None:
                continue

            try:
                metric_val = float(metric_val)
            except (TypeError, ValueError):
                continue

            condition_met = self._check_condition(
                metric_val, rule.operator, rule.value, rule.value2)

            if condition_met:
                self._streak_counters[rule.id] = self._streak_counters.get(rule.id, 0) + 1
                if self._streak_counters[rule.id] >= rule.streak_seconds:
                    if rule.id not in self._triggered_ids:
                        event = AlertEvent(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            metric=rule.metric,
                            operator=rule.operator,
                            threshold=rule.value,
                            actual_value=metric_val,
                            timestamp_s=timestamp_s,
                            message=f"Alert '{rule.name}': {rule.metric} = {metric_val:.1f} {rule.operator} {rule.value}",
                        )
                        events.append(event)
                        self._triggered_ids.add(rule.id)
            else:
                self._streak_counters[rule.id] = 0

        return events

    def evaluate_ride(self, ride_stream: list[dict],
                      time_step_s: float = 1.0) -> AlertEvaluation:
        """Evaluate all rules against a full ride data stream.

        Args:
            ride_stream:  List of metric snapshots (one per time_step_s).
            time_step_s:  Time between snapshots (seconds).

        Returns:
            AlertEvaluation with all triggered events.
        """
        self._streak_counters = {}
        self._triggered_ids = set()
        all_events = []

        for i, snapshot in enumerate(ride_stream):
            t = i * time_step_s
            events = self.evaluate_snapshot(snapshot, t)
            all_events.extend(events)

        return AlertEvaluation(
            events=all_events,
            rules_evaluated=len([r for r in self.rules if r.enabled]),
            rules_triggered=len(self._triggered_ids),
        )

    def reset(self):
        """Reset streak counters for a new ride."""
        self._streak_counters = {}
        self._triggered_ids = set()


# ══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════

def _alerts_file(profile_dir: Path) -> Path:
    return profile_dir / "custom_alerts.json"


def save_rules(rules: list[AlertRule], profile_dir: Path) -> None:
    """Persist alert rules to disk."""
    data = [r.to_dict() for r in rules]
    _alerts_file(profile_dir).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_rules(profile_dir: Path) -> list[AlertRule]:
    """Load alert rules from disk."""
    path = _alerts_file(profile_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [
            AlertRule(
                id=r["id"], name=r["name"], metric=r["metric"],
                operator=r["operator"], value=r["value"],
                value2=r.get("value2"), streak_seconds=r.get("streak_seconds", 0),
                enabled=r.get("enabled", True),
                created_at=r.get("created_at", ""),
            )
            for r in data
        ]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def create_rule(name: str, metric: str, operator: str, value: float,
                value2: Optional[float] = None,
                streak_seconds: int = 0) -> AlertRule:
    """Create a new alert rule with auto-generated ID."""
    rule_id = f"alert_{int(time.time() * 1000)}"
    return AlertRule(
        id=rule_id,
        name=name,
        metric=metric,
        operator=operator,
        value=value,
        value2=value2,
        streak_seconds=streak_seconds,
        enabled=True,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
