"""Session Manager for Cycling Performance Studio Lab.

Handles multi-user session isolation and concurrent profile access.
Provides session tokens, profile locking, and audit logging.

For desktop app: single-user with profile switching.
For web mode: session-based isolation with optional auth.
"""

from __future__ import annotations

import logging
import secrets
import threading
import time
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

SESSION_TTL = 3600.0  # 1 hour
MAX_SESSIONS = 32


class Session:
    """Represents an active user session."""

    def __init__(self, session_id: str, profile_id: str, created_at: float) -> None:
        self.session_id = session_id
        self.profile_id = profile_id
        self.created_at = created_at
        self.last_activity = created_at
        self.metadata: dict[str, Any] = {}

    @property
    def is_expired(self) -> bool:
        return (time.monotonic() - self.last_activity) > SESSION_TTL

    def touch(self) -> None:
        self.last_activity = time.monotonic()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "profile_id": self.profile_id,
            "created_at": datetime.fromtimestamp(self.created_at, tz=UTC).isoformat(),
            "last_activity": datetime.fromtimestamp(self.last_activity, tz=UTC).isoformat(),
            "is_expired": self.is_expired,
            "metadata": self.metadata,
        }


class SessionManager:
    """Thread-safe session manager with TTL expiration."""

    def __init__(self) -> None:
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = threading.Lock()
        self._profile_locks: dict[str, str] = {}  # profile_id -> session_id

    def create_session(self, profile_id: str, metadata: dict | None = None) -> Session:
        session_id = secrets.token_urlsafe(32)
        now = time.monotonic()
        session = Session(session_id, profile_id, now)
        if metadata:
            session.metadata = metadata

        with self._lock:
            while len(self._sessions) >= MAX_SESSIONS:
                oldest_id, _ = self._sessions.popitem(last=False)
                self._profile_locks = {
                    k: v for k, v in self._profile_locks.items() if v != oldest_id
                }
            self._sessions[session_id] = session
            self._profile_locks[profile_id] = session_id

        logger.info(f"Created session {session_id[:8]}... for profile {profile_id}")
        return session

    def get_session(self, session_id: str) -> Session | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session and not session.is_expired:
                session.touch()
                return session
            if session:
                del self._sessions[session_id]
                self._profile_locks = {
                    k: v for k, v in self._profile_locks.items() if v != session_id
                }
        return None

    def destroy_session(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                self._profile_locks = {
                    k: v for k, v in self._profile_locks.items() if v != session_id
                }
                logger.info(f"Destroyed session {session_id[:8]}...")
                return True
        return False

    def get_active_session_for_profile(self, profile_id: str) -> Session | None:
        with self._lock:
            session_id = self._profile_locks.get(profile_id)
            if session_id:
                session = self._sessions.get(session_id)
                if session and not session.is_expired:
                    return session
        return None

    def list_sessions(self) -> list[Session]:
        with self._lock:
            self._cleanup_expired()
            return list(self._sessions.values())

    def _cleanup_expired(self) -> None:
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        for sid in expired:
            session = self._sessions.pop(sid, None)
            if session:
                self._profile_locks = {
                    k: v for k, v in self._profile_locks.items() if v != sid
                }

    def cleanup(self) -> int:
        with self._lock:
            before = len(self._sessions)
            self._cleanup_expired()
            return before - len(self._sessions)

    @property
    def stats(self) -> dict[str, Any]:
        with self._lock:
            self._cleanup_expired()
            return {
                "active_sessions": len(self._sessions),
                "max_sessions": MAX_SESSIONS,
                "profiles_in_use": len(self._profile_locks),
                "sessions": [s.to_dict() for s in self._sessions.values()],
            }


class AuditLog:
    """Simple audit log for profile access and changes."""

    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max_entries = max_entries
        self._lock = threading.Lock()

    def log(
        self,
        action: str,
        profile_id: str,
        session_id: str | None = None,
        details: dict | None = None,
    ) -> None:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "profile_id": profile_id,
            "session_id": session_id,
            "details": details or {},
        }
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries:]

    def get_entries(
        self,
        profile_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with self._lock:
            entries = self._entries
            if profile_id:
                entries = [e for e in entries if e["profile_id"] == profile_id]
            return list(reversed(entries[-limit:]))


_session_manager: SessionManager | None = None
_audit_log: AuditLog | None = None


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def get_audit_log() -> AuditLog:
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log


def register_routes(app: Any) -> None:

    sm = get_session_manager()
    audit = get_audit_log()

    @app.post("/api/sessions")
    async def api_create_session(request: Request):
        data = await request.json()
        profile_id = data.get("profile_id", "")
        if not profile_id:
            return JSONResponse({"error": "profile_id required"}, status_code=400)

        from profile_manager import get as pm_get
        pm = pm_get()
        if profile_id not in pm.list_profiles():
            return JSONResponse({"error": "Profile not found"}, status_code=404)

        session = sm.create_session(profile_id, metadata=data.get("metadata"))
        audit.log("session_create", profile_id, session.session_id)
        return {"session_id": session.session_id, "profile_id": profile_id}

    @app.get("/api/sessions")
    async def api_list_sessions():
        sessions = sm.list_sessions()
        return {
            "sessions": [s.to_dict() for s in sessions],
            "stats": sm.stats,
        }

    @app.delete("/api/sessions/{session_id}")
    async def api_destroy_session(session_id: str):
        session = sm.get_session(session_id)
        if not session:
            return JSONResponse({"error": "Session not found"}, status_code=404)

        profile_id = session.profile_id
        sm.destroy_session(session_id)
        audit.log("session_destroy", profile_id, session_id)
        return {"success": True}

    @app.get("/api/sessions/{session_id}")
    async def api_get_session(session_id: str):
        session = sm.get_session(session_id)
        if not session:
            return JSONResponse({"error": "Session not found or expired"}, status_code=404)
        return session.to_dict()

    @app.get("/api/audit")
    async def api_audit_log(request: Request):
        profile_id = request.query_params.get("profile_id")
        limit = int(request.query_params.get("limit", "50"))
        entries = audit.get_entries(profile_id=profile_id, limit=limit)
        return {"entries": entries, "total": len(audit._entries)}
