"""Database module for Cycling Performance Studio Lab.

Minimal sync-gate and write-lock layer for atomic profile operations.
Provides sync_write_gate context manager used by power_curve.py.
"""

from __future__ import annotations

import logging
import threading
import tempfile
import os
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_write_lock = threading.Lock()


@contextmanager
def sync_write_gate(profile_id: str, timeout: float = 10.0):
    """Context manager for atomic gated writes during sync operations."""
    acquired = _write_lock.acquire(timeout=timeout)
    if not acquired:
        logger.warning(f"Sync write gate timeout for profile {profile_id}")
        raise TimeoutError(f"Could not acquire write lock for profile {profile_id}")
    try:
        yield
    finally:
        _write_lock.release()


def atomic_write_json(path: Path, data: Any) -> None:
    """Write JSON atomically using tempfile + rename."""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def read_json(path: Path, default: Any = None) -> Any:
    """Read JSON file safely, returning default on error."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to read {path}: {e}")
        return default


class _BackfillLock:
    def acquire(self, profile_id: str, timeout: float = 5.0) -> bool:
        return True

    def release(self, profile_id: str) -> None:
        pass


backfill_lock = _BackfillLock()
