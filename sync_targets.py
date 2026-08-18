"""
Sync targets module for Cycling Performance Studio Lab.

Pluggable sync target architecture enabling multiple data destinations.
Each target implements the SyncTarget base class with standardized interfaces.
"""

from __future__ import annotations

import abc
import base64
import json
import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Base class for all sync targets
# ---------------------------------------------------------------------------

class SyncTarget(abc.ABC):
    """Abstract base class for sync targets."""

    key: str
    display_name: str
    can_write: bool = False

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Check if this target has required credentials/config."""
        raise NotImplementedError

    @abc.abstractmethod
    def push_activity(self, activity_data: dict) -> bool:
        """Push a single activity to the target."""
        raise NotImplementedError

    @abc.abstractmethod
    def pull_wellness(self, since: Optional[datetime] = None) -> list[dict]:
        """Pull wellness data from the target."""
        raise NotImplementedError

    @abc.abstractmethod
    def push_wellness(self, data: dict) -> bool:
        """Push wellness data to the target."""
        raise NotImplementedError

    @abc.abstractmethod
    def stop_sync(self) -> None:
        """Stop any running sync process for this target."""
        raise NotImplementedError

    @abc.abstractmethod
    def restart_sync(self) -> None:
        """Restart sync process for this target."""
        raise NotImplementedError

    def pull_activities(self, since: Optional[datetime] = None) -> list[dict]:
        """Pull activities (default: not implemented, override if supported)."""
        return []


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, SyncTarget] = {}

def register_target(target: SyncTarget) -> None:
    """Register a sync target in the global registry."""
    _REGISTRY[target.key] = target
    logger.info(f"Registered sync target: {target.key} ({target.display_name})")


def get_target(key: str) -> Optional[SyncTarget]:
    """Get a sync target by key from the registry."""
    return _REGISTRY.get(key)


def list_targets() -> list[dict]:
    """Return registry entries with status."""
    result = []
    for key, target in _REGISTRY.items():
        result.append(
            {
                "key": target.key,
                "display_name": target.display_name,
                "can_write": target.can_write,
                "is_configured": target.is_configured(),
            }
        )
    return result


def connected_targets() -> list[str]:
    """Return list of keys for targets that are currently configured."""
    return [t["key"] for t in list_targets() if t["is_configured"]]


# ---------------------------------------------------------------------------
# Default target: Intervals.icu
# ---------------------------------------------------------------------------

class IntervalsIcuTarget(SyncTarget):
    """Sync target for Intervals.icu API."""

    key = "intervals_icu"
    display_name = "Intervals.icu"
    can_write = True

    def __init__(self) -> None:
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._expires_at: Optional[datetime] = None
        self._patient_id: str = ""
        self._http: Optional[httpx.AsyncClient] = None

    def _load_credentials(self) -> None:
        """Load credentials from active profile's .env."""
        from profile_manager import get as pm_get
        pm = pm_get()
        env = pm.active_env()
        self._access_token = env.get("ICU_ACCESS_TOKEN", "")
        self._refresh_token = env.get("ICU_REFRESH_TOKEN", "")
        self._expires_at = (
            datetime.fromisoformat(env["ICU_EXPIRES_AT"])
            if env.get("ICU_EXPIRES_AT")
            else None
        )
        self._patient_id = env.get("ICU_ATHLETE_ID", "")

    def _http_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                base_url="https://intervals.icu/api/v1",
                timeout=30.0,
                follow_redirects=True,
            )
        return self._http

    async def _ensure_auth(self) -> bool:
        """Ensure we have a valid access token, refresh if needed."""
        if not self._access_token:
            return False

        # If token expired or near expiry, try refresh
        if self._expires_at and datetime.utcnow() >= self._expires_at - timedelta(minutes=5):
            # Attempt refresh
            http = self._http_client()
            try:
                resp = await http.post(
                    "/oauth/token",
                    data={
                        "client_id": "511",
                        "client_secret": "",  # from config/env
                        "grant_type": "refresh_token",
                        "refresh_token": self._refresh_token,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._access_token = data["access_token"]
                    self._refresh_token = data.get("refresh_token", self._refresh_token)
                    # Set new expiry
                    self._expires_at = datetime.utcnow() + timedelta(
                        seconds=data.get("expires_in", 3600)
                    )
                    # Save back to .env
                    # pm.save_env(...)  # delegate to profile manager
                    return True
            except Exception as e:
                logger.warning(f"ICU token refresh failed: {e}")
        
        return True  # assume valid if no refresh needed or attempted

    def is_configured(self) -> bool:
        """Check if Intervals.icu has required credentials."""
        return bool(self._patient_id and self._access_token)

    async def push_activity(self, activity_data: dict) -> bool:
        """Push a single activity to Intervals.icu."""
        await self._ensure_auth()
        http = self._http_client()

        try:
            # Endpoint varies by activity type
            endpoint = "/activities"
            resp = await http.post(endpoint, json=activity_data)
            return resp.status_code in (200, 201)
        except Exception as e:
            _log_error("E_SYNC_BLOCKING_SLOW", e)  # generic sync error
            return False

    async def pull_wellness(self, since: Optional[datetime] = None) -> list[dict]:
        """Pull wellness data from Intervals.icu."""
        await self._ensure_auth()
        http = self._http_client()

        params = {}
        if since:
            params["since"] = int(since.timestamp())

        try:
            resp = await http.get("/wellness", params=params)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception as e:
            logger.warning(f"ICU wellness pull failed: {e}")
            return []

    async def push_wellness(self, data: dict) -> bool:
        """Push wellness data to Intervals.icu."""
        await self._ensure_auth()
        http = self._http_client()

        try:
            endpoint = "/wellness"
            resp = await http.post(endpoint, json=data)
            return resp.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"ICU wellness push failed: {e}")
            return False

    def stop_sync(self) -> None:
        """Stop Intervals.icu sync process."""
        if self._http and not self._http.is_closed:
            asyncio.get_event_loop().create_task(self._http.aclose())
        logger.info("Intervals.icu sync stopped")

    def restart_sync(self) -> None:
        """Restart Intervals.icu sync process."""
        logger.info("Intervals.icu sync restart scheduled")
        # Would trigger async pull loop here


# Auto-register the default target
register_target(IntervalsIcuTarget())

# Also register any additional targets that are importable
# from sync_targets_additional import register_additional_targets()
# register_additional_targets()