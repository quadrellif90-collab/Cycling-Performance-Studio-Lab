"""Persistent AI Coach memory + rider-context RAG for CPSL.

This module gives the AI Coach a real memory across sessions and grounds its
answers in the rider's OWN data instead of generic LLM knowledge.

Storage: a single SQLite DB at ``<DATA_DIR>/ai_memory.db`` (per-install, not
per-profile at the file level — rows are keyed by ``profile_id`` so multiple
profiles are isolated within one store).

Design notes
------------
* No new dependencies: stdlib ``sqlite3`` + ``json`` only.
* Memory is append-only with soft semantics: ``add_memory`` stores coach
  replies and user corrections; ``get_relevant_memory`` returns the most
  recent N entries plus any tagged with the current topic.
* ``build_rider_context`` pulls from the live profile/analytics so the prompt
  always reflects the latest FTP, HRV trend, recent rides and plan gaps.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# DATA_DIR is imported lazily to avoid a circular import at module load.
_DATA_DIR = None


def _db_path() -> Path:
    global _DATA_DIR
    if _DATA_DIR is None:
        try:
            from user_home import cpsl_home
            _DATA_DIR = cpsl_home()
        except Exception:
            _DATA_DIR = Path.home() / ".cpsl"
    return Path(_DATA_DIR) / "ai_memory.db"


def _conn() -> sqlite3.Connection:
    p = _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(p))
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id TEXT NOT NULL,
            role TEXT NOT NULL,            -- 'user' | 'coach' | 'system'
            content TEXT NOT NULL,
            tags TEXT DEFAULT '[]',        -- JSON list of topic tags
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_ai_memory_profile ON ai_memory(profile_id)"
    )
    c.commit()
    return c


def add_memory(
    profile_id: str,
    role: str,
    content: str,
    tags: Optional[list[str]] = None,
) -> int:
    """Store one memory entry. Returns the new row id."""
    c = _conn()
    try:
        cur = c.execute(
            "INSERT INTO ai_memory (profile_id, role, content, tags, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                profile_id,
                role,
                content,
                json.dumps(tags or []),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()


def get_recent_memory(profile_id: str, limit: int = 12) -> list[dict]:
    """Most recent memories for a profile (oldest-last ordering)."""
    c = _conn()
    try:
        rows = c.execute(
            "SELECT role, content, tags, created_at FROM ai_memory "
            "WHERE profile_id=? ORDER BY id DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
    finally:
        c.close()
    out = []
    for role, content, tags, created_at in reversed(rows):
        try:
            tag_list = json.loads(tags)
        except (TypeError, ValueError):
            tag_list = []
        out.append(
            {"role": role, "content": content, "tags": tag_list, "created_at": created_at}
        )
    return out


def search_memory(profile_id: str, keyword: str, limit: int = 6) -> list[dict]:
    """Keyword search across a profile's memory (case-insensitive)."""
    c = _conn()
    try:
        rows = c.execute(
            "SELECT role, content, tags, created_at FROM ai_memory "
            "WHERE profile_id=? AND content LIKE ? ORDER BY id DESC LIMIT ?",
            (profile_id, f"%{keyword}%", limit),
        ).fetchall()
    finally:
        c.close()
    out = []
    for role, content, tags, created_at in reversed(rows):
        try:
            tag_list = json.loads(tags)
        except (TypeError, ValueError):
            tag_list = []
        out.append(
            {"role": role, "content": content, "tags": tag_list, "created_at": created_at}
        )
    return out


def clear_memory(profile_id: str) -> int:
    """Delete all memory for a profile. Returns rows removed."""
    c = _conn()
    try:
        cur = c.execute("DELETE FROM ai_memory WHERE profile_id=?", (profile_id,))
        c.commit()
        return cur.rowcount
    finally:
        c.close()


# ──────────────────────────────────────────────────────────────────────────
# Rider-context RAG — pulls the rider's REAL data into the prompt
# ──────────────────────────────────────────────────────────────────────────

def build_rider_context(profile_id: Optional[str] = None) -> dict:
    """Collect the rider's current analytics into a compact context dict.

    Best-effort: any module that fails to import or returns nothing is simply
    omitted, so the coach still works with partial data (e.g. fresh install).
    """
    ctx: dict = {"profile_id": profile_id or "default"}
    try:
        from profile_manager import ProfileManager
        pm = ProfileManager.get()
        prof = pm.active_profile or {}
        ctx["athlete"] = {
            "ftp": prof.get("ftp"),
            "weight": prof.get("weight"),
            "lthr": prof.get("lthr"),
            "max_hr": prof.get("max_hr"),
            "age": prof.get("age"),
        }
    except Exception:
        pass

    # Recent rides / plan gaps via the existing analytics helpers
    try:
        from training_planner import detect_plan_gaps
        gaps = detect_plan_gaps()
        if gaps:
            ctx["plan_gaps"] = gaps[:5]
    except Exception:
        pass

    try:
        from hrv_engine import get_recent_hrv_trend
        trend = get_recent_hrv_trend(days=14)
        if trend:
            ctx["hrv_trend_14d"] = trend
    except Exception:
        pass

    try:
        from phenotype import classify_phenotype
        pheno = classify_phenotype()
        if pheno:
            ctx["phenotype"] = pheno
    except Exception:
        pass

    try:
        from durability_score import compute_durability_score
        dur = compute_durability_score()
        if dur:
            ctx["durability"] = dur
    except Exception:
        pass

    return ctx


def rider_context_prompt(profile_id: Optional[str] = None) -> str:
    """Render the rider context as a compact text block for the LLM prompt."""
    ctx = build_rider_context(profile_id)
    parts = ["[RIDER CONTEXT — ground every answer in THIS data]"]
    if ctx.get("athlete"):
        a = ctx["athlete"]
        parts.append(
            f"Athlete: FTP={a.get('ftp')}W, weight={a.get('weight')}kg, "
            f"LTHR={a.get('lthr')}bpm, maxHR={a.get('max_hr')}bpm, age={a.get('age')}"
        )
    if ctx.get("plan_gaps"):
        parts.append("Plan gaps: " + "; ".join(str(g) for g in ctx["plan_gaps"]))
    if ctx.get("hrv_trend_14d"):
        parts.append(f"HRV trend (14d): {ctx['hrv_trend_14d']}")
    if ctx.get("phenotype"):
        parts.append(f"Phenotype: {ctx['phenotype']}")
    if ctx.get("durability"):
        parts.append(f"Durability score: {ctx['durability']}")
    return "\n".join(parts)
