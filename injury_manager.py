"""Injury Manager for Cycling Performance Studio Lab.

Gestione infortuni ciclisti con protocolli return-to-ride (RTP).
Persistenza su file JSON per ogni profilo.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

_injury_manager_instances: Dict[str, "InjuryManager"] = {}


def get(profile_id: str) -> "InjuryManager":
    if profile_id not in _injury_manager_instances:
        _injury_manager_instances[profile_id] = InjuryManager(profile_id)
    return _injury_manager_instances[profile_id]


class Injury:
    def __init__(
        self,
        injury_id: str,
        profile_id: str,
        name: str,
        date_start: date,
        date_end: Optional[date] = None,
        severity: str = "medium",
        status: str = "active",
        notes: str = "",
    ) -> None:
        self.injury_id = injury_id
        self.profile_id = profile_id
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        self.severity = severity
        self.status = status
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "injury_id": self.injury_id,
            "profile_id": self.profile_id,
            "name": self.name,
            "date_start": self.date_start.isoformat(),
            "date_end": self.date_end.isoformat() if self.date_end else None,
            "severity": self.severity,
            "status": self.status,
            "notes": self.notes,
        }


class InjurySummary:
    def __init__(
        self,
        active_count: int,
        total_count: int,
        by_severity: Dict[str, int],
        recent_injuries: List[Dict[str, Any]],
    ) -> None:
        self.active_count = active_count
        self.total_count = total_count
        self.by_severity = by_severity
        self.recent_injuries = recent_injuries


class InjuryManager:
    INJURIES_FILENAME = "injuries.json"

    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        self._data_dir = Path(os.getenv("APPDATA", Path.home() / ".cpsl")) / "profiles" / profile_id
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._file_path = self._data_dir / self.INJURIES_FILENAME
        self._lock = threading.Lock()
        self._injuries: Dict[str, Injury] = {}
        self._load_injuries()

    def _load_injuries(self) -> None:
        if not self._file_path.exists():
            self._injuries = {}
            return
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._injuries = {}
            for inj_data in data:
                inj = Injury(
                    injury_id=inj_data.get("injury_id", ""),
                    profile_id=self.profile_id,
                    name=inj_data.get("name", ""),
                    date_start=date.fromisoformat(inj_data.get("date_start", str(date.today()))),
                    date_end=date.fromisoformat(inj_data["date_end"]) if inj_data.get("date_end") else None,
                    severity=inj_data.get("severity", "medium"),
                    status=inj_data.get("status", "active"),
                    notes=inj_data.get("notes", ""),
                )
                self._injuries[inj.injury_id] = inj
            logger.info(f"Loaded {len(self._injuries)} injuries for profile {self.profile_id}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to load injuries: {e}")
            self._injuries = {}

    def _save_injuries(self) -> None:
        data = [inj.to_dict() for inj in self._injuries.values()]
        fd, tmp_path = tempfile.mkstemp(dir=self._data_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, self._file_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
        logger.info(f"Saved {len(self._injuries)} injuries for profile {self.profile_id}")

    def create_injury(
        self,
        name: str,
        date_start: date,
        severity: str = "medium",
        status: str = "active",
        notes: str = "",
    ) -> Injury:
        injury_id = f"inj_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        if date_start > date.today():
            raise ValueError("Data inizio infortunio non puo' essere nel futuro")
        inj = Injury(
            injury_id=injury_id,
            profile_id=self.profile_id,
            name=name,
            date_start=date_start,
            severity=severity,
            status=status,
            notes=notes,
        )
        with self._lock:
            self._injuries[injury_id] = inj
            self._save_injuries()
        logger.info(f"Created injury: {injury_id} - {name}")
        return inj

    def get_injury(self, injury_id: str) -> Optional[Injury]:
        return self._injuries.get(injury_id)

    def update_injury(
        self,
        injury_id: str,
        name: Optional[str] = None,
        date_end: Optional[date] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Injury]:
        inj = self._injuries.get(injury_id)
        if not inj:
            return None
        with self._lock:
            if name is not None:
                inj.name = name
            if date_end is not None:
                inj.date_end = date_end
            if severity is not None:
                inj.severity = severity
            if status is not None:
                inj.status = status
            if notes is not None:
                inj.notes = notes
            self._save_injuries()
        logger.info(f"Updated injury: {injury_id}")
        return inj

    def resolve_injury(self, injury_id: str, date_resolved: date) -> Optional[Injury]:
        inj = self._injuries.get(injury_id)
        if not inj:
            return None
        with self._lock:
            inj.status = "resolved"
            inj.date_end = date_resolved
            self._save_injuries()
        logger.info(f"Resolved injury: {injury_id}")
        return inj

    def delete_injury(self, injury_id: str) -> bool:
        with self._lock:
            inj = self._injuries.pop(injury_id, None)
            if inj:
                self._save_injuries()
                logger.info(f"Deleted injury: {injury_id}")
                return True
        return False

    def get_active_injuries(self) -> List[Injury]:
        return [inj for inj in self._injuries.values() if inj.status == "active"]

    def get_resolved_injuries(self) -> List[Injury]:
        return [inj for inj in self._injuries.values() if inj.status == "resolved"]

    def get_injuries_by_severity(self, severity: str) -> List[Injury]:
        return [inj for inj in self._injuries.values() if inj.severity == severity]

    def get_injuries_date_range(self, start_date: date, end_date: date) -> List[Injury]:
        result = []
        for inj in self._injuries.values():
            if start_date <= inj.date_start <= end_date:
                result.append(inj)
            elif inj.date_end and start_date <= inj.date_end <= end_date:
                result.append(inj)
        return result

    def get_summary(self) -> InjurySummary:
        from datetime import timedelta

        active = self.get_active_injuries()
        by_severity: Dict[str, int] = {"minor": 0, "medium": 0, "severe": 0}
        for inj in self._injuries.values():
            by_severity[inj.severity] = by_severity.get(inj.severity, 0) + 1
        thirty_days_ago = date.today() - timedelta(days=30)
        recent = self.get_injuries_date_range(thirty_days_ago, date.today())
        return InjurySummary(
            active_count=len(active),
            total_count=len(self._injuries),
            by_severity=by_severity,
            recent_injuries=[inj.to_dict() for inj in recent],
        )


def register_routes(app: Any) -> None:

    @app.post("/api/injuries")
    async def api_create_injury(request: Request):
        data = await request.json()
        try:
            from profile_manager import get as pm_get

            pm = pm_get()
            im = get(pm.active_id)
            inj = im.create_injury(
                name=data.get("name", ""),
                date_start=date.fromisoformat(data.get("date_start", "")),
                severity=data.get("severity", "medium"),
                status=data.get("status", "active"),
                notes=data.get("notes", ""),
            )
            return {"success": True, "injury_id": inj.injury_id}
        except Exception as e:
            logger.error(f"Failed to create injury: {e}")
            return JSONResponse({"error": str(e)}, status_code=400)

    @app.get("/api/injuries")
    async def api_list_injuries():
        from profile_manager import get as pm_get

        pm = pm_get()
        im = get(pm.active_id)
        summary = im.get_summary()
        return {
            "active_injuries": [inj.to_dict() for inj in im.get_active_injuries()],
            "summary": {
                "active_count": summary.active_count,
                "total_count": summary.total_count,
                "by_severity": summary.by_severity,
                "recent_injuries": summary.recent_injuries,
            },
        }

    @app.put("/api/injuries/{injury_id}")
    async def api_update_injury(injury_id: str, request: Request):
        data = await request.json()
        from profile_manager import get as pm_get

        pm = pm_get()
        im = get(pm.active_id)
        inj = im.update_injury(
            injury_id=injury_id,
            name=data.get("name"),
            date_end=date.fromisoformat(data["date_end"]) if data.get("date_end") else None,
            severity=data.get("severity"),
            status=data.get("status"),
            notes=data.get("notes"),
        )
        if inj is None:
            return JSONResponse({"error": "Infortunio non trovato"}, status_code=404)
        return {"success": True}

    @app.post("/api/injuries/{injury_id}/resolve")
    async def api_resolve_injury(injury_id: str, request: Request):
        data = await request.json()
        from profile_manager import get as pm_get

        pm = pm_get()
        im = get(pm.active_id)
        inj = im.resolve_injury(
            injury_id, date.fromisoformat(data.get("date_resolved", date.today().isoformat()))
        )
        if inj is None:
            return JSONResponse({"error": "Infortunio non trovato"}, status_code=404)
        return {"success": True}

    @app.delete("/api/injuries/{injury_id}")
    async def api_delete_injury(injury_id: str):
        from profile_manager import get as pm_get

        pm = pm_get()
        im = get(pm.active_id)
        deleted = im.delete_injury(injury_id)
        if not deleted:
            return JSONResponse({"error": "Infortunio non trovato"}, status_code=404)
        return {"success": True}
