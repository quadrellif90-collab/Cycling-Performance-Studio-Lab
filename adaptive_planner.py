"""v0.9.0 — Enhanced Adaptive Training Planner (AI-driven).

Goes beyond the basic training_planner.py by adding:
  - Automatic plan adjustment based on readiness signals (HRV, sleep, TSB)
  - Multi-method plan generation (polarized, threshold, pyramidal, IF-based)
  - Plan recommendations based on current phase and goals
  - Weekly load distribution optimization

References:
  - TrainerRoad Adaptive Training: "AI-driven progression"
  - Xert Adaptive Training Advisor: goal-based workout recommendations
  - Ride Cave Auto Train: "adaptive plans that reshape themselves"
  - Seiler: "4-Zone model" for intensity distribution
  - Coggan: "Training Zones" and periodisation

Note: This module enhances training_planner.py — it does NOT replace it.
It provides higher-level recommendations that training_planner consumes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING METHODS (intensity distribution strategies)
# ══════════════════════════════════════════════════════════════════════════════

TRAINING_METHODS = {
    "polarized": {
        "label": "Polarized (80/20)",
        "description": "80% Z1-Z2, 5% Z3-Z4, 15% Z5+. Seiler model — maximize adaptations.",
        "z1z2_pct": 80, "z3z4_pct": 5, "z5plus_pct": 15,
        "best_for": ["general_fitness", "endurance", "fat_loss"],
        "caution": "Requires solid aerobic base. Not ideal for beginners.",
    },
    "pyramidal": {
        "label": "Pyramidal (70/20/10)",
        "description": "70% Z1-Z2, 20% Z3-Z4, 10% Z5+. Balanced approach.",
        "z1z2_pct": 70, "z3z4_pct": 20, "z5plus_pct": 10,
        "best_for": ["general_fitness", "time_trial", "gran_fondo"],
        "caution": "Good all-around. May limit top-end if over-used.",
    },
    "threshold": {
        "label": "Threshold Focus (60/30/10)",
        "description": "60% Z1-Z2, 30% Z3-Z4, 10% Z5+. FTP-focused.",
        "z1z2_pct": 60, "z3z4_pct": 30, "z5plus_pct": 10,
        "best_for": ["time_trial", "sustained_power", "ftp_improvement"],
        "caution": "High Z3-Z4 volume — monitor fatigue carefully.",
    },
    "hiit": {
        "label": "HIIT Focus (50/15/35)",
        "description": "50% Z1-Z2, 15% Z3-Z4, 35% Z5+. VO2max dominant.",
        "z1z2_pct": 50, "z3z4_pct": 15, "z5plus_pct": 35,
        "best_for": ["vo2max_improvement", "short_races", "crits"],
        "caution": "Very taxing. Limit to 2-3 weeks blocks with recovery.",
    },
    "sweet_spot": {
        "label": "Sweet Spot (65/25/10)",
        "description": "65% Z1-Z2, 25% Z3-Z4 (sweet spot heavy), 10% Z5+.",
        "z1z2_pct": 65, "z3z4_pct": 25, "z5plus_pct": 10,
        "best_for": ["ftp_improvement", "time_crunched", "base_to_build"],
        "caution": "Efficient but can accumulate fatigue. Watch monotony.",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# GOAL PROFILES
# ══════════════════════════════════════════════════════════════════════════════

GOAL_PROFILES = {
    "general_fitness": {
        "label": "General Fitness",
        "recommended_method": "polarized",
        "typical_weekly_tss": 300,
        "typical_weekly_hours": 6,
        "key_focus": ["aerobic_base", "consistency"],
    },
    "fat_loss": {
        "label": "Fat Loss / Weight Management",
        "recommended_method": "polarized",
        "typical_weekly_tss": 350,
        "typical_weekly_hours": 7,
        "key_focus": ["volume", "consistency", "recovery"],
    },
    "ftp_improvement": {
        "label": "FTP Improvement",
        "recommended_method": "sweet_spot",
        "typical_weekly_tss": 400,
        "typical_weekly_hours": 8,
        "key_focus": ["threshold_work", "progressive_overload"],
    },
    "vo2max_improvement": {
        "label": "VO2max Development",
        "recommended_method": "hiit",
        "typical_weekly_tss": 350,
        "typical_weekly_hours": 7,
        "key_focus": ["vo2max_intervals", "recovery"],
    },
    "endurance": {
        "label": "Endurance / Grand Fondo",
        "recommended_method": "pyramidal",
        "typical_weekly_tss": 500,
        "typical_weekly_hours": 10,
        "key_focus": ["volume", "long_rides", "fatigue_resistance"],
    },
    "time_trial": {
        "label": "Time Trial Specialist",
        "recommended_method": "threshold",
        "typical_weekly_tss": 450,
        "typical_weekly_hours": 9,
        "key_focus": ["sustained_power", "pacing", "aero"],
    },
    "crit_racing": {
        "label": "Criterium Racing",
        "recommended_method": "hiit",
        "typical_weekly_tss": 350,
        "typical_weekly_hours": 7,
        "key_focus": ["repeated_efforts", "sprint", "tactical"],
    },
    "stage_race": {
        "label": "Stage Race / Multi-Day",
        "recommended_method": "polarized",
        "typical_weekly_tss": 600,
        "typical_weekly_hours": 12,
        "key_focus": ["recovery", "consistency", "sustainability"],
    },
}


@dataclass
class WeeklyLoadRecommendation:
    """Recommended weekly load distribution."""
    method: str
    method_label: str
    target_weekly_tss: float
    target_weekly_hours: float
    z1z2_hours: float
    z3z4_hours: float
    z5plus_hours: float
    sessions_per_week: int
    key_sessions: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "method_label": self.method_label,
            "target_tss": round(self.target_weekly_tss, 0),
            "target_hours": round(self.target_weekly_hours, 1),
            "z1z2_hours": round(self.z1z2_hours, 1),
            "z3z4_hours": round(self.z3z4_hours, 1),
            "z5plus_hours": round(self.z5plus_hours, 1),
            "sessions_per_week": self.sessions_per_week,
            "key_sessions": self.key_sessions,
            "notes": self.notes,
        }


@dataclass
class AdaptiveRecommendation:
    """Complete adaptive training recommendation."""
    goal: str
    goal_label: str
    current_method: Optional[str]           # Detected current method
    recommended_method: str
    recommended_method_label: str
    weekly_load: WeeklyLoadRecommendation
    readiness_adjustment: float             # 0.8-1.2 multiplier based on readiness
    phase_adjustment: str                   # e.g. "increase_volume", "maintain", "reduce"
    confidence: float
    reasoning: list[str]

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "goal_label": self.goal_label,
            "current_method": self.current_method,
            "recommended_method": self.recommended_method,
            "recommended_method_label": self.recommended_method_label,
            "weekly_load": self.weekly_load.to_dict(),
            "readiness_adjustment": round(self.readiness_adjustment, 2),
            "phase_adjustment": self.phase_adjustment,
            "confidence": round(self.confidence, 1),
            "reasoning": self.reasoning,
        }


def _compute_readiness_adjustment(
    hrv_rmssd_pct: Optional[float] = None,
    sleep_score: Optional[float] = None,
    tsb: Optional[float] = None,
    recent_tss_avg: Optional[float] = None,
    monotony: Optional[float] = None,
) -> tuple[float, list[str]]:
    """Compute a readiness-based load adjustment multiplier (0.80 - 1.20).

    Returns (multiplier, list_of_reasons).
    """
    adjustment = 1.0
    reasons = []

    # HRV contribution (±10%)
    if hrv_rmssd_pct is not None:
        if hrv_rmssd_pct > 110:
            adjustment += 0.05
            reasons.append(f"HRV above baseline ({hrv_rmssd_pct:.0f}%) — ready for load.")
        elif hrv_rmssd_pct < 85:
            adjustment -= 0.05
            reasons.append(f"HRV suppressed ({hrv_rmssd_pct:.0f}%) — reduce load.")
        elif hrv_rmssd_pct < 70:
            adjustment -= 0.10
            reasons.append(f"HRV significantly suppressed ({hrv_rmssd_pct:.0f}%) — rest day recommended.")

    # Sleep contribution (±5%)
    if sleep_score is not None:
        if sleep_score > 85:
            adjustment += 0.03
            reasons.append(f"Excellent sleep ({sleep_score:.0f}/100) — recovery is strong.")
        elif sleep_score < 60:
            adjustment -= 0.05
            reasons.append(f"Poor sleep ({sleep_score:.0f}/100) — reduce intensity.")

    # TSB contribution (±10%)
    if tsb is not None:
        if tsb > 25:
            adjustment += 0.05
            reasons.append(f"TSB positive ({tsb:+.0f}) — form is good, push harder.")
        elif tsb < -30:
            adjustment -= 0.10
            reasons.append(f"TSB deeply negative ({tsb:+.0f}) — accumulated fatigue, recover.")
        elif tsb < -15:
            adjustment -= 0.05
            reasons.append(f"TSB negative ({tsb:+.0f}) — monitor fatigue.")

    # Monotony contribution (±5%)
    if monotony is not None:
        if monotony > 2.0:
            adjustment -= 0.05
            reasons.append(f"Training monotony high ({monotony:.1f}) — add variety.")

    # Clamp
    adjustment = max(0.80, min(1.20, adjustment))

    if not reasons:
        reasons.append("No readiness signals available — using default load.")

    return adjustment, reasons


def _detect_current_method(z1z2_pct: float, z3z4_pct: float,
                           z5plus_pct: float) -> Optional[str]:
    """Detect which training method the athlete is currently using."""
    best_match = None
    best_dist = float("inf")
    for method_key, method_def in TRAINING_METHODS.items():
        dist = math.sqrt(
            (z1z2_pct - method_def["z1z2_pct"]) ** 2 +
            (z3z4_pct - method_def["z3z4_pct"]) ** 2 +
            (z5plus_pct - method_def["z5plus_pct"]) ** 2
        )
        if dist < best_dist:
            best_dist = dist
            best_match = method_key
    return best_match if best_dist < 20 else None


def _build_weekly_load(method: str, base_tss: float, base_hours: float,
                       readiness_adj: float) -> WeeklyLoadRecommendation:
    """Build weekly load recommendation for the given method."""
    m = TRAINING_METHODS[method]
    adj_tss = base_tss * readiness_adj
    adj_hours = base_hours * readiness_adj

    z1z2_h = adj_hours * m["z1z2_pct"] / 100.0
    z3z4_h = adj_hours * m["z3z4_pct"] / 100.0
    z5plus_h = adj_hours * m["z5plus_pct"] / 100.0

    sessions = max(3, min(7, int(adj_hours / 1.5)))

    key_sessions = []
    if z5plus_h > 0.5:
        key_sessions.append({
            "type": "VO2max / Anaerobic",
            "hours": round(z5plus_h / max(1, sessions // 3), 1),
            "n_sessions": max(1, sessions // 3),
            "intensity": "Z5+ (106-120% FTP)",
        })
    if z3z4_h > 0.5:
        key_sessions.append({
            "type": "Threshold / Sweet Spot",
            "hours": round(z3z4_h / max(1, sessions // 3), 1),
            "n_sessions": max(1, sessions // 3),
            "intensity": "Z3-Z4 (76-105% FTP)",
        })
    key_sessions.append({
        "type": "Endurance / Recovery",
        "hours": round(z1z2_h / max(1, sessions - len(key_sessions)), 1),
        "n_sessions": max(1, sessions - len(key_sessions)),
        "intensity": "Z1-Z2 (56-75% FTP)",
    })

    return WeeklyLoadRecommendation(
        method=method,
        method_label=m["label"],
        target_weekly_tss=adj_tss,
        target_weekly_hours=adj_hours,
        z1z2_hours=z1z2_h,
        z3z4_hours=z3z4_h,
        z5plus_hours=z5plus_h,
        sessions_per_week=sessions,
        key_sessions=key_sessions,
        notes=[m["caution"]],
    )


def generate_adaptive_recommendation(
    goal: str,
    current_z1z2_pct: float = 80.0,
    current_z3z4_pct: float = 15.0,
    current_z5plus_pct: float = 5.0,
    current_phase: str = "base",
    hrv_rmssd_pct: Optional[float] = None,
    sleep_score: Optional[float] = None,
    tsb: Optional[float] = None,
    recent_tss_avg: Optional[float] = None,
    monotony: Optional[float] = None,
    current_weekly_tss: float = 300.0,
    current_weekly_hours: float = 6.0,
) -> AdaptiveRecommendation:
    """Generate an adaptive training recommendation.

    Args:
        goal:                Goal key (e.g. "ftp_improvement", "polarized").
        current_z1z2_pct:    Current Z1+Z2 time percentage.
        current_z3z4_pct:    Current Z3+Z4 time percentage.
        current_z5plus_pct:  Current Z5+ time percentage.
        current_phase:       Current training phase ("base", "build", "peak", etc).
        hrv_rmssd_pct:       HRV as % of personal baseline (100 = baseline).
        sleep_score:         Sleep quality score (0-100).
        tsb:                 Training Stress Balance (CTL - ATL).
        recent_tss_avg:      Average TSS over last 7 days.
        monotony:            Training monotony (weekly TSS / max daily TSS).
        current_weekly_tss:  Current weekly TSS.
        current_weekly_hours: Current weekly training hours.

    Returns:
        AdaptiveRecommendation with full analysis.
    """
    goal_profile = GOAL_PROFILES.get(goal, GOAL_PROFILES["general_fitness"])
    recommended_method = goal_profile["recommended_method"]
    method_def = TRAINING_METHODS[recommended_method]

    # Detect current method
    current_method = _detect_current_method(current_z1z2_pct, current_z3z4_pct, current_z5plus_pct)

    # Readiness adjustment
    readiness_adj, readiness_reasons = _compute_readiness_adjustment(
        hrv_rmssd_pct, sleep_score, tsb, recent_tss_avg, monotony)

    # Phase-based adjustment
    phase_reasons = []
    if current_phase == "base":
        phase_adj = "increase_volume"
        phase_reasons.append("Base phase: focus on volume and consistency.")
    elif current_phase == "build":
        phase_adj = "increase_intensity"
        phase_reasons.append("Build phase: progressively increase intensity.")
    elif current_phase == "peak":
        phase_adj = "reduce_volume_maintain_intensity"
        phase_reasons.append("Peak phase: reduce volume, maintain race intensity.")
    elif current_phase == "recovery":
        phase_adj = "reduce_all"
        phase_reasons.append("Recovery phase: active rest, reduce load significantly.")
    elif current_phase == "taper":
        phase_adj = "taper"
        phase_reasons.append("Taper phase: reduce volume 40-60%, maintain intensity.")
    else:
        phase_adj = "maintain"
        phase_reasons.append("Unknown phase: maintain current approach.")

    # Build weekly load
    target_tss = goal_profile["typical_weekly_tss"]
    target_hours = goal_profile["typical_weekly_hours"]

    # Adjust targets based on phase
    if current_phase == "recovery":
        target_tss *= 0.5
        target_hours *= 0.5
    elif current_phase == "taper":
        target_tss *= 0.6
        target_hours *= 0.6
    elif current_phase == "peak":
        target_tss *= 0.8
        target_hours *= 0.8

    weekly_load = _build_weekly_load(recommended_method, target_tss, target_hours, readiness_adj)

    # Confidence
    confidence = 70.0
    if hrv_rmssd_pct is not None:
        confidence += 5
    if sleep_score is not None:
        confidence += 5
    if current_method is not None:
        confidence += 5
    confidence = min(95, confidence)

    # Reasoning
    reasoning = []
    reasoning.append(f"Goal: {goal_profile['label']} → recommended method: {method_def['label']}.")
    if current_method and current_method != recommended_method:
        reasoning.append(f"Currently using {TRAINING_METHODS[current_method]['label']} — "
                         f"shifting to {method_def['label']}.")
    elif current_method == recommended_method:
        reasoning.append(f"Already using {method_def['label']} — maintain and refine.")
    reasoning.extend(readiness_reasons)
    reasoning.extend(phase_reasons)

    return AdaptiveRecommendation(
        goal=goal,
        goal_label=goal_profile["label"],
        current_method=current_method,
        recommended_method=recommended_method,
        recommended_method_label=method_def["label"],
        weekly_load=weekly_load,
        readiness_adjustment=readiness_adj,
        phase_adjustment=phase_adj,
        confidence=confidence,
        reasoning=reasoning,
    )
