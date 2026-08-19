"""v0.9.0 — Training Phase Detection (Ride Cave-style).

Automatically detects structured training phases from weekly volume and
intensity patterns. Identifies Base, Build, Peak, Recovery, and Taper phases.

References:
  - Ride Cave Data Lab: "Training Distribution" module with automatic
    phase detection from volume and intensity patterns.
  - Coggan/Allen: "Training and Racing with a Power Meter" — periodisation.
  - Seiler: "Four Quadrants of Training" — intensity distribution.
  - Lydiard: periodisation model — base → build → peak → taper.

Algorithm:
  1. Aggregate weekly TSS, volume (hours), and average IF.
  2. Compute 3-week rolling averages for each metric.
  3. Detect phase transitions based on:
     - Base:     high volume, low IF, stable/increasing
     - Build:    increasing volume + increasing IF
     - Peak:     highest IF, moderate volume, short duration
     - Recovery: sharp volume drop (>30%), low IF
     - Taper:    volume decreases, IF maintained or increased
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math


# Phase definitions with typical ranges
PHASE_DEFINITIONS = {
    "base": {
        "label": "Base",
        "description": "Aerobic development phase — high volume, low-moderate intensity.",
        "color": "#4CAF50",
        "typical_weeks": "4-12",
        "typical_volume_pct": "80-100% of peak",
        "typical_if_range": "0.55-0.72",
    },
    "build": {
        "label": "Build",
        "description": "Intensity build — increasing threshold and VO2max work.",
        "color": "#FF9800",
        "typical_weeks": "3-6",
        "typical_volume_pct": "70-100% of peak",
        "typical_if_range": "0.70-0.82",
    },
    "peak": {
        "label": "Peak",
        "description": "Race-specific sharpening — highest intensity, reduced volume.",
        "color": "#F44336",
        "typical_weeks": "1-3",
        "typical_volume_pct": "50-80% of peak",
        "typical_if_range": "0.78-0.90",
    },
    "recovery": {
        "label": "Recovery",
        "description": "Recovery / adaptation block — sharp volume reduction.",
        "color": "#9C27B0",
        "typical_weeks": "1-2",
        "typical_volume_pct": "30-60% of peak",
        "typical_if_range": "0.50-0.68",
    },
    "taper": {
        "label": "Taper",
        "description": "Pre-competition taper — volume drops, intensity maintained.",
        "color": "#2196F3",
        "typical_weeks": "1-3",
        "typical_volume_pct": "40-70% of peak",
        "typical_if_range": "0.70-0.85",
    },
    "transition": {
        "label": "Transition",
        "description": "Off-season / active rest — low volume and intensity.",
        "color": "#607D8B",
        "typical_weeks": "2-6",
        "typical_volume_pct": "20-50% of peak",
        "typical_if_range": "0.45-0.65",
    },
}


@dataclass
class WeeklyData:
    """Aggregated training data for a single week."""
    week_start: str       # ISO date of Monday
    tss: float            # Total Training Stress Score
    hours: float          # Total training hours
    if_avg: float         # Average Intensity Factor
    ride_count: int       # Number of rides
    tss_per_hour: float   # TSS/hour (training density)

    def to_dict(self) -> dict:
        return {
            "week": self.week_start,
            "tss": round(self.tss, 0),
            "hours": round(self.hours, 1),
            "if_avg": round(self.if_avg, 3),
            "ride_count": self.ride_count,
            "tss_per_hour": round(self.tss_per_hour, 1),
        }


@dataclass
class PhaseSegment:
    """A detected training phase segment."""
    phase: str                # "base", "build", "peak", "recovery", "taper", "transition"
    phase_label: str
    description: str
    color: str
    start_week: str           # ISO date
    end_week: str             # ISO date
    n_weeks: int
    avg_tss: float
    avg_hours: float
    avg_if: float
    avg_tss_per_hour: float
    volume_trend: str         # "increasing", "stable", "decreasing"
    intensity_trend: str      # "increasing", "stable", "decreasing"
    confidence: float         # 0-100

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "label": self.phase_label,
            "description": self.description,
            "color": self.color,
            "start_week": self.start_week,
            "end_week": self.end_week,
            "n_weeks": self.n_weeks,
            "avg_tss": round(self.avg_tss, 0),
            "avg_hours": round(self.avg_hours, 1),
            "avg_if": round(self.avg_if, 3),
            "avg_tss_per_hour": round(self.avg_tss_per_hour, 1),
            "volume_trend": self.volume_trend,
            "intensity_trend": self.intensity_trend,
            "confidence": round(self.confidence, 1),
        }


@dataclass
class PhaseDetectionResult:
    """Complete training phase detection result."""
    current_phase: str
    current_phase_label: str
    phases: list[PhaseSegment]
    weekly_data: list[WeeklyData]
    summary: str

    def to_dict(self) -> dict:
        return {
            "current_phase": self.current_phase,
            "current_phase_label": self.current_phase_label,
            "phases": [p.to_dict() for p in self.phases],
            "weekly_data": [w.to_dict() for w in self.weekly_data],
            "summary": self.summary,
        }


def _rolling_average(values: list[float], window: int = 3) -> list[Optional[float]]:
    """Compute rolling average with the given window size."""
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        subset = values[start:i + 1]
        result.append(sum(subset) / len(subset) if subset else None)
    return result


def _trend(values: list[float]) -> str:
    """Determine if values are increasing, stable, or decreasing."""
    if len(values) < 2:
        return "stable"
    recent = values[-3:] if len(values) >= 3 else values
    if len(recent) < 2:
        return "stable"
    first_half = sum(recent[:len(recent) // 2]) / max(1, len(recent) // 2)
    second_half = sum(recent[len(recent) // 2:]) / max(1, len(recent) - len(recent) // 2)
    diff_pct = 100.0 * (second_half - first_half) / max(first_half, 1.0)
    if diff_pct > 10:
        return "increasing"
    elif diff_pct < -10:
        return "decreasing"
    return "stable"


def _classify_phase(avg_tss: float, avg_hours: float, avg_if: float,
                    volume_trend: str, intensity_trend: str,
                    tss_percentile: float, if_percentile: float) -> tuple[str, float]:
    """Classify a week-block into a training phase with confidence."""
    # Normalize IF to typical cycling ranges
    # Typical: base 0.55-0.72, build 0.70-0.82, peak 0.78-0.90

    # Recovery: sharp volume drop
    if volume_trend == "decreasing" and tss_percentile < 40:
        return "recovery", 75.0

    # Taper: volume decreasing but IF maintained/increasing
    if volume_trend == "decreasing" and intensity_trend in ("stable", "increasing") and if_percentile > 50:
        return "taper", 70.0

    # Transition: very low volume and intensity
    if tss_percentile < 25 and if_percentile < 35:
        return "transition", 80.0

    # Peak: highest IF, moderate volume
    if if_percentile > 80 and tss_percentile < 75:
        return "peak", 85.0

    # Build: increasing intensity with decent volume
    if intensity_trend in ("increasing", "stable") and if_percentile > 55 and tss_percentile > 40:
        return "build", 75.0

    # Base: high volume, low-moderate IF
    if tss_percentile > 50 and if_percentile < 60:
        return "base", 70.0

    # Default: if volume is increasing, it's base; if IF is high, it's build
    if volume_trend == "increasing":
        return "base", 60.0
    if intensity_trend == "increasing":
        return "build", 60.0

    return "base", 50.0


def detect_training_phases(weekly_summaries: list[dict]) -> PhaseDetectionResult:
    """Detect training phases from weekly summary data.

    Args:
        weekly_summaries: List of dicts with keys:
            week_start (str): ISO date of Monday
            tss (float): Total TSS for the week
            hours (float): Total training hours
            if_avg (float): Average intensity factor
            ride_count (int): Number of rides

    Returns:
        PhaseDetectionResult with detected phases and weekly data.
    """
    if not weekly_summaries:
        return PhaseDetectionResult(
            current_phase="unknown",
            current_phase_label="Unknown",
            phases=[],
            weekly_data=[],
            summary="No training data available for phase detection.",
        )

    # Sort by week
    sorted_weeks = sorted(weekly_summaries, key=lambda w: w.get("week_start", ""))

    # Build weekly data
    weekly_data = []
    for ws in sorted_weeks:
        tss = float(ws.get("tss", 0))
        hours = float(ws.get("hours", 0))
        if_avg = float(ws.get("if_avg", 0))
        ride_count = int(ws.get("ride_count", 0))
        tss_per_hour = tss / max(hours, 0.1)
        weekly_data.append(WeeklyData(
            week_start=ws.get("week_start", ""),
            tss=tss, hours=hours, if_avg=if_avg,
            ride_count=ride_count, tss_per_hour=tss_per_hour,
        ))

    # Compute rolling averages
    tss_values = [w.tss for w in weekly_data]
    hours_values = [w.hours for w in weekly_data]
    if_values = [w.if_avg for w in weekly_data]

    tss_rolling = _rolling_average(tss_values, 3)
    hours_rolling = _rolling_average(hours_values, 3)
    if_rolling = _rolling_average(if_values, 3)

    # Percentiles for classification
    tss_sorted = sorted(tss_values)
    if_sorted = sorted(if_values)

    def _percentile(val: float, sorted_vals: list[float]) -> float:
        if not sorted_vals:
            return 50.0
        for i, v in enumerate(sorted_vals):
            if val <= v:
                return 100.0 * i / len(sorted_vals)
        return 100.0

    # Detect phases — group consecutive weeks with the same phase
    phases: list[PhaseSegment] = []
    current_phase = None
    phase_start_idx = 0

    for i in range(len(weekly_data)):
        vol_trend = _trend(hours_values[max(0, i - 3):i + 1])
        int_trend = _trend(if_values[max(0, i - 3):i + 1])
        tss_pct = _percentile(tss_rolling[i] or tss_values[i], tss_sorted)
        if_pct = _percentile(if_rolling[i] or if_values[i], if_sorted)

        phase, confidence = _classify_phase(
            tss_rolling[i] or tss_values[i],
            hours_rolling[i] or hours_values[i],
            if_rolling[i] or if_values[i],
            vol_trend, int_trend, tss_pct, if_pct,
        )

        if phase != current_phase:
            # Close previous phase
            if current_phase is not None and phase_start_idx < i:
                seg_weeks = weekly_data[phase_start_idx:i]
                if seg_weeks:
                    pheno_def = PHASE_DEFINITIONS.get(current_phase, PHASE_DEFINITIONS["base"])
                    phases.append(PhaseSegment(
                        phase=current_phase,
                        phase_label=pheno_def["label"],
                        description=pheno_def["description"],
                        color=pheno_def["color"],
                        start_week=seg_weeks[0].week_start,
                        end_week=seg_weeks[-1].week_start,
                        n_weeks=len(seg_weeks),
                        avg_tss=sum(w.tss for w in seg_weeks) / len(seg_weeks),
                        avg_hours=sum(w.hours for w in seg_weeks) / len(seg_weeks),
                        avg_if=sum(w.if_avg for w in seg_weeks) / len(seg_weeks),
                        avg_tss_per_hour=sum(w.tss_per_hour for w in seg_weeks) / len(seg_weeks),
                        volume_trend=_trend([w.hours for w in seg_weeks]),
                        intensity_trend=_trend([w.if_avg for w in seg_weeks]),
                        confidence=confidence,
                    ))
            current_phase = phase
            phase_start_idx = i

    # Close final phase
    if current_phase is not None and phase_start_idx < len(weekly_data):
        seg_weeks = weekly_data[phase_start_idx:]
        if seg_weeks:
            pheno_def = PHASE_DEFINITIONS.get(current_phase, PHASE_DEFINITIONS["base"])
            # Use last week's trends for final segment
            vol_trend = _trend([w.hours for w in seg_weeks])
            int_trend = _trend([w.if_avg for w in seg_weeks])
            tss_pct = _percentile(seg_weeks[-1].tss, tss_sorted)
            if_pct = _percentile(seg_weeks[-1].if_avg, if_sorted)
            _, confidence = _classify_phase(
                seg_weeks[-1].tss, seg_weeks[-1].hours, seg_weeks[-1].if_avg,
                vol_trend, int_trend, tss_pct, if_pct,
            )
            phases.append(PhaseSegment(
                phase=current_phase,
                phase_label=pheno_def["label"],
                description=pheno_def["description"],
                color=pheno_def["color"],
                start_week=seg_weeks[0].week_start,
                end_week=seg_weeks[-1].week_start,
                n_weeks=len(seg_weeks),
                avg_tss=sum(w.tss for w in seg_weeks) / len(seg_weeks),
                avg_hours=sum(w.hours for w in seg_weeks) / len(seg_weeks),
                avg_if=sum(w.if_avg for w in seg_weeks) / len(seg_weeks),
                avg_tss_per_hour=sum(w.tss_per_hour for w in seg_weeks) / len(seg_weeks),
                volume_trend=vol_trend,
                intensity_trend=int_trend,
                confidence=confidence,
            ))

    # Current phase = last detected
    current = phases[-1].phase if phases else "unknown"
    current_label = phases[-1].phase_label if phases else "Unknown"

    # Summary
    phase_counts = {}
    for p in phases:
        phase_counts[p.phase] = phase_counts.get(p.phase, 0) + p.n_weeks
    summary_parts = []
    for phase_key in ["base", "build", "peak", "recovery", "taper", "transition"]:
        if phase_key in phase_counts:
            label = PHASE_DEFINITIONS[phase_key]["label"]
            summary_parts.append(f"{label}: {phase_counts[phase_key]} weeks")
    summary = f"Current: {current_label}. Detected: {', '.join(summary_parts)}." if summary_parts else "No clear phase pattern detected."

    return PhaseDetectionResult(
        current_phase=current,
        current_phase_label=current_label,
        phases=phases,
        weekly_data=weekly_data,
        summary=summary,
    )
