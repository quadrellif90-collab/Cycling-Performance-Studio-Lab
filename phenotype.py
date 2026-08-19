"""v0.9.0 — Athlete Phenotype Classification & Radar Chart.

Classifies riders into phenotypes based on their power-duration curve shape
and generates radar chart data for visual profiling.

References:
  - Coggan AP. "Phenotypes in WKO" (wko5.com/phenotypes).
  - Coggan AP. "Power Duration Model V2 — WKO5."
  - Leo et al. (2021). "Power Profiling in Cycling." Eur J Appl Physiol.
  - Ride Cave Data Lab: phenotype radar across sprint/anaerobic/VO2max/threshold/endurance.

Phenotype axes (5 dimensions for the radar chart):
  1. Sprint (neuromuscular power) — 5-15s normalized to elite
  2. Anaerobic — 1-2 min normalized to elite
  3. VO2max — 3-8 min normalized to elite
  4. Threshold — 20-30 min normalized to elite
  5. Endurance — 60+ min normalized to elite

Phenotype classes:
  - Sprinter:       high sprint + anaerobic, moderate VO2max, low endurance
  - Pursuiter:      high anaerobic + VO2max, moderate sprint/threshold
  - All-Rounder:    balanced across all axes
  - Time Trialist:  high threshold + endurance, moderate others
  - Climber:        high VO2max + threshold, high W/kg, moderate sprint
  - Rouleur:        high endurance + threshold, moderate sprint (flat specialist)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math


# ══════════════════════════════════════════════════════════════════════════════
# ELITE BENCHMARKS (W/kg) for each axis anchor duration
# Sources: Leo et al. 2021, Coggan WKO5, power-profiling literature
# ══════════════════════════════════════════════════════════════════════════════

AXIS_ANCHORS: dict[str, dict] = {
    "sprint": {
        "label": "Sprint (NM Power)",
        "duration_s": 15,
        "elite_wkg": 13.5,       # ~15s peak W/kg (elite male)
        "untrained_wkg": 5.0,
    },
    "anaerobic": {
        "label": "Anaerobic Capacity",
        "duration_s": 120,        # 2 min
        "elite_wkg": 8.2,
        "untrained_wkg": 3.5,
    },
    "vo2max": {
        "label": "VO2max Power",
        "duration_s": 300,        # 5 min
        "elite_wkg": 6.5,
        "untrained_wkg": 2.8,
    },
    "threshold": {
        "label": "Threshold Power",
        "duration_s": 1200,       # 20 min
        "elite_wkg": 5.3,
        "untrained_wkg": 2.2,
    },
    "endurance": {
        "label": "Endurance Power",
        "duration_s": 3600,       # 60 min
        "elite_wkg": 4.8,
        "untrained_wkg": 1.8,
    },
}

AXIS_KEYS = ["sprint", "anaerobic", "vo2max", "threshold", "endurance"]

# ══════════════════════════════════════════════════════════════════════════════
# PHENOTYPE DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

# Each phenotype is defined by a canonical axis profile (0-100 scale).
# Classification = closest canonical profile (Euclidean distance).
PHENOTYPE_PROFILES: dict[str, dict] = {
    "sprinter": {
        "label": "Sprinter",
        "description": "Explosive neuromuscular power. Excels in short sprints and criterium finishes.",
        "axes": {"sprint": 95, "anaerobic": 85, "vo2max": 60, "threshold": 45, "endurance": 35},
    },
    "pursuiter": {
        "label": "Pursuiter",
        "description": "Strong anaerobic + VO2max. Dominates pursuits and short time trials.",
        "axes": {"sprint": 65, "anaerobic": 90, "vo2max": 85, "threshold": 70, "endurance": 50},
    },
    "all_rounder": {
        "label": "All-Rounder",
        "description": "Balanced power profile. Competitive across a range of efforts and terrain.",
        "axes": {"sprint": 70, "anaerobic": 70, "vo2max": 70, "threshold": 70, "endurance": 70},
    },
    "time_trialist": {
        "label": "Time Trialist",
        "description": "Sustained threshold + endurance power. Excels in TT and long efforts.",
        "axes": {"sprint": 40, "anaerobic": 50, "vo2max": 65, "threshold": 90, "endurance": 90},
    },
    "climber": {
        "label": "Climber",
        "description": "High W/kg at VO2max and threshold. Excels on steep climbs.",
        "axes": {"sprint": 50, "anaerobic": 65, "vo2max": 90, "threshold": 88, "endurance": 60},
    },
    "rouleur": {
        "label": "Rouleur",
        "description": "Strong endurance and threshold. Dominates flat terrain and long breakaways.",
        "axes": {"sprint": 55, "anaerobic": 55, "vo2max": 65, "threshold": 80, "endurance": 90},
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RadarPoint:
    """A single axis on the radar chart."""
    axis_key: str
    axis_label: str
    normalized_score: float    # 0-100 scale
    actual_wkg: Optional[float] = None
    elite_wkg: Optional[float] = None
    duration_s: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "axis": self.axis_key,
            "label": self.axis_label,
            "score": round(self.normalized_score, 1),
            "wkg": round(self.actual_wkg, 2) if self.actual_wkg else None,
            "elite_wkg": self.elite_wkg,
            "duration_s": self.duration_s,
        }


@dataclass
class PhenotypeResult:
    """Complete phenotype classification result."""
    phenotype: str                # e.g. "climber"
    phenotype_label: str          # e.g. "Climber"
    description: str
    confidence: float             # 0-1 distance-based confidence
    radar_points: list[RadarPoint] = field(default_factory=list)
    radar_scores: dict[str, float] = field(default_factory=dict)  # {axis: 0-100}
    closest_distance: float = 0.0
    second_closest: str = ""
    second_distance: float = 0.0

    def to_dict(self) -> dict:
        return {
            "phenotype": self.phenotype,
            "label": self.phenotype_label,
            "description": self.description,
            "confidence": round(self.confidence, 1),
            "radar": [p.to_dict() for p in self.radar_points],
            "radar_scores": {k: round(v, 1) for k, v in self.radar_scores.items()},
            "closest_distance": round(self.closest_distance, 2),
            "second_closest": self.second_closest,
            "second_distance": round(self.second_distance, 2),
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def _compute_axis_score(watts: float, weight_kg: float,
                        axis_key: str) -> float:
    """Convert raw watts at the axis anchor duration to a 0-100 normalized score."""
    if weight_kg <= 0:
        return 0.0
    anchor = AXIS_ANCHORS[axis_key]
    wkg = watts / weight_kg
    elite = anchor["elite_wkg"]
    untrained = anchor["untrained_wkg"]
    if elite <= untrained:
        return 0.0
    # Linear interpolation: untrained=0, elite=100
    score = 100.0 * (wkg - untrained) / (elite - untrained)
    return max(0.0, min(100.0, score))


def _compute_radar_scores(best_efforts: dict[int, int],
                          weight_kg: float) -> dict[str, float]:
    """Compute the 5-axis radar scores from the best-effort curve."""
    scores: dict[str, float] = {}
    for axis_key in AXIS_KEYS:
        anchor = AXIS_ANCHORS[axis_key]
        dur = anchor["duration_s"]
        watts = best_efforts.get(dur)
        if watts and watts > 0:
            scores[axis_key] = _compute_axis_score(float(watts), weight_kg, axis_key)
        else:
            # Try nearest available duration
            available = sorted(best_efforts.keys())
            nearest = min(available, key=lambda d: abs(d - dur)) if available else None
            if nearest and best_efforts.get(nearest, 0) > 0:
                scores[axis_key] = _compute_axis_score(
                    float(best_efforts[nearest]), weight_kg, axis_key)
            else:
                scores[axis_key] = 0.0
    return scores


def _phenotype_distance(scores: dict[str, float],
                        profile: dict[str, float]) -> float:
    """Euclidean distance between athlete scores and a phenotype profile."""
    dist_sq = 0.0
    for axis in AXIS_KEYS:
        diff = scores.get(axis, 0) - profile.get(axis, 0)
        dist_sq += diff * diff
    return math.sqrt(dist_sq)


def classify_phenotype(best_efforts: dict[int, int],
                       weight_kg: float) -> Optional[PhenotypeResult]:
    """Classify athlete phenotype from best-effort power-duration curve.

    Args:
        best_efforts: {duration_s: watts} mean-max best efforts.
        weight_kg:   Rider body mass (kg).

    Returns:
        PhenotypeResult or None if insufficient data.
    """
    if not best_efforts or weight_kg <= 0:
        return None

    # Compute radar scores
    scores = _compute_radar_scores(best_efforts, weight_kg)

    # Check if we have enough data (at least 3 axes with non-zero scores)
    non_zero = sum(1 for v in scores.values() if v > 0)
    if non_zero < 3:
        return None

    # Find closest phenotype
    distances: list[tuple[str, float]] = []
    for pheno_key, pheno_def in PHENOTYPE_PROFILES.items():
        dist = _phenotype_distance(scores, pheno_def["axes"])
        distances.append((pheno_key, dist))

    distances.sort(key=lambda x: x[1])
    best_pheno, best_dist = distances[0]
    second_pheno, second_dist = distances[1] if len(distances) > 1 else ("", 0.0)

    # Confidence: based on distance gap between best and second
    # If gap is large, confidence is high. Typical range: 50-95%
    max_possible_dist = math.sqrt(5 * (100 ** 2))  # theoretical max
    gap = second_dist - best_dist
    # Confidence formula: base 50% + up to 45% from the gap
    confidence = 50.0 + 45.0 * min(1.0, gap / (max_possible_dist * 0.3))

    # Build radar points
    radar_points = []
    for axis_key in AXIS_KEYS:
        anchor = AXIS_ANCHORS[axis_key]
        dur = anchor["duration_s"]
        watts = best_efforts.get(dur)
        if not watts:
            available = sorted(best_efforts.keys())
            nearest = min(available, key=lambda d: abs(d - dur)) if available else None
            watts = best_efforts.get(nearest) if nearest else None
        wkg = float(watts) / weight_kg if watts and weight_kg > 0 else None
        radar_points.append(RadarPoint(
            axis_key=axis_key,
            axis_label=anchor["label"],
            normalized_score=scores[axis_key],
            actual_wkg=round(wkg, 2) if wkg else None,
            elite_wkg=anchor["elite_wkg"],
            duration_s=anchor["duration_s"],
        ))

    pheno_def = PHENOTYPE_PROFILES[best_pheno]

    return PhenotypeResult(
        phenotype=best_pheno,
        phenotype_label=pheno_def["label"],
        description=pheno_def["description"],
        confidence=round(confidence, 1),
        radar_points=radar_points,
        radar_scores=scores,
        closest_distance=round(best_dist, 2),
        second_closest=second_pheno,
        second_distance=round(second_dist, 2),
    )


def get_radar_chart_data(best_efforts: dict[int, int],
                         weight_kg: float) -> Optional[dict]:
    """Get radar chart data in a format suitable for frontend rendering.

    Returns a dict with:
      - axes: list of axis labels
      - scores: list of normalized scores (0-100)
      - athlete_wkg: list of actual W/kg values
      - elite_wkg: list of elite benchmark W/kg
      - phenotype: classified phenotype info
    """
    result = classify_phenotype(best_efforts, weight_kg)
    if result is None:
        return None

    return {
        "axes": [p.axis_label for p in result.radar_points],
        "scores": [round(p.normalized_score, 1) for p in result.radar_points],
        "athlete_wkg": [round(p.actual_wkg, 2) if p.actual_wkg else 0 for p in result.radar_points],
        "elite_wkg": [p.elite_wkg for p in result.radar_points],
        "phenotype": result.to_dict(),
    }
