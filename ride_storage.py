"""Ride Storage module for Cycling Performance Studio Lab.

Handles ICU ride data storage and retrieval.
Used by power_curve.py to load cached ride data for power curve computation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _icu_rides_dir(profile_id: Optional[str] = None) -> Path:
    """Return the path to ICU rides cache directory."""
    from user_home import domestique_home
    home = domestique_home()
    if profile_id:
        return home / "rides" / profile_id
    return home / "rides"


def load_cached_rides(profile_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Load cached ride data from disk."""
    rides_dir = _icu_rides_dir(profile_id)
    if not rides_dir.exists():
        return []

    rides = []
    ride_files = sorted(rides_dir.glob("*.json"), reverse=True)[:limit]
    for rf in ride_files:
        try:
            with open(rf, "r", encoding="utf-8") as f:
                data = json.load(f)
                rides.append(data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load ride {rf}: {e}")

    return rides


def save_ride_data(profile_id: str, ride_id: str, data: Dict[str, Any]) -> None:
    """Save ride data to cache."""
    rides_dir = _icu_rides_dir(profile_id)
    rides_dir.mkdir(parents=True, exist_ok=True)
    ride_path = rides_dir / f"{ride_id}.json"
    try:
        with open(ride_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save ride {ride_id}: {e}")


def list_cached_ride_ids(profile_id: str) -> List[str]:
    """List cached ride IDs."""
    rides_dir = _icu_rides_dir(profile_id)
    if not rides_dir.exists():
        return []
    return [rf.stem for rf in rides_dir.glob("*.json")]


def clear_ride_cache(profile_id: str) -> int:
    """Clear all cached rides for a profile. Returns count removed."""
    rides_dir = _icu_rides_dir(profile_id)
    if not rides_dir.exists():
        return 0
    count = 0
    for rf in rides_dir.glob("*.json"):
        rf.unlink()
        count += 1
    return count
