"""Register the AI Coach memory + rider-context routes on the FastAPI app.

Kept in its own module so app.py stays the single composition root and the
AI Coach feature is self-contained (mirrors the pcc_routes_v2 / missing_routes
pattern already used by CPSL).
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


def register_ai_memory_routes(app):
    """Attach /api/ai/memory, /api/ai/memory (DELETE) and
    /api/ai/rider-context to ``app``."""

    @app.get("/api/ai/memory")
    async def api_ai_memory(profile_id: str = "default"):
        """Return the rider's persisted AI Coach memory (most recent first).

        Works independently of the LLM provider so the rider's memory is
        always available for analytics/UI even before an API key is set.
        """
        try:
            from ai_coach.memory import get_recent_memory
            return {"ok": True, "profile_id": profile_id,
                    "memory": get_recent_memory(profile_id, limit=50)}
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)})

    @app.delete("/api/ai/memory")
    async def api_ai_memory_clear(profile_id: str = "default"):
        """Clear the rider's AI Coach memory."""
        try:
            from ai_coach.memory import clear_memory
            removed = clear_memory(profile_id)
            return {"ok": True, "profile_id": profile_id, "removed": removed}
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)})

    @app.get("/api/ai/rider-context")
    async def api_ai_rider_context(profile_id: str = "default"):
        """Return the grounded rider-context block used to ground the coach.

        Pure data aggregation — no LLM call — so it is always available.
        """
        try:
            from ai_coach.memory import build_rider_context, rider_context_prompt
            return {"ok": True, "profile_id": profile_id,
                    "context": build_rider_context(profile_id),
                    "prompt_block": rider_context_prompt(profile_id)}
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)})
