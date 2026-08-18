"""Capacity Cap module for Cycling Performance Studio Lab.

Ramp test FTP advisory and capacity capping logic.
Used by fitness_estimation.py for ramp test guidance.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Coggan ramp test advisory thresholds
RAMP_TEST_FTP_DROP_THRESHOLD = 0.05  # 5% drop indicates potential FTP overestimation
RAMP_TEST_MIN_INCREASE = 5.0  # Minimum FTP increase expected from ramp test (watts)


def ramp_test_advisory(
    current_ftp: float,
    ramp_test_ftp: float,
    weight_kg: Optional[float] = None,
) -> dict:
    """Generate advisory based on ramp test FTP result.

    Args:
        current_ftp: Current known FTP (watts)
        ramp_test_ftp: FTP estimated from ramp test (watts)
        weight_kg: Athlete weight for w/kg analysis

    Returns:
        dict with advisory fields
    """
    advisory = {
        "status": "ok",
        "message": "",
        "suggestion": "",
    }

    if current_ftp <= 0 or ramp_test_ftp <= 0:
        advisory["status"] = "error"
        advisory["message"] = "FTP values must be positive"
        return advisory

    pct_change = (ramp_test_ftp - current_ftp) / current_ftp

    if pct_change > 0.10:
        advisory["status"] = "warning"
        advisory["message"] = f"FTP increase of {pct_change*100:.1f}% seems unusually large"
        advisory["suggestion"] = "Consider using 95% of ramp test value or retesting"
    elif pct_change < -RAMP_TEST_FTP_DROP_THRESHOLD:
        advisory["status"] = "info"
        advisory["message"] = f"FTP decreased by {abs(pct_change)*100:.1f}%"
        advisory["suggestion"] = "Normal variation if fatigue or different test conditions"
    elif abs(pct_change) < 0.02:
        advisory["status"] = "ok"
        advisory["message"] = f"FTP consistent with ramp test ({pct_change*100:+.1f}%)"
    else:
        advisory["status"] = "ok"
        advisory["message"] = f"FTP updated: {current_ftp:.0f}W -> {ramp_test_ftp:.0f}W ({pct_change*100:+.1f}%)"

    if weight_kg and weight_kg > 0:
        new_wkg = ramp_test_ftp / weight_kg
        advisory["w_kg"] = round(new_wkg, 2)
        if new_wkg > 6.0:
            advisory["suggestion"] = (
                advisory.get("suggestion", "") +
                " W/kg value is very high for amateur athletes - verify weight."
            ).strip()

    return advisory


def cap_ftp(ftp: float, weight_kg: Optional[float] = None) -> float:
    """Cap FTP to reasonable bounds."""
    ftp = max(50.0, min(600.0, ftp))
    if weight_kg and weight_kg > 0:
        wkg = ftp / weight_kg
        if wkg > 7.0:
            ftp = weight_kg * 7.0
    return round(ftp, 1)
