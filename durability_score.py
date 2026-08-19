"""v0.9.0 — Durability Score (Xert-style).

Measures an athlete's ability to maintain high power outputs deep into
long rides (>3 hours). A higher durability score means less power fade
at duration — a key metric for endurance performance.

References:
  - Xert: "Durability Score" (baronbiosys.com/glossary/durability-score)
  - Xert Forum (Apr 2025): "Durability: The Hottest New Metric in Cycling"
  - Pinot & Grappe (2014): "The骑行 power profile and fatigue resistance"
  - Concept: compare peak power in the first 60 min vs peak power after
    120+ min of riding. The ratio (adjusted for duration) = durability.

Algorithm:
  1. Load all rides >2 hours with power streams.
  2. For each ride, find peak 5min, 20min power in:
     a. First 60 minutes (fresh legs)
     b. After 120+ minutes (fatigued legs)
  3. Durability = (fatigued_peak / fresh_peak) × 100, capped at 100.
  4. Average across rides for the overall durability score.
  5. Classify: >90% = excellent, 80-90% = good, 70-80% = average, <70% = needs work.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# Durability tiers
_DURABILITY_TIERS = [
    (95, "exceptional", "Exceptional durability — elite-level resistance to fatigue."),
    (90, "excellent", "Excellent durability — strong power maintenance on long rides."),
    (80, "good", "Good durability — solid endurance performance with moderate fade."),
    (70, "average", "Average durability — noticeable power fade on long rides."),
    (0, "developing", "Developing durability — significant fade; focus on long-ride training."),
]


@dataclass
class DurabilityResult:
    """Durability score result."""
    score: float                   # 0-100 durability percentage
    tier: str                      # "exceptional" / "excellent" / "good" / "average" / "developing"
    tier_label: str                # Human-readable tier
    description: str
    n_rides_analyzed: int          # Number of long rides used
    avg_fresh_5min_wkg: Optional[float] = None
    avg_tired_5min_wkg: Optional[float] = None
    avg_fresh_20min_wkg: Optional[float] = None
    avg_tired_20min_wkg: Optional[float] = None
    fade_5min_pct: Optional[float] = None       # % drop from fresh to tired (5min)
    fade_20min_pct: Optional[float] = None      # % drop from fresh to tired (20min)
    best_ride_date: str = ""       # Date of the ride with best durability
    best_ride_score: float = 0.0   # Score of the best individual ride
    by_ride: list[dict] = field(default_factory=list)  # Per-ride breakdown

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 1),
            "tier": self.tier,
            "tier_label": self.tier_label,
            "description": self.description,
            "n_rides_analyzed": self.n_rides_analyzed,
            "fresh_5min_wkg": round(self.avg_fresh_5min_wkg, 2) if self.avg_fresh_5min_wkg else None,
            "tired_5min_wkg": round(self.avg_tired_5min_wkg, 2) if self.avg_tired_5min_wkg else None,
            "fresh_20min_wkg": round(self.avg_fresh_20min_wkg, 2) if self.avg_fresh_20min_wkg else None,
            "tired_20min_wkg": round(self.avg_tired_20min_wkg, 2) if self.avg_tired_20min_wkg else None,
            "fade_5min_pct": round(self.fade_5min_pct, 1) if self.fade_5min_pct is not None else None,
            "fade_20min_pct": round(self.fade_20min_pct, 1) if self.fade_20min_pct is not None else None,
            "best_ride_date": self.best_ride_date,
            "best_ride_score": round(self.best_ride_score, 1),
            "by_ride": self.by_ride,
        }


def _peak_power_in_window(power_stream: list[int],
                          start_s: int, end_s: int,
                          window_s: int) -> Optional[float]:
    """Find peak mean power over a sliding window within a time range."""
    if not power_stream or start_s >= end_s:
        return None
    n = len(power_stream)
    actual_end = min(end_s, n)
    window_end = start_s + window_s
    if window_end > actual_end:
        return None

    # Sliding window mean
    best = 0.0
    wsum = sum(power_stream[start_s:start_s + window_s])
    best = wsum / window_s
    for i in range(start_s + 1, actual_end - window_s + 1):
        wsum += power_stream[i + window_s - 1] - power_stream[i - 1]
        mean_w = wsum / window_s
        if mean_w > best:
            best = mean_w
    return best if best > 0 else None


def compute_durability_score(rides: list[dict],
                             weight_kg: float = 70.0,
                             min_duration_s: int = 7200) -> DurabilityResult:
    """Compute durability score from ride history.

    Args:
        rides:          List of ride dicts with "power_stream", "duration_s",
                        "started_at" keys.
        weight_kg:      Rider body mass for W/kg calculations.
        min_duration_s: Minimum ride duration to qualify (default 2h).

    Returns:
        DurabilityResult with score and analysis.
    """
    if not rides or weight_kg <= 0:
        return DurabilityResult(
            score=0, tier="insufficient_data", tier_label="Insufficient Data",
            description="No ride data available for durability analysis.",
            n_rides_analyzed=0,
        )

    analyzed = []
    for ride in rides:
        duration = ride.get("duration_s", 0)
        if duration < min_duration_s:
            continue
        power_stream = ride.get("power_stream") or ride.get("streams", {}).get("watts") or []
        if not power_stream or len(power_stream) < 600:
            continue

        # Fresh peak: first 60 min (0-3600s)
        fresh_5min = _peak_power_in_window(power_stream, 0, 3600, 300)
        fresh_20min = _peak_power_in_window(power_stream, 0, 3600, 1200)

        # Tired peak: after 120 min (7200s+)
        tired_start = 7200
        tired_5min = _peak_power_in_window(power_stream, tired_start, len(power_stream), 300)
        tired_20min = _peak_power_in_window(power_stream, tired_start, len(power_stream), 1200)

        # Compute per-ride durability (average of available ratios)
        ratios = []
        if fresh_5min and tired_5min and fresh_5min > 0:
            ratios.append(tired_5min / fresh_5min)
        if fresh_20min and tired_20min and fresh_20min > 0:
            ratios.append(tired_20min / fresh_20min)

        if not ratios:
            continue

        ride_score = 100.0 * sum(ratios) / len(ratios)
        ride_date = ride.get("started_at", "")[:10]

        analyzed.append({
            "date": ride_date,
            "duration_min": round(duration / 60.0),
            "fresh_5min_w": fresh_5min,
            "tired_5min_w": tired_5min,
            "fresh_20min_w": fresh_20min,
            "tired_20min_w": tired_20min,
            "ratio_5min": round(tired_5min / fresh_5min, 3) if fresh_5min and tired_5min else None,
            "ratio_20min": round(tired_20min / fresh_20min, 3) if fresh_20min and tired_20min else None,
            "durability_score": round(ride_score, 1),
        })

    if not analyzed:
        return DurabilityResult(
            score=0, tier="insufficient_data", tier_label="Insufficient Data",
            description="No rides longer than 3 hours with power data found.",
            n_rides_analyzed=0,
        )

    # Overall score = mean of per-ride durability scores
    scores = [a["durability_score"] for a in analyzed]
    overall = sum(scores) / len(scores)

    # Best ride
    best_ride = max(analyzed, key=lambda a: a["durability_score"])

    # Averages
    fresh_5 = [a["fresh_5min_w"] for a in analyzed if a["fresh_5min_w"]]
    tired_5 = [a["tired_5min_w"] for a in analyzed if a["tired_5min_w"]]
    fresh_20 = [a["fresh_20min_w"] for a in analyzed if a["fresh_20min_w"]]
    tired_20 = [a["tired_20min_w"] for a in analyzed if a["tired_20min_w"]]

    avg_fresh_5 = sum(fresh_5) / len(fresh_5) if fresh_5 else None
    avg_tired_5 = sum(tired_5) / len(tired_5) if tired_5 else None
    avg_fresh_20 = sum(fresh_20) / len(fresh_20) if fresh_20 else None
    avg_tired_20 = sum(tired_20) / len(tired_20) if tired_20 else None

    fade_5 = None
    if avg_fresh_5 and avg_tired_5 and avg_fresh_5 > 0:
        fade_5 = 100.0 * (1.0 - avg_tired_5 / avg_fresh_5)
    fade_20 = None
    if avg_fresh_20 and avg_tired_20 and avg_fresh_20 > 0:
        fade_20 = 100.0 * (1.0 - avg_tired_20 / avg_fresh_20)

    # Tier classification
    tier = "developing"
    tier_label = "Developing"
    description = ""
    for threshold, t, desc in _DURABILITY_TIERS:
        if overall >= threshold:
            tier = t
            tier_label = t.capitalize()
            description = desc
            break

    return DurabilityResult(
        score=overall,
        tier=tier,
        tier_label=tier_label,
        description=description,
        n_rides_analyzed=len(analyzed),
        avg_fresh_5min_wkg=round(avg_fresh_5 / weight_kg, 2) if avg_fresh_5 else None,
        avg_tired_5min_wkg=round(avg_tired_5 / weight_kg, 2) if avg_tired_5 else None,
        avg_fresh_20min_wkg=round(avg_fresh_20 / weight_kg, 2) if avg_fresh_20 else None,
        avg_tired_20min_wkg=round(avg_tired_20 / weight_kg, 2) if avg_tired_20 else None,
        fade_5min_pct=round(fade_5, 1) if fade_5 is not None else None,
        fade_20min_pct=round(fade_20, 1) if fade_20 is not None else None,
        best_ride_date=best_ride["date"],
        best_ride_score=best_ride["durability_score"],
        by_ride=analyzed,
    )
