"""Zones module for Cycling Performance Studio Lab.

HR zones and power zones calculation based on athlete profile data.
Used by training_live.py for workout classification and feedback.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def hr_zones_from_lthr(lthr: int, max_hr: Optional[int] = None) -> List[Dict[str, float]]:
    """Calculate HR zones from LTHR using Coggan model."""
    if lthr <= 0:
        return []

    zones = [
        {"zone": 1, "name": "Recovery", "low": 0.0, "high": lthr * 0.68},
        {"zone": 2, "name": "Aerobic", "low": lthr * 0.68, "high": lthr * 0.83},
        {"zone": 3, "name": "Tempo", "low": lthr * 0.83, "high": lthr * 0.94},
        {"zone": 4, "name": "Threshold", "low": lthr * 0.94, "high": lthr * 1.05},
        {"zone": 5, "name": "VO2max", "low": lthr * 1.05, "high": lthr * 1.20},
    ]

    if max_hr and max_hr > lthr:
        zones[4]["high"] = max_hr

    return zones


def power_zones_from_ftp(ftp: float) -> List[Dict[str, float]]:
    """Calculate power zones from FTP using Coggan model."""
    if ftp <= 0:
        return []

    zones = [
        {"zone": 1, "name": "Active Recovery", "low": 0.0, "high": ftp * 0.55},
        {"zone": 2, "name": "Endurance", "low": ftp * 0.55, "high": ftp * 0.75},
        {"zone": 3, "name": "Tempo", "low": ftp * 0.75, "high": ftp * 0.90},
        {"zone": 4, "name": "Threshold", "low": ftp * 0.90, "high": ftp * 1.05},
        {"zone": 5, "name": "VO2max", "low": ftp * 1.05, "high": ftp * 1.20},
        {"zone": 6, "name": "Anaerobic", "low": ftp * 1.20, "high": ftp * 1.50},
        {"zone": 7, "name": "Neuromuscular", "low": ftp * 1.50, "high": 9999.0},
    ]

    return zones


def classify_power_in_zones(power: float, ftp: float) -> int:
    """Return which power zone a given power value falls into."""
    zones = power_zones_from_ftp(ftp)
    for zone in zones:
        if zone["low"] <= power < zone["high"]:
            return zone["zone"]
    return 7 if power > (ftp * 1.50) else 1


def classify_hr_in_zones(hr: float, lthr: int) -> int:
    """Return which HR zone a given heart rate falls into."""
    zones = hr_zones_from_lthr(lthr)
    for zone in zones:
        if zone["low"] <= hr < zone["high"]:
            return zone["zone"]
    return 5 if hr > (lthr * 1.20) else 1


def time_in_zones(power_data: List[float], ftp: float) -> Dict[int, float]:
    """Calculate time spent in each power zone given a list of power samples (1 per second)."""
    result: Dict[int, float] = {z: 0.0 for z in range(1, 8)}
    for power in power_data:
        zone = classify_power_in_zones(power, ftp)
        result[zone] = result.get(zone, 0.0) + 1.0
    return result
