"""
Profile Manager for Cycling Performance Studio Lab.

Singleton pattern managing athlete profiles, sync state, and profile switching.
Handles per-profile .env files, athlete.json schema validation, and migration.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import tempfile
from collections import deque
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import config, _ConfigProxy
from error_codes import Codes, _log_error, REGISTRY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Profile ID validation
# ---------------------------------------------------------------------------
_PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_profile_manager: Optional["ProfileManager"] = None


def get() -> "ProfileManager":
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    return _profile_manager


# ---------------------------------------------------------------------------
# ProfileManager class
# ---------------------------------------------------------------------------


class ProfileManager:
    """Singleton profile manager."""

    def __init__(self) -> None:
        # Data directory: ~/.cpsl/ or per-user AppData
        if os.name == "nt":  # Windows
            self._data_dir = Path(
                os.getenv("APPDATA", Path.home() / ".cpsl")
            )
        else:  # macOS / Linux
            self._data_dir = Path.home() / ".cpsl"

        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._profiles_dir = self._data_dir / "profiles"
        self._profiles_dir.mkdir(parents=True, exist_ok=True)

        # In-memory state
        self._active_id: Optional[str] = None
        self._lock = threading.RLock()
        self._switch_lock = threading.Lock()  # Bounded 10s gate
        self._library_rows_lock = threading.Lock()
        self._library_tags_lock = threading.Lock()

        # Load / migrate
        self._maybe_migrate_data_dir()

        # Load active profile
        self._load_active_profile()

    def _load_active_profile(self) -> None:
        """Load the active profile, or set first profile as active if none configured."""
        profiles = self.list_profiles()
        if not profiles:
            self._active_id = None
            return

        # Try to find a fully configured profile
        for pid in profiles:
            athlete = self._load_athlete_json(pid)
            if athlete and "ftp" in athlete and "weight_kg" in athlete:
                self._active_id = pid
                return

        # Use first profile if none configured
        self._active_id = profiles[0]

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def list_profiles(self) -> List[str]:
        """Return sorted list of profile IDs."""
        if not self._profiles_dir.exists():
            return []
        return sorted(
            p.name
            for p in self._profiles_dir.iterdir()
            if p.is_dir() and _PROFILE_ID_RE.match(p.name)
        )

    def is_fully_configured(self) -> bool:
        """Check if at least one profile has athlete.json with required fields."""
        profiles = self.list_profiles()
        if not profiles:
            return False
        for pid in profiles:
            athlete = self._load_athlete_json(pid)
            if athlete and "ftp" in athlete and "weight_kg" in athlete:
                return True
        return False

    def _make_unique_id(self, pid: str) -> str:
        """Ensure profile ID is unique by appending number if needed."""
        existing = self.list_profiles()
        if pid not in existing:
            return pid
        # Append counter until unique
        counter = 1
        while True:
            new_pid = f"{pid}-{counter}"
            if new_pid not in existing:
                return new_pid
            counter += 1

    def create_profile(self, name: str, color: Optional[str] = None) -> str:
        """Create a new profile with default athlete.json."""
        import re as _re

        # Generate ID from name
        pid = _re.sub(r"\s+", "-", name.lower()).strip("-")
        pid = _re.sub(r"[-]+", "-", pid)[:32]
        if not _PROFILE_ID_RE.match(pid):
            pid = pid[:32]  # best-effort

        # Ensure unique
        pid = self._make_unique_id(pid)

        prof_dir = self._profiles_dir / pid
        if prof_dir.exists():
            raise ValueError(f"Profile '{pid}' already exists")

        prof_dir.mkdir(parents=True, exist_ok=True)

        # Default athlete.json
        default_athlete = {
            "ftp": 200,
            "weight_kg": 70,
            "lthr": 180,
            "max_hr": 190,
            "lbm_kg": 56,
            "age": 30,
            "sex": "M",
            "target_mode": "performance",
            "ftp_source": "manual",
            "max_hr_source": "manual",
            "wprime_source": "manual",
            "pmax_source": "manual",
            "ftp_tests": [],
        }

        # Write athlete.json atomically
        athlete_path = prof_dir / "athlete.json"
        self._atomic_write_json(athlete_path, default_athlete)

        # Create .env file (per-profile)
        env_path = prof_dir / ".env"
        self._atomic_write_env(env_path, {})

        # Create user_prefs.json
        prefs_path = prof_dir / "user_prefs.json"
        default_prefs = {
            "hours_per_week": 6,
            "available_days": [1, 2, 3, 4, 5],
            "rest_days": [6, 7],
            "default_cadence": 90,
            "zones_auto": True,
        }
        self._atomic_write_json(prefs_path, default_prefs)

        # Create device_prefs.json
        device_path = prof_dir / "device_prefs.json"
        default_device = {}
        self._atomic_write_json(device_path, default_device)

        # Create plans/ and rides/ dirs
        (prof_dir / "plans").mkdir(exist_ok=True)
        (prof_dir / "rides").mkdir(exist_ok=True)

        # Index in profiles_indexed.json
        self._update_profiles_indexed()

        logger.info(f"Created profile: {pid}")
        return pid

    def delete_profile(self, profile_id: str) -> None:
        """Delete a profile and its directory."""
        with self._lock:
            prof_dir = self._profiles_dir / profile_id
            if prof_dir.exists():
                import shutil
                shutil.rmtree(prof_dir)
                logger.info(f"Deleted profile: {profile_id}")
                self._update_profiles_indexed()
            else:
                raise ValueError(f"Profile '{profile_id}' not found")

    def switch(self, profile_id: str) -> None:
        """Switch active profile with sync gate."""
        # Use bounded acquire (no context manager, supports timeout)
        acquired = self._switch_lock.acquire(timeout=config.SYNC_GATE_TIMEOUT_S)
        if not acquired:
            from error_codes import Codes
            _log_error(Codes.PROFILE_SWITCH_FAILED)
            raise RuntimeError("Sync gate timeout - another profile switch in progress")

        try:
            # Stop any active sync
            # db_mod.stop_sync()  # abstracted

            # Load profile
            prof_dir = self._profiles_dir / profile_id
            if not prof_dir.exists():
                raise ValueError(f"Profile '{profile_id}' not found")

            # Load athlete.json
            athlete = self._load_athlete_json(profile_id)
            if not athlete:
                raise ValueError(f"Profile '{profile_id}' has invalid or missing athlete.json")

            # Validate required fields
            if "ftp" not in athlete or "weight_kg" not in athlete:
                raise ValueError(
                    f"Profile '{profile_id}' athlete.json missing required fields (ftp, weight_kg)"
                )

            # Set active
            self._active_id = profile_id

            # Re-initialize config proxy with new profile values
            # (config.__getattr__ will resolve via ProfileManager)

            logger.info(f"Switched to profile: {profile_id}")
            # Trigger sync restart
            # db_mod.restart_sync()
        finally:
            self._switch_lock.release()

    def apply_training_dirs(self) -> str:
        """Resolve WORKOUT_DIR with priority:
        1. <active_dir>/user_paths.json["workout_dir"]
        2. <active_dir>/workouts/
        3. Bundled default
        """
        if not self._active_id:
            from error_codes import Codes
            _log_error(Codes.PROFILE_LOAD)
            return ""

        active_dir = self._profiles_dir / self._active_id

        # Check user_paths.json
        user_paths_path = active_dir / "user_paths.json"
        if user_paths_path.exists():
            try:
                up = json.loads(user_paths_path.read_text())
                if up.get("workout_dir"):
                    return str(active_dir / up["workout_dir"])
            except (json.JSONDecodeError, KeyError):
                pass

        # Default: <active_dir>/workouts/
        workouts_dir = active_dir / "workouts"
        if workouts_dir.exists():
            return str(workouts_dir)

        # Bundled default (placeholder - implement if needed)
        return str(workouts_dir)

    # ---- Athlete JSON helpers ----

    def _load_athlete_json(self, profile_id: Optional[str] = None) -> Optional[Dict]:
        """Load athlete.json for profile, with migration if needed."""
        if profile_id is None:
            profile_id = self._active_id
        if not profile_id:
            return None

        path = self._profiles_dir / profile_id / "athlete.json"
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Schema migration
            data = self._maybe_migrate_athlete_data(data)
            return data
        except (json.JSONDecodeError, ValueError) as e:
            _log_error(Codes.PROFILE_LOAD, ValueError(e), path=str(path))
            return None

    def _maybe_migrate_athlete_data(self, data: Dict) -> Dict:
        """Migrate athlete data to current schema version."""
        # v3 -> v4: add source tracking fields if missing
        if "ftp_source" not in data:
            data["ftp_source"] = "manual"
        if "max_hr_source" not in data:
            data["max_hr_source"] = "manual"
        if "wprime_source" not in data:
            data["wprime_source"] = "manual"
        if "pmax_source" not in data:
            data["pmax_source"] = "manual"
        if "ftp_tests" not in data:
            data["ftp_tests"] = []
        # Ensure numeric types
        try:
            data["ftp"] = float(data.get("ftp", 200))
            data["weight_kg"] = float(data.get("weight_kg", 70))
        except (ValueError, TypeError):
            data["ftp"] = 200
            data["weight_kg"] = 70
        return data

    def save_athlete(self, data: Dict[str, Any]) -> None:
        """Save validated athlete data."""
        if not self._active_id:
            raise ValueError("No active profile")

        athlete_path = self._profiles_dir / self._active_id / "athlete.json"

        # Validate ranges
        ftp = data.get("ftp", 0)
        weight = data.get("weight_kg", 0)
        lthr = data.get("lthr", 0)
        max_hr = data.get("max_hr", 0)
        lbm_kg = data.get("lbm_kg", 0)

        # FTP: 50-600 W
        if not (50 <= ftp <= 600):
            raise ValueError(f"FTP out of range: {ftp} (must be 50-600 W)")

        # Weight: 30-200 kg
        if not (30 <= weight <= 200):
            raise ValueError(f"Weight out of range: {weight} (must be 30-200 kg)")

        # LTHR: 100-250 bpm
        if lthr and not (100 <= lthr <= 250):
            raise ValueError(f"LTHR out of range: {lthr} (must be 100-250 bpm)")

        # Max HR: 100-250 bpm
        if max_hr and not (100 <= max_hr <= 250):
            raise ValueError(f"Max HR out of range: {max_hr} (must be 100-250 bpm)")

        # LBM: 20-150 kg
        if lbm_kg and not (20 <= lbm_kg <= 150):
            raise ValueError(f"LBM out of range: {lbm_kg} (must be 20-150 kg)")

        # Track source
        if "ftp_source" not in data:
            data["ftp_source"] = "manual"
        if "max_hr_source" not in data:
            data["max_hr_source"] = "manual"
        if "wprime_source" not in data:
            data["wprime_source"] = "manual"
        if "pmax_source" not in data:
            data["pmax_source"] = "manual"

        # Atomic write
        self._atomic_write_json(athlete_path, data)
        logger.info(f"Saved athlete data for profile: {self._active_id}")

    def _maybe_migrate_data_dir(self) -> None:
        """Move .chickencycling/ -> ~/.cpsl/ on first boot (legacy migration)."""
        legacy = Path.home() / ".chickencycling"
        if legacy.exists() and not self._data_dir.exists():
            logger.info("Migrating data from .chickencycling to ~/.cpsl")
            try:
                import shutil
                new_data = self._data_dir / "profiles"
                # Copy existing profiles if any
                if legacy.is_dir():
                    # Find any profile dirs
                    for p in legacy.iterdir():
                        if p.is_dir() and p.name.replace("-", "").replace("_", "").isalnum():
                            # Simple check - just copy the directory
                            target = self._profiles_dir / p.name
                            if not target.exists():
                                import shutil
                                shutil.copytree(p, target)
                # Now point to new location
                self._profiles_dir = new_data
                self._profiles_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Legacy migration failed: {e}")

    # ---- .env helpers ----

    def save_env(
        self,
        icu_athlete_id: str,
        icu_api_key: str,
        icu_access_token: str,
        bia_vision_api_key: str = "",
    ) -> None:
        """Save per-profile .env credentials atomically."""
        if not self._active_id:
            raise ValueError("No active profile")

        prof_dir = self._profiles_dir / self._active_id
        env_path = prof_dir / ".env"

        lines = [
            f"ICU_ATHLETE_ID={icu_athlete_id}",
            f"ICU_API_KEY={icu_api_key}",
            f"ICU_ACCESS_TOKEN={icu_access_token}",
            f"BIA_VISION_API_KEY={bia_vision_api_key}",
        ]

        # Write to temp file then rename (atomic)
        fd, tmp_path = tempfile.mkstemp(dir=prof_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("\n".join(lines))
            os.replace(tmp_path, env_path)
        except Exception:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

        logger.info(f"Saved .env for profile: {self._active_id}")

    def _atomic_write_json(self, path: Path, data: Dict) -> None:
        """Write JSON file atomically using tempfile + rename."""
        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, path)
        except Exception:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _atomic_write_env(self, path: Path, data: Dict[str, str]) -> None:
        """Write .env file atomically using tempfile + rename."""
        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                for key, value in data.items():
                    f.write(f"{key}={value}\n")
            os.replace(tmp_path, path)
        except Exception:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    # ---- Public data getters ----

    def active_athlete(self) -> Optional[Dict]:
        """Return current profile's athlete dict."""
        if not self._active_id:
            return None
        return self._load_athlete_json(self._active_id)

    def active_env(self) -> Dict[str, str]:
        """Return current profile's .env dict."""
        if not self._active_id:
            return {}
        prof_dir = self._profiles_dir / self._active_id
        env_path = prof_dir / ".env"
        if not env_path.exists():
            return {}
        try:
            content = env_path.read_text(encoding="utf-8")
            result = {}
            for line in content.strip().split("\n"):
                if "=" in line:
                    key, val = line.split("=", 1)
                    result[key.strip()] = val.strip()
            return result
        except Exception:
            return {}

    # ---- Sync helpers ----

    # db_mod.* methods abstracted - concrete impl depends on DB layer

    def list_targets(self) -> List[Dict[str, Any]]:
        """List configured sync targets (registry + status)."""
        from sync_targets import get_target, Codes

        targets = []
        # Always include Intervals.icu base
        targets.append(
            {
                "key": "intervals_icu",
                "display_name": "Intervals.icu",
                "can_write": True,
                "is_configured": self._is_icu_configured(),
            }
        )
        # Add any additional targets from sync_targets module
        for key in ["strava", "trainingpeaks", "garmin", "google_fit", "apple_health"]:
            target = get_target(key)
            if target:
                targets.append(
                    {
                        "key": target.key,
                        "display_name": target.display_name,
                        "can_write": getattr(target, "can_write", False),
                        "is_configured": target.is_configured()
                        if hasattr(target, "is_configured")
                        else False,
                    }
                )
        return targets

    def _is_icu_configured(self) -> bool:
        """Check if Intervals.icu credentials are set for active profile."""
        env = self.active_env()
        return bool(env.get("ICU_ATHLETE_ID") and env.get("ICU_API_KEY"))

    def _update_profiles_indexed(self) -> None:
        """Update the global profiles_indexed.json registry."""
        indexed_path = self._data_dir / "profiles_indexed.json"
        profiles = self.list_profiles()

        # Read existing or create new
        if indexed_path.exists():
            try:
                data = json.loads(indexed_path.read_text())
            except (json.JSONDecodeError, ValueError):
                data = {"profiles": [], "version": 1}
        else:
            data = {"profiles": [], "version": 1}

        # Merge: keep existing entries, add/update current
        existing_ids = {p["id"] for p in data.get("profiles", [])}
        for pid in profiles:
            if pid not in existing_ids:
                athlete = self._load_athlete_json(pid)
                data["profiles"].append(
                    {
                        "id": pid,
                        "name": pid,
                        "color": "blue",  # default, can be overridden
                        "ftp": athlete.get("ftp", 0) if athlete else 0,
                        "weight_kg": athlete.get("weight_kg", 0) if athlete else 0,
                        "last_modified": (
                            datetime.now().isoformat() if athlete else None
                        ),
                    }
                )

        # Write atomically
        self._atomic_write_json(indexed_path, data)

    # ---- Shutdown ----

    def shutdown(self) -> None:
        """Cleanup on app exit."""
        logger.info("ProfileManager shutdown")
        # Stop any active sync
        # db_mod.stop_sync()  # concrete impl per DB layer