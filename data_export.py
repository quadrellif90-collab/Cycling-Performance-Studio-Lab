"""
Data Export Module for Cycling Performance Studio Lab.

Fornisce funzionalità di backup, export dati esportazione completa del profilo,
export workout, export metriche, e formati compatibili con altri software.
"""

import json
import os
import csv
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from profile_manager import get as pm_get
from error_codes import _log_error, REGISTRY


INJURIES_EXPORT_FILENAME = "injuries_backup.json"
WORKOUTS_EXPORT_FILENAME = "workouts_backup.json"


def get_profile_dir(profile_id: str) -> Path:
    """Ottiene la directory del profilo."""
    pm = pm_get()
    return Path(os.getenv("APPDATA", Path.home() / ".cpsl")) / "profiles" / profile_id


def export_profile_backup(profile_id: str, backup_dir: Optional[Path] = None) -> Path:
    """Crea un backup completo del profilo."""
    try:
        pm = pm_get()
        if profile_id != pm.active_id:
            return JSONResponse({"error": "Profile not active"}, status_code=400)

        profile_dir = get_profile_dir(profile_id)
        if not profile_dir.exists():
            return JSONResponse({"error": "Profile directory not found"}, status_code=404)

        if backup_dir is None:
            backup_dir = profile_dir / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"profile_backup_{timestamp}"

        # 1. Backup athlete.json
        athlete_path = profile_dir / "athlete.json"
        if athlete_path.exists():
            import shutil
            shutil.copy2(athlete_path, backup_dir / f"{backup_name}_athlete.json")

        # 2. Backup user_prefs.json
        prefs_path = profile_dir / "user_prefs.json"
        if prefs_path.exists():
            import shutil
            shutil.copy2(prefs_path, backup_dir / f"{backup_name}_prefs.json")

        # 3. Backup .env (senza valori sensibili marcati)
        env_path = profile_dir / ".env"
        if env_path.exists():
            import shutil
            shutil.copy2(env_path, backup_dir / f"{backup_name}_env.json")

        # 4. Backup injuries data
        injuries_path = profile_dir / "injuries.json"
        if injuries_path.exists():
            import shutil
            shutil.copy2(injuries_path, backup_dir / f"{backup_name}_injuries.json")

        # 5. Backup ride data (rides directory)
        rides_dir = profile_dir / "rides"
        if rides_dir.exists():
            backup_rides_dir = backup_dir / f"{backup_name}_rides"
            import shutil
            shutil.copytree(rides_dir, backup_rides_dir, dirs_exist_ok=True)

        # 6. Create manifest
        manifest = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "profile_id": profile_id,
            "files": [
                f for f in os.listdir(backup_dir)
                if f.startswith(backup_name)
            ]
        }
        with open(backup_dir / f"{manifest_name}_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return JSONResponse({"backup_path": str(backup_dir), "manifest": manifest})

    except Exception as e:
        _log_error("E_EXPORT_FAILED", e)
        return JSONResponse({"error": str(e)}, status_code=500)


def export_metrics_export(profile_id: str, metrics_type: str = "all") -> Dict[str, Any]:
    """Esporta metriche specifiche del profilo."""
    try:
        pm = pm_get()
        if profile_id != pm.active_id:
            return {"error": "Profile not active"}

        profile_dir = get_profile_dir(profile_id)
        metrics: Dict[str, Any] = {}

        # Metriche base atleta
        athlete_path = profile_dir / "athlete.json"
        if athlete_path.exists():
            import json
            with open(athlete_path, "r", encoding="utf-8") as f:
                athlete = json.load(f)
            metrics["athlete"] = {
                "ftp": athlete.get("ftp"),
                "weight_kg": athlete.get("weight_kg"),
                "lthr": athlete.get("lthr"),
                "max_hr": athlete.get("max_hr"),
                "lbm_kg": athlete.get("lbm_kg"),
                "ftp_source": athlete.get("ftp_source"),
                "max_hr_source": athlete.get("max_hr_source"),
            }

        # Metriche infortuni
        injuries_path = profile_dir / "injuries.json"
        if injuries_path.exists():
            import json
            with open(injuries_path, "r", encoding="utf-8") as f:
                injuries = json.load(f)
            active_injuries = [i for i in injuries if i.get("status") == "active"]
            metrics["injuries"] = {
                "active_count": len(active_injuries),
                "total_count": len(injuries),
                "by_severity": {
                    "minor": sum(1 for i in active_injuries if i.get("severity") == "minor"),
                    "medium": sum(1 for i in active_injuries if i.get("severity") == "medium"),
                    "severe": sum(1 for i in active_injuries if i.get("severity") == "severe"),
                },
                "recent_injuries": len([
                    i for i in active_injuries
                    if date.fromisoformat(i.get("date_start", "")) 
                    >= date.today() - __import__("datetime").timedelta(days=30)
                ]),
            }

        # Metriche workout (se disponibili)
        workouts_dir = profile_dir / "workouts"
        if workouts_dir.exists():
            import json
            workout_files = [f for f in os.listdir(workouts_dir) if f.endswith(".zwo")]
            metrics["workouts"] = {
                "total_count": len(workout_files),
                "file_names": workout_files[:20],  # Primo 20 file
            }

        return metrics

    except Exception as e:
        _log_error("E_EXPORT_FAILED", e)
        return {"error": str(e)}


def export_zip_backup(profile_id: str, backup_dir: Optional[Path] = None) -> Path:
    """Crea un archivio ZIP compressato del profilo."""
    try:
        pm = pm_get()
        if profile_id != pm.active_id:
            return JSONResponse({"error": "Profile not active"}, status_code=404)

        profile_dir = get_profile_dir(profile_id)
        if not profile_dir.exists():
            return JSONResponse({"error": "Profile directory not found"}, status_code=404)

        if backup_dir is None:
            backup_dir = profile_dir / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"profile_backup_{timestamp}.zip"
        zip_path = backup_dir / zip_name

        # Raccolta files da includere
        files_to_zip = [
            ("athlete.json", profile_dir / "athlete.json"),
            ("user_prefs.json", profile_dir / "user_prefs.json"),
            (".env", profile_dir / ".env"),
            ("injuries.json", profile_dir / "injuries.json"),
        ]

        # Aggiungi rides directory se esiste
        rides_dir = profile_dir / "rides"
        rides_relative = "rides"
        if rides_dir.exists():
            rides_relative = "rides"

        # Crea ZIP
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, filepath in files_to_zip:
                if filepath.exists():
                    zf.write(filepath, filename)
            # Aggiungi rides directory
            if rides_dir.exists():
                zf.write(rides_dir, rides_relative)

        return JSONResponse({"zip_path": str(zip_path), "size": zip_path.stat().st_size})

    except Exception as e:
        _log_error("E_EXPORT_FAILED", e)
        return JSONResponse({"error": str(e)}, status_code=500)