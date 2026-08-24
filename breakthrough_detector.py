"""v0.9.0 — Xert-style Breakthrough Detection.

Detects fitness breakthroughs by identifying activities where the athlete
exceeded their current Maximum Power Available (MPA) — meaning their
fitness signature (CP, W', Pmax) has improved.

References:
  - Baron Biosys / Xert: "Breakthrough Detection" (baronbiosys.com)
  - Xert Community Forum: "I just got a breakthrough. What happened?"
  - Concept: when power exceeds MPA during an activity, it indicates
    the athlete's fitness signature is now higher than previously estimated.

Algorithm:
  1. Load current fitness signature (CP, W', Pmax from power_duration_model).
  2. For each ride with power streams, compute MPA at every second.
  3. MPA(t) = Pmax if t <= 0, else CP + W' / (t_elapsed_above_cp + tau)
  4. If any power second exceeds MPA → breakthrough detected.
  5. Compute the new estimated signature from the breakthrough data.
  6. Score the breakthrough magnitude (minor / major / epic).

This is a simplified version of Xert's proprietary algorithm, adapted for
the open-source CPSL context.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BreakthroughResult:
    """Result of breakthrough detection for a single activity."""
    is_breakthrough: bool
    breakthrough_type: str         # "none", "minor", "major", "epic"
    max_power_above_mpa: float     # Peak watts above MPA (0 if no breakthrough)
    max_pct_above_mpa: float       # Peak % above MPA
    duration_above_mpa_s: float    # Total seconds where power > MPA
    peak_mpa_watts: float          # MPA value at the moment of breakthrough
    peak_power_watts: float        # Actual power at breakthrough moment
    signature_before: dict         # CP, W', Pmax before
    signature_after: dict          # Estimated CP, W', Pmax after
    confidence: float              # 0-100 confidence in the new signature
    details: str                   # Human-readable explanation

    def to_dict(self) -> dict:
        return {
            "is_breakthrough": self.is_breakthrough,
            "type": self.breakthrough_type,
            "max_power_above_mpa_w": round(self.max_power_above_mpa, 1),
            "max_pct_above_mpa": round(self.max_pct_above_mpa, 1),
            "duration_above_mpa_s": round(self.duration_above_mpa_s, 1),
            "peak_mpa_watts": round(self.peak_mpa_watts, 1),
            "peak_power_watts": round(self.peak_power_watts, 1),
            "signature_before": {k: round(v, 1) if isinstance(v, float) else v
                                 for k, v in self.signature_before.items()},
            "signature_after": {k: round(v, 1) if isinstance(v, float) else v
                                for k, v in self.signature_after.items()},
            "confidence": round(self.confidence, 1),
            "details": self.details,
        }


def _compute_mpa(t_above_cp_s: float, pmax: float, cp: float,
                 wprime: float, tau: float) -> float:
    """Compute Maximum Power Available at time t above CP.

    MPA starts at Pmax and decays toward CP as W' is consumed.
    MPA(t) = CP + W' / (t + tau)
    """
    denom = t_above_cp_s + tau
    if denom <= 0:
        return pmax
    return cp + wprime / denom


def detect_breakthrough(power_stream: list[int],
                        current_signature: dict,
                        weight_kg: float = 70.0) -> BreakthroughResult:
    """Detect whether an activity contains a fitness breakthrough.

    Args:
        power_stream:     Per-second power data (watts).
        current_signature: {"cp_w": float, "wprime_j": float, "pmax_w": float, "tau_s": float}
        weight_kg:        Rider weight for W/kg calculations.

    Returns:
        BreakthroughResult with detection details.
    """
    cp = current_signature.get("cp_w", 200.0)
    wprime = current_signature.get("wprime_j", 20000.0)
    pmax = current_signature.get("pmax_w", 600.0)
    tau = current_signature.get("tau_s", 30.0)

    if not power_stream or len(power_stream) < 10:
        return BreakthroughResult(
            is_breakthrough=False,
            breakthrough_type="none",
            max_power_above_mpa=0, max_pct_above_mpa=0,
            duration_above_mpa_s=0, peak_mpa_watts=0,
            peak_power_watts=0,
            signature_before={"cp_w": cp, "wprime_j": wprime, "pmax_w": pmax},
            signature_after={"cp_w": cp, "wprime_j": wprime, "pmax_w": pmax},
            confidence=0, details="Insufficient power data for analysis.",
        )

    # Walk the power stream and compute MPA
    t_above_cp = 0.0       # cumulative time above CP (for W' depletion)
    wprime_remaining = wprime
    max_above = 0.0        # peak watts above MPA
    max_pct = 0.0
    duration_above = 0.0
    peak_mpa = 0.0
    peak_power = 0.0
    above_count = 0

    for i, p in enumerate(power_stream):
        p_watts = float(p) if p else 0.0

        # Current MPA
        mpa = _compute_mpa(t_above_cp, pmax, cp, wprime, tau)

        # Check if power exceeds MPA
        if p_watts > mpa:
            above = p_watts - mpa
            pct = 100.0 * above / mpa if mpa > 0 else 0.0
            if above > max_above:
                max_above = above
                max_pct = pct
                peak_mpa = mpa
                peak_power = p_watts
            above_count += 1
            duration_above += 1.0

        # Update W' depletion model
        if p_watts > cp:
            # Power above CP → deplete W'
            excess = p_watts - cp
            wprime_remaining -= excess
            t_above_cp += 1.0
        else:
            # Power below CP → W' reconstitutes (Skiba 2015 time-varying model)
            # dW'/dt = (W'max - W') / tau,  tau = 546*exp(-0.01*(CP-P)) + 316 s
            deficit = max(0.0, cp - p_watts)
            tau_w = 546.0 * math.exp(-0.01 * deficit) + 316.0
            wprime_remaining = min(
                wprime, wprime_remaining + (wprime - wprime_remaining) / tau_w
            )
            # Reset t_above_cp when essentially fully recovered
            if wprime_remaining >= wprime * 0.95:
                t_above_cp = 0.0

    # Determine breakthrough type
    if max_above <= 0:
        btype = "none"
        confidence = 0.0
        details = "No power exceeded MPA. Current fitness signature appears accurate."
    elif max_pct < 3:
        btype = "minor"
        confidence = 60.0
        details = (f"Minor breakthrough: peak power {peak_power:.0f}W exceeded MPA "
                   f"{peak_mpa:.0f}W by {max_pct:.1f}% ({duration_above:.0f}s above MPA). "
                   f"Small fitness improvement detected.")
    elif max_pct < 10:
        btype = "major"
        confidence = 80.0
        details = (f"Major breakthrough: peak power {peak_power:.0f}W exceeded MPA "
                   f"{peak_mpa:.0f}W by {max_pct:.1f}% ({duration_above:.0f}s above MPA). "
                   f"Significant fitness improvement detected.")
    else:
        btype = "epic"
        confidence = 95.0
        details = (f"Epic breakthrough! Peak power {peak_power:.0f}W exceeded MPA "
                   f"{peak_mpa:.0f}W by {max_pct:.1f}% ({duration_above:.0f}s above MPA). "
                   f"Major fitness improvement — update recommended.")

    # Estimate new signature from breakthrough
    sig_before = {"cp_w": cp, "wprime_j": wprime, "pmax_w": pmax, "tau_s": tau}
    sig_after = dict(sig_before)

    if max_above > 0:
        # New Pmax ≥ peak_power (the new peak is at least what was achieved)
        new_pmax = max(pmax, peak_power * 1.02)  # small margin

        # New CP: if the breakthrough was sustained (>30s), CP likely increased
        if duration_above > 30 and max_pct > 2:
            cp_boost = max_above * 0.1  # conservative: 10% of the excess
            new_cp = cp + cp_boost
        else:
            new_cp = cp

        # New W': if the breakthrough exhausted W' deeply, W' may have grown
        wprime_min_reached = max(0, wprime_remaining)
        if wprime_min_reached < wprime * 0.2:  # >80% depletion
            new_wprime = wprime + (wprime - wprime_min_reached) * 0.15
        else:
            new_wprime = wprime

        sig_after = {
            "cp_w": new_cp,
            "wprime_j": new_wprime,
            "pmax_w": new_pmax,
            "tau_s": tau,
        }

    return BreakthroughResult(
        is_breakthrough=(max_above > 0),
        breakthrough_type=btype,
        max_power_above_mpa=max_above,
        max_pct_above_mpa=max_pct,
        duration_above_mpa_s=duration_above,
        peak_mpa_watts=peak_mpa,
        peak_power_watts=peak_power,
        signature_before=sig_before,
        signature_after=sig_after,
        confidence=confidence,
        details=details,
    )
