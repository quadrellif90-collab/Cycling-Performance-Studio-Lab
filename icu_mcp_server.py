"""CPSL MCP Server (v1.3.0) — expose CPSL/ICU data to any MCP-capable LLM client.

Implements a small Model Context Protocol server over stdio using the ``mcp``
package. Tools exposed:

- ``wellness_recent``      — last N wellness records (HRV, sleep, CTL/ATL/TSB)
- ``rider_context``        — the AI Coach RAG context (FTP, weight, HRV trend…)
- ``coach_memory_search``  — semantic-ish search over the coach memory store
- ``activities_recent``    — recent activities summary
- ``plan_preview``         — current training plan preview

Run standalone:
    python icu_mcp_server.py

Or from within the app (the /api/ai/mcp/status endpoint reports availability).
"""
from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger("cpsl.mcp")

SERVER_NAME = "cpsl-mcp"
SERVER_VERSION = "1.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# Tool implementations (plain functions — also callable without MCP)
# ─────────────────────────────────────────────────────────────────────────────

def tool_wellness_recent(days: int = 14) -> dict:
    from ride_storage import load_recent_wellness
    recs = load_recent_wellness(days=min(int(days), 180))
    out = []
    for r in recs[:days]:
        out.append({
            "date": r.get("id"),
            "hrv": r.get("hrv") or r.get("hrvSDNN"),
            "sleepSeconds": r.get("sleepSeconds"),
            "weightKg": r.get("weightKg"),
            "ctl": r.get("ctl"), "atl": r.get("atl"),
            "tsb": (r.get("ctl") - r.get("atl")) if (r.get("ctl") is not None and r.get("atl") is not None) else None,
            "restingHr": r.get("restingHr"),
        })
    return {"ok": True, "count": len(out), "records": out}


def tool_rider_context() -> dict:
    from ai_coach.memory import build_rider_context
    ctx = build_rider_context()
    return {"ok": True, "context": ctx}


def tool_coach_memory_search(keyword: str = "", limit: int = 8) -> dict:
    import ai_coach.memory as mem
    fn = getattr(mem, "search_memory", None)
    if not fn:
        return {"ok": False, "error": "search_memory unavailable"}
    rows = fn(profile_id="default", keyword=keyword or "", limit=int(limit))
    return {"ok": True, "count": len(rows), "entries": rows}


def tool_activities_recent(days: int = 30, limit: int = 10) -> dict:
    from datetime import datetime, timedelta
    try:
        from ride_storage import list_rides
        rides = list_rides() or []
        cutoff = (datetime.now() - timedelta(days=int(days))).isoformat()
        out = []
        for r in rides:
            started = (r.get("started_at") or "")
            if started and started >= cutoff:
                out.append({
                    "date": started[:10],
                    "name": (r.get("name") or r.get("summary", {}).get("name") or "")[:60],
                    "tss": r.get("tss") or (r.get("summary") or {}).get("tss"),
                })
            if len(out) >= int(limit):
                break
        return {"ok": True, "count": len(out), "activities": out}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def tool_plan_preview() -> dict:
    try:
        from training_planner import TrainingPlanner
        tp = TrainingPlanner()
        plan = getattr(tp, "current_plan", None)
        if plan is None and hasattr(tp, "load_plan"):
            plan = tp.load_plan()
        if plan is None:
            return {"ok": False, "error": "no saved plan"}
        weeks = plan.get("weeks", []) if isinstance(plan, dict) else []
        return {"ok": True, "weeks": len(weeks),
                "preview": [{k: w.get(k) for k in ("week", "label", "total_tss", "hours")} for w in weeks[:4]]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


TOOLS = {
    "wellness_recent": (tool_wellness_recent, "Ultimi record wellness (HRV, sonno, peso, CTL/ATL/TSB). Args: days=14"),
    "rider_context": (tool_rider_context, "Contesto atleta per il coach RAG (FTP, peso, HRV trend, RHR). Nessun arg."),
    "coach_memory_search": (tool_coach_memory_search, "Cerca nella memoria del coach. Args: keyword='', limit=8"),
    "activities_recent": (tool_activities_recent, "Attività recenti. Args: days=30, limit=10"),
    "plan_preview": (tool_plan_preview, "Anteprima piano allenamento salvato. Nessun arg."),
}


# ─────────────────────────────────────────────────────────────────────────────
# stdlib fallback JSON-RPC loop (works even without the mcp package)
# ─────────────────────────────────────────────────────────────────────────────

def run_stdio_loop() -> None:
    """Minimal JSON-RPC 2.0 loop over stdin/stdout (MCP-compatible subset).

    Supports initialize, tools/list, tools/call. One JSON message per line.
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}
        if method == "initialize":
            resp = {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }}
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": rid, "result": {"tools": [
                {"name": n, "description": d, "inputSchema": {"type": "object"}}
                for n, (_, d) in TOOLS.items()
            ]}}
        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments") or {}
            fn = TOOLS.get(name, (None, None))[0]
            if not fn:
                resp = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
            else:
                try:
                    result = fn(**args)
                    resp = {"jsonrpc": "2.0", "id": rid, "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}}
                except Exception as e:
                    resp = {"jsonrpc": "2.0", "id": rid, "result": {
                        "content": [{"type": "text", "text": f"error: {e}"}], "isError": True}}
        else:
            resp = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {method}"}}
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    import sys
    from datetime import datetime, timedelta
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    run_stdio_loop()
