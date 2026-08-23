"""
PCC Routes v2 — extracted from PCC/app.py for CPSL.

These are routes that exist in PCC but NOT in CPSL.
Replace any ".domestique" paths with ".cpsl" in the extracted code.

Run: included in app.py via include_router or copy-paste
"""

import collections
import functools
import hashlib
import json
import os
import re
import sys
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from fastapi import FastAPI, File, Form, Request, Query, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse, PlainTextResponse, Response
from starlette.background import BackgroundTask

# ═══════════════════════════════════════════════════════════════════════════════
# v1.4.6 FIX (F821): questo modulo è stato estratto da app.py e diversi helper
# referenziano ancora global di app. Li dichiaro qui come placeholder (None) —
# ruff/mypy vedono nomi definiti — e register_pcc_routes() li RILEGA dal modulo
# 'app' già importato (sovrascrivendo i placeholder) prima che qualunque route
# venga eseguita.
# ═══════════════════════════════════════════════════════════════════════════════
cached = None                      # functools decorator di app
clear_cache = None                 # invalidazione cache ride
DATA_DIR = None                    # Path dati utente
ROUTE_PROFILES_INDEX = None        # Path profiles_indexed.json
_compute_local_atl = None          # ATL locale (7d)
_sync_icu_activities = None        # sync Intervals.icu
_setup_marker = None               # marker onboarding completato
_get_json_body = None              # parse body JSON async
SETUP_LIMITS: dict = {}            # range validazione campi atleta
api_activities = None              # GET archivio attività
api_readiness_composite = None     # readiness composita
api_update_check = None            # controllo aggiornamenti
db = None                          # ActivityDatabase
config = None                      # config globale CPSLConfig
tp = None                          # training_planner

# Vocabolario locale di validazione (non esiste in app; usato da /api/athlete)
_SETUP_ENUM_LOCAL: dict = {"sex": {"m", "f", "other"}}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (dependencies for the routes below)
# ═══════════════════════════════════════════════════════════════════════════════

def _plan_dir() -> Path:
    """v1.3.1 FIX: this helper was referenced but never defined here (NameError
    on /api/onboarding/status and 3 other routes). Mirrors app.py::_plan_dir:
    profile-aware plans dir via training_planner.PLAN_DIR, fallback to
    ~/.cpsl/plans. Local copy avoids a circular import from app."""
    try:
        import training_planner as _tp
        d = getattr(_tp, 'PLAN_DIR', None)
        if d:
            d = Path(d)
            d.mkdir(parents=True, exist_ok=True)
            return d
    except Exception:
        pass
    try:
        from user_home import cpsl_home
        d = cpsl_home() / "plans"
    except Exception:
        d = Path.home() / ".cpsl" / "plans"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _local_training_load() -> dict:
    """v4.4.2 — single helper that returns CTL/ATL/TSB derived from the
    local rides archive.

    Output shape: ``{ctl, atl, tsb, source}`` where ``source`` is always
    "local" (callers compose with ICU values to produce "icu"/"mixed"/"local").
    Any of ctl/atl/tsb may be None if local rides have no TSS values at all.
    """
    try:
        import ride_storage as _rs
        ctl = _rs.compute_local_ctl()
    except Exception:
        ctl = None
    atl = _compute_local_atl()
    tsb = None
    if ctl is not None and atl is not None:
        tsb = round(ctl - atl, 1)
    return {"ctl": ctl, "atl": atl, "tsb": tsb, "source": "local"}


def _merge_training_load(icu_t: dict | None) -> dict:
    """v4.4.2 — merge ICU-derived training metrics with local fallback.

    Rule: prefer ICU value when present; fall back to local on a per-field
    basis. Source label:
      - "icu" if all ICU fields present
      - "local" if no ICU fields and local fallback used
      - "mixed" otherwise
    """
    icu = icu_t or {}
    local = _local_training_load()
    icu_ctl = icu.get("ctl")
    icu_atl = icu.get("atl")
    icu_tsb = icu.get("tsb")
    out = {
        "ctl": icu_ctl if icu_ctl is not None else local["ctl"],
        "atl": icu_atl if icu_atl is not None else local["atl"],
        "tsb": icu_tsb if icu_tsb is not None else local["tsb"],
        "acwr": icu.get("acwr"),
        "ramp_rate": icu.get("ramp_rate"),
        "monotony": icu.get("monotony"),
        "strain": icu.get("strain"),
    }
    icu_count = sum(1 for v in (icu_ctl, icu_atl, icu_tsb) if v is not None)
    if icu_count == 3:
        out["source"] = "icu"
    elif icu_count == 0:
        out["source"] = "local" if any(v is not None for v in (out["ctl"], out["atl"], out["tsb"])) else "none"
    else:
        out["source"] = "mixed"
    return out


def _icu_wellness_auth():
    """Returns the Authorization header from training.py (Bearer or Basic base64),
    or None if ICU is not configured.
    """
    try:
        import training as _training
        return _training._auth_header()
    except Exception:
        return None


def _icu_wellness_sync_state_path() -> Path | None:
    """Separate marker for last wellness sync.

    Per-profile ``<profile>/wellness/.last_sync_at`` via
    ride_storage._wellness_dir."""
    try:
        import ride_storage as _rs_m7
        marker = _rs_m7._wellness_dir() / ".last_sync_at"
    except Exception:
        return None
    return marker


def _write_last_sync_at(ts: float) -> None:
    p = _icu_sync_state_path()
    if p is None:
        return
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(ts), encoding="utf-8")
    except OSError:
        pass


def _load_all_rides_safe() -> list[dict]:
    """Defensive wrapper around ride_storage.load_all_rides().

    Memoised via the shared 5-min cache so a home-page load pays it once.
    """
    return cached("all_rides", _load_all_rides_uncached)


def _load_all_rides_uncached() -> list[dict]:
    try:
        import ride_storage as _rs
        return _rs.load_all_rides()
    except Exception:
        return []


def _ride_started_local_iso_date(ride: dict) -> str | None:
    """Best-effort local-TZ ISO date from ride.started_at."""
    started = ride.get("started_at") or ""
    if not started:
        return None
    try:
        s = started.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            return started[:10]
        return dt.astimezone().date().isoformat()
    except (TypeError, ValueError):
        return started[:10] if len(started) >= 10 else None


def _route_profile_points(lat_lon_grade: list) -> list[dict]:
    """Convert [[lat,lon,grade],...] to [{d, e, g},...] for elevProfile rendering."""
    from geodesy import haversine
    if not lat_lon_grade or len(lat_lon_grade) < 2:
        return []

    points = []
    cum_dist_km = 0.0
    cum_ele = 0.0
    for i, pt in enumerate(lat_lon_grade):
        if len(pt) < 3:
            continue
        lat, lon, grade = pt[0], pt[1], pt[2]
        grade = max(-45, min(45, grade))
        if i > 0:
            prev = lat_lon_grade[i - 1]
            d_m = haversine((prev[0], prev[1]), (lat, lon))
            d_km = d_m / 1000.0
            cum_dist_km += d_km
            cum_ele += d_m * grade / 100.0
        points.append({"d": round(cum_dist_km, 3), "e": round(cum_ele, 1), "g": round(grade, 1)})

    if len(points) > 200:
        step = max(1, len(points) // 200)
        sampled = [points[i] for i in range(0, len(points), step)]
        if sampled[-1] != points[-1]:
            sampled.append(points[-1])
        return sampled
    return points


def _load_route_index() -> dict:
    """Load compact pre-indexed virtual route profiles (~1MB, loaded once)."""
    return cached("route_index", lambda: (
        json.loads(ROUTE_PROFILES_INDEX.read_text(encoding="utf-8"))
        if ROUTE_PROFILES_INDEX.exists() else {}
    ), ttl=3600)


def _load_route_detail(url: str) -> dict | None:
    """Load full route data from individual file (for detail modal)."""
    if not url:
        return None
    url = url.split("?", 1)[0].split("#", 1)[0].strip()
    clean = url.replace("..", "").replace("\\", "/").strip("/")
    parts = [p for p in clean.split("/") if p]
    if not parts:
        return None

    last = parts[-1]
    last_stem = last.rsplit(".", 1)[0] if "." in last else last

    candidates: list[tuple[str, str]] = []

    if "climb-portal" in parts:
        candidates.append(("climb-portal", last_stem))

    if len(parts) >= 2:
        candidates.append((parts[-2], last_stem))

    if len(parts) >= 3:
        candidates.append((parts[-3], last_stem))

    candidates.append(("_", last_stem))

    idx = _load_route_index()
    for world, slug in candidates:
        key = f"{world}/{slug}"
        if key in idx:
            return idx[key]
        # Try climbing-portal prefix
        key2 = f"climbing-portal/{slug}"
        if key2 in idx:
            return idx[key2]

    return None


def _read_update_check_cache():
    p = _update_check_cache_path()
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_update_check_cache(payload):
    p = _update_check_cache_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        body = dict(payload)
        body["cache_written_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p.write_text(json.dumps(body, indent=2), encoding="utf-8")
    except Exception:
        pass


def _cache_is_fresh(cache, now):
    if not cache:
        return False
    written = cache.get("cache_written_at")
    if not written:
        return False
    try:
        age = now - datetime.fromisoformat(written.replace("Z", "+00:00"))
        return age.total_seconds() < _UPDATE_CHECK_CACHE_TTL_S
    except Exception:
        return False


def _update_check_cache_path() -> Path:
    return DATA_DIR / "update_check_cache.json"


_UPDATE_CHECK_CACHE_TTL_S = 6 * 60 * 60
_GITHUB_RELEASES_LATEST_URL = "https://api.github.com/repos/quadrellif90-collab/pcc-cycling-coach/releases/latest"
_RELEASE_BODY_MAX_CHARS = 8192
_RELEASE_BODY_TRUNCATION_SUFFIX = "\n\n… (full release notes on GitHub)"


def _select_platform_asset(assets, plat):
    if not isinstance(assets, list):
        return None, None

    def _name(a):
        return (a.get("name") or "") if isinstance(a, dict) else ""

    def _url(a):
        return (a.get("browser_download_url") or "") if isinstance(a, dict) else ""

    if plat == "darwin":
        dmgs = [a for a in assets if _name(a).lower().endswith(".dmg")]
        if not dmgs:
            return None, None
        import re as _re
        _ver = _re.compile(r"[-_ ].*\d+\.\d+")
        canonical = [a for a in dmgs
                     if _name(a) in ("PCC.dmg", "pcc.dmg", "Domestique.dmg", "domestique.dmg")
                     or not _ver.search(_name(a)[:-4])]
        chosen = canonical[0] if canonical else dmgs[0]
        return _url(chosen) or None, _name(chosen) or None

    if plat == "win32":
        exes = [a for a in assets if _name(a).lower().endswith(".exe")]
        preferred = [a for a in exes if _name(a).lower().startswith("pcc-setup")]
        if preferred:
            return _url(preferred[0]) or None, _name(preferred[0]) or None
        if exes:
            return _url(exes[0]) or None, _name(exes[0]) or None
        zips = [a for a in assets if _name(a).lower().endswith(".zip")]
        if zips:
            return _url(zips[0]) or None, _name(zips[0]) or None
        return None, None

    return None, None


def _kick_lazy_icu_sync(force_if_today_missing: bool = False) -> bool:
    """Fire-and-forget lazy ICU sync kick — best-effort, never blocks."""
    try:
        if not _icu_credentials_present():
            return False
        last = _read_last_sync_at()
        if last is not None and (time.time() - last) < 3600:
            return False
        import threading
        def _bg():
            try:
                _sync_icu_activities(force=force_if_today_missing)
            except Exception:
                pass
        threading.Thread(target=_bg, daemon=True, name="lazy-icu-sync").start()
        return True
    except Exception:
        return False


def _icu_credentials_present() -> bool:
    """True iff ICU is configured — OAuth OR legacy Basic auth."""
    if getattr(config, "ICU_ACCESS_TOKEN", None):
        return True
    return bool(
        getattr(config, "ICU_ATHLETE_ID", None)
        and getattr(config, "ICU_API_KEY", None)
    )


def _read_last_sync_at() -> float | None:
    p = _icu_sync_state_path()
    if p is None or not p.exists():
        return None
    try:
        return float(p.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _icu_sync_state_path() -> Path | None:
    """Per-profile sync state path."""
    try:
        import ride_storage as _rs
        return _rs._rides_dir() / ".last_sync_at"
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — extracted from PCC/app.py
# ═══════════════════════════════════════════════════════════════════════════════

# ─── 20. POST /api/activity/rpe ──────────────────────────────────────────────
# @app.post("/api/activity/rpe")
async def api_activity_rpe(request: Request):
    try:
        body = await request.json()
        ride_id = body.get("ride_id") or ""
        rpe = float(body.get("rpe"))
        note = body.get("note", "") or ""
        if not ride_id:
            return JSONResponse({"error": "ride_id required"}, 400)
        from training_planner import PLAN_DIR
        from activity_insights import save_rpe
        prof_dir = Path(PLAN_DIR)
        entry = save_rpe(prof_dir, ride_id, rpe, note)
        return {"ok": True, "ride_id": ride_id, "rpe": entry["rpe"]}
    except (ValueError, TypeError) as e:
        return JSONResponse({"error": str(e)}, 400)
    except Exception as e:
        return JSONResponse({"detail": "rpe failed"}, 500)


# ─── 1. GET /api/activity-insights ───────────────────────────────────────────
# @app.get("/api/activity-insights")
def api_activity_insights(days: int = Query(14, ge=1, le=365)):
    try:
        from training_planner import PLAN_DIR
        from activity_insights import build_activity_insights
        from profile_manager import ProfileManager
        pm = ProfileManager.get()
        prof_dir = Path(PLAN_DIR)
        ftp = float(pm.ftp) if getattr(pm, "ftp", None) else None
        activities = api_activities() if callable(api_activities) else []
        if not isinstance(activities, list):
            activities = []
        plan_path = _plan_dir() / "current_plan.json"
        plan = {}
        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
            except Exception:
                plan = {}
        rows = build_activity_insights(activities, plan, prof_dir, ftp, days=days)
        unplanned = [r for r in rows if r.get("unplanned")]
        return {
            "days": days,
            "activities": rows,
            "n_unplanned": len(unplanned),
            "method": "IF-band classification + rematch_week (single engine)",
        }
    except Exception as e:
        return {"error": str(e), "activities": [], "n_unplanned": 0}


# ─── 2. GET /api/custom-charts ───────────────────────────────────────────────
# @app.get("/api/custom-charts")
def api_custom_charts_list():
    from custom_charts import load_charts
    return {"charts": load_charts()}


# ─── 4. POST /api/custom-charts ──────────────────────────────────────────────
# @app.post("/api/custom-charts")
async def api_custom_charts_save(request: Request):
    try:
        body = await request.json()
        from custom_charts import upsert_chart
        rec = upsert_chart(body)
        return {"ok": True, **rec}
    except (ValueError, TypeError) as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ─── 5. DELETE /api/custom-charts/{chart_id} ─────────────────────────────────
# @app.delete("/api/custom-charts/{chart_id}")
def api_custom_charts_delete(chart_id: str):
    from custom_charts import delete_chart
    ok = delete_chart(chart_id)
    return {"ok": ok}


# ─── 3. GET /api/custom-charts/data/{chart_id} ───────────────────────────────
# @app.get("/api/custom-charts/data/{chart_id}")
def api_custom_charts_data(chart_id: str, days: int = Query(365, ge=1, le=3650)):
    try:
        from custom_charts import load_charts, compute_series
        defs = load_charts()
        defn = next((c for c in defs if c.get("id") == chart_id), None)
        if not defn:
            return JSONResponse(status_code=404, content={"error": "chart not found"})
        defn = dict(defn)
        defn["days"] = days
        series = compute_series(defn, lambda m, d: db.query_metric_history(m, d))
        return {"id": chart_id, **series}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ─── 6. GET /api/dashboard/home ──────────────────────────────────────────────
# @app.get("/api/dashboard/home")
def api_dashboard_home():
    """Aggregated dashboard data for Montis-style home view."""
    from profile_manager import ProfileManager
    pm = ProfileManager.get()

    try:
        r = api_readiness_composite()
        readiness = r.get("readiness", {})
        training = r.get("training", {})
        sleep = r.get("sleep", {})
    except Exception:
        readiness, training, sleep = {}, {}, {}

    severity = readiness.get("severity", "normal")
    fatigue_signal = {
        "normal":    {"label": "Normale",     "color": "green", "emoji": "🟢", "action": "Allenamento regolare"},
        "tier_down": {"label": "Alleggerire", "color": "amber", "emoji": "🟡", "action": "Riduci intensità oggi"},
        "rest":      {"label": "Riposo",      "color": "red",   "emoji": "🔴", "action": "Giorno di riposo consigliato"},
    }.get(severity, {"label": "Sconosciuto", "color": "gray", "emoji": "⚪", "action": "—"})

    today_session = None
    next_sessions = []
    try:
        import json
        from datetime import date
        plan_path = _plan_dir() / "current_plan.json"
        if plan_path.exists():
            with open(plan_path, encoding="utf-8") as f:
                plan = json.load(f)
            today_iso = date.today().isoformat()
            weeks = plan.get("weeks", [])
            all_sessions = []
            for w in weeks:
                for s in w.get("sessions", []):
                    all_sessions.append({**s, "week_start": w.get("start"), "week_idx": w.get("week_idx", 0)})
            all_sessions.sort(key=lambda x: x.get("day", ""))
            for s in all_sessions:
                if s.get("day") == today_iso:
                    today_session = s
                elif s.get("day", "") > today_iso and len(next_sessions) < 3:
                    next_sessions.append(s)
    except Exception:
        pass

    hrv = sleep.get("hrv_ms")
    sleep_h = sleep.get("sleep_h")
    rhr = sleep.get("rhr_today")

    def recovery_badge(value, key):
        if value is None:
            return {"value": "—", "status": "unknown"}
        if key == "hrv":
            if value >= 60: return {"value": f"{value:.1f} ms", "status": "good"}
            elif value >= 40: return {"value": f"{value:.1f} ms", "status": "fair"}
            return {"value": f"{value:.1f} ms", "status": "poor"}
        elif key == "sleep":
            if value >= 8: return {"value": f"{value:.1f} h", "status": "good"}
            elif value >= 7: return {"value": f"{value:.1f} h", "status": "fair"}
            return {"value": f"{value:.1f} h", "status": "poor"}
        elif key == "rhr":
            if value <= 55: return {"value": f"{value} bpm", "status": "good"}
            elif value <= 65: return {"value": f"{value} bpm", "status": "fair"}
            return {"value": f"{value} bpm", "status": "poor"}
        return {"value": str(value), "status": "unknown"}

    recovery = {
        "hrv": recovery_badge(hrv, "hrv"),
        "sleep": recovery_badge(sleep_h, "sleep"),
        "rhr": recovery_badge(rhr, "rhr"),
    }

    fitness = {
        "ctl": training.get("ctl"),
        "atl": training.get("atl"),
        "tsb": training.get("tsb"),
    }

    env = getattr(pm, "_env", {}) or {}
    icu_athlete_id = (env.get("ICU_ATHLETE_ID") or "").strip()
    icu_api_key = (env.get("ICU_API_KEY") or "").strip()
    icu_connected = bool(icu_athlete_id or icu_api_key)
    icu_write_ok = False
    try:
        from icu_calendar_push import ICUClient
        if icu_athlete_id and icu_api_key:
            client = ICUClient(icu_api_key, icu_athlete_id)
            icu_write_ok = client.check_write_permission()
    except Exception:
        pass

    quick_actions = [
        {"id": "generate", "label": "Genera Piano", "icon": "📋", "action": "gotoTab('plan');generatePlan()"},
        {"id": "sync", "label": "Sync Intervals", "icon": "☁️", "action": "icuPushNow()"},
        {"id": "workout", "label": "Nuovo Workout", "icon": "➕", "action": "gotoTab('picker')"},
        {"id": "calendar", "label": "Calendario", "icon": "📅", "action": "gotoTab('plan');document.getElementById('plan-calendar-view')?.scrollIntoView()"},
    ]

    return {
        "fitness": fitness,
        "fatigue_signal": fatigue_signal,
        "today_session": today_session,
        "next_sessions": next_sessions,
        "recovery": recovery,
        "intervals": {
            "connected": icu_connected,
            "athlete_id": icu_athlete_id,
            "write_ok": icu_write_ok,
            "method": "apikey" if icu_api_key else ("oauth" if icu_athlete_id else "none"),
        },
        "quick_actions": quick_actions,
        "readiness_score": readiness.get("score"),
        "readiness_severity": severity,
    }


# ─── 15. GET /api/onboarding/status ──────────────────────────────────────────
# @app.get("/api/onboarding/status")
def api_onboarding_status():
    """Stato di completamento del setup."""
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    ath = getattr(pm, "_athlete", {}) or {}

    required = {
        "weight_kg": "peso corporeo",
        "ftp": "FTP",
        "max_hr": "FC massima",
    }
    missing_profile = [label for k, label in required.items()
                       if not ath.get(k) and not getattr(pm, k, None)]
    if not missing_profile and not getattr(pm, "ftp", None):
        missing_profile.append("FTP")

    try:
        # v1.4.6 FIX: era query_activities(limit=1) — nome mai esistito.
        # api_activities() (iniettata da app) restituisce l'archivio completo.
        acts = api_activities()
        has_activities = bool(acts)
    except Exception:
        has_activities = False

    plan_path = _plan_dir() / "current_plan.json"
    has_plan = plan_path.exists()

    env = getattr(pm, "_env", {}) or {}
    icu_linked = bool((env.get("ICU_ATHLETE_ID") or "").strip()
                      or (env.get("ICU_API_KEY") or "").strip())

    gaps = []
    if missing_profile:
        gaps.append({"id": "profile", "label": "Completa il profilo",
                     "detail": "Mancano: " + ", ".join(missing_profile),
                     "goto": "settings"})
    if not has_activities:
        if icu_linked:
            gaps.append({"id": "activities", "label": "Sincronizza attività da Intervals.icu",
                         "detail": "ICU collegato: importa le uscite automaticamente.",
                         "goto": "icu_sync"})
        else:
            gaps.append({"id": "activities", "label": "Importa la prima uscita (FIT)",
                         "detail": "Serve almeno un FIT per chiudere il loop.",
                         "goto": "import"})
    if not has_plan:
        gaps.append({"id": "plan", "label": "Genera il primo piano",
                     "detail": "Crea un piano di 4-6 settimane.",
                     "goto": "plan"})
    if not icu_linked:
        gaps.append({"id": "icu", "label": "Collega Intervals.icu",
                     "detail": "Sincronizza pesi/uscite automaticamente.",
                     "goto": "settings"})

    done = []
    for gid, label in [("profile", "Profilo"), ("activities", "Prima uscita"),
                      ("plan", "Piano"), ("icu", "Intervals.icu")]:
        if not any(g["id"] == gid for g in gaps):
            done.append({"id": gid, "label": label})

    first_run = not (has_activities or has_plan)
    return {
        "first_run": first_run,
        "gaps": gaps,
        "done": done,
        "missing_profile_fields": missing_profile,
        "has_activities": has_activities,
        "has_plan": has_plan,
        "icu_linked": icu_linked,
        "can_sync_icu": icu_linked,
    }


# ─── 16. POST /api/onboarding/complete ───────────────────────────────────────
# @app.post("/api/onboarding/complete")
def api_onboarding_complete(body: dict):
    """Complete the 5-step onboarding wizard."""
    from profile_manager import ProfileManager
    pm = ProfileManager.get()

    profile_data = {}
    if body.get("weight"): profile_data["weight_kg"] = body["weight"]
    if body.get("height_cm"): profile_data["height_cm"] = body["height_cm"]
    if body.get("age"): profile_data["age"] = body["age"]
    if body.get("sex"): profile_data["sex"] = body["sex"]
    if body.get("ftp") and not body.get("ftp_unknown"): profile_data["ftp"] = body["ftp"]
    if body.get("lthr"): profile_data["lthr"] = body["lthr"]
    if body.get("max_hr"): profile_data["max_hr"] = body["max_hr"]

    if profile_data:
        pm.save_athlete(profile_data)

    settings_data = {}
    if body.get("weekly_hours"):
        total_hours = sum(body["weekly_hours"].values())
        settings_data["hours_per_week"] = total_hours
    if body.get("rest_days"):
        settings_data["rest_days"] = body["rest_days"]
    if body.get("goal_type"):
        settings_data["goal_type"] = body["goal_type"]
    if body.get("plan_weeks"):
        settings_data["plan_weeks"] = body["plan_weeks"]
    if body.get("event_date"):
        settings_data["event_date"] = body["event_date"]
    if body.get("event_name"):
        settings_data["event_name"] = body["event_name"]
    if body.get("event_km"):
        settings_data["event_km"] = body["event_km"]
    if body.get("event_climb"):
        settings_data["event_climb"] = body["event_climb"]

    if settings_data:
        pm.save_prefs(settings_data)

    icu_connected = body.get("icu_connected", False)

    imported = 0
    if body.get("import_recent") and icu_connected:
        try:
            import db as _db
            result = _db.run_sync(days=30)
            imported = int(result.get("activities", 0) or 0) + int(result.get("wellness", 0) or 0)
        except Exception:
            pass

    try:
        from training_planner import PlanOptions, generate_plan
        plan_opts = PlanOptions(
            enable_strength=False,
            enable_mobility=False,
            enable_nutrition=False,
            enable_integrators=False,
        )
        plan_weeks = body.get("plan_weeks", 12)
        plan = generate_plan(pm, plan_opts, weeks=plan_weeks)
        plan_id = getattr(plan, "id", "generated")
    except Exception:
        plan_id = None

    try:
        _setup_marker().write_text("1")
    except Exception:
        pass

    return {
        "ok": True,
        "profile_saved": bool(profile_data),
        "settings_saved": bool(settings_data),
        "activities_imported": imported,
        "plan_generated": plan_id is not None,
        "plan_id": plan_id,
        "message": "Setup completato con successo"
    }


# ─── 17. GET /api/profile (profile data endpoint) ────────────────────────────
# @app.get("/api/profile")
def api_profile_get():
    """Scheda Profilo Atleta — legge i dati dell'atleta attivo."""
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    a = dict(pm._athlete or {})
    for k in ("weight", "ftp", "lthr", "max_hr", "age", "height_cm",
              "one_rm_kg", "sex"):
        a.setdefault(k, None)
    return {"profile": a, "icu_connected": bool(pm.icu_api_key)}


# ─── 18. POST /api/profile (update profile data) ─────────────────────────────
# @app.post("/api/profile")
async def api_profile_put(request: Request):
    """Aggiorna il profilo atleta e (se connesso a ICU) sincronizza."""
    from profile_manager import ProfileManager
    import httpx
    body = {}
    try:
        raw = await request.body()
        body = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        body = {}
    pm = ProfileManager.get()
    allowed = ("weight", "ftp", "lthr", "max_hr", "age", "height_cm",
               "one_rm_kg", "sex")
    updates = {k: body[k] for k in allowed if k in body}
    disc_updates = {}
    if "disciplines" in body:
        disc = body["disciplines"]
        if isinstance(disc, str):
            disc = [d.strip() for d in disc.split(",") if d.strip()]
        if not isinstance(disc, list):
            raise HTTPException(400, "disciplines deve essere una lista")
        _allowed_disc = {"cycling", "running", "mtb", "swim", "strength", "mobility"}
        disc_updates["disciplines"] = [str(d).lower() for d in disc if str(d).lower() in _allowed_disc]
    for k in ("weight", "ftp", "lthr", "max_hr", "age", "height_cm", "one_rm_kg"):
        if k in updates:
            lo, hi = SETUP_LIMITS.get(k, [0, 1e9])
            try:
                v = float(updates[k])
            except (TypeError, ValueError):
                raise HTTPException(400, f"invalid {k}")
            if not (lo <= v <= hi):
                raise HTTPException(400, f"{k}={v} out of range [{lo},{hi}]")
            updates[k] = v
        if "sex" in updates and str(updates["sex"]).lower() not in _SETUP_ENUM_LOCAL["sex"]:
            raise HTTPException(400, "sex must be m/f/other")
    if "weight" in updates:
        updates["weight_kg"] = updates.pop("weight")
    if not updates and not disc_updates:
        return {"ok": True, "profile": dict(pm._athlete or {})}
    try:
        if updates:
            pm.save_athlete(updates)
        if disc_updates:
            pm.save_athlete(disc_updates)
    except ValueError as e:
        raise HTTPException(400, str(e))
    icu_msg = None
    if pm.icu_api_key:
        try:
            api_key = pm.icu_api_key
            aid = pm.icu_athlete_id or "0"
            hdr = {"Authorization": f"Bearer {api_key}"}
            cur = httpx.get(f"https://intervals.icu/api/v1/athlete/{aid}",
                            headers=hdr, timeout=15)
            icu_data = cur.json() if cur.status_code == 200 else {}
            send = {}
            if "weight" in updates:
                send["BodyWeightKg"] = updates["weight"]
            if "ftp" in updates:
                send["FTP"] = updates["ftp"]
            if "max_hr" in updates:
                send["MaxHeartRate"] = updates["max_hr"]
            if send:
                httpx.put(f"https://intervals.icu/api/v1/athlete/{aid}",
                          headers=hdr, json=send, timeout=15)
            if icu_data.get("BodyWeightKg") and not pm._athlete.get("weight_kg"):
                pm.save_athlete({"weight_kg": float(icu_data["BodyWeightKg"])})
            icu_msg = "sincronizzato con intervals.icu"
        except Exception as e:
            icu_msg = f"salvato localmente; sync ICU non riuscita: {type(e).__name__}"
    clear_cache()
    return {"ok": True, "profile": dict(pm._athlete or {}),
            "icu_sync": icu_msg}


# ─── 19. GET /api/route-wprime ───────────────────────────────────────────────
# @app.get("/api/route-wprime")
def api_route_wprime(url: str = Query(...)):
    """BETA Fase 4.7 — stima del consumo di W′ su percorso."""
    route_data = _load_route_detail(url)
    if not route_data:
        return JSONResponse({"error": "Route not scraped yet"}, 404)
    profile = (route_data.get("profile") or
               _route_profile_points(route_data.get("lat_lon_grade", [])) or
               route_data.get("profile_points") or [])
    if not profile:
        return JSONResponse({"error": "No profile data"}, 404)

    try:
        weight = float(getattr(config, "WEIGHT_KG", None) or 0) or 72.0
    except Exception:
        weight = 72.0
    mass = weight + 8.0
    g = 9.81

    climb_work_j = 0.0
    for i in range(1, len(profile)):
        de = (profile[i].get("e", 0) or 0) - (profile[i - 1].get("e", 0) or 0)
        if de > 0:
            climb_work_j += mass * g * de

    wprime_j = None
    try:
        from profile_manager import ProfileManager
        ath = getattr(ProfileManager.get(), "_athlete", {}) or {}
        wprime_j = ath.get("wprime_j") or getattr(config, "WPRIME_J", None)
    except Exception:
        wprime_j = None
    if not wprime_j:
        wprime_j = 20000.0

    used_pct = round(climb_work_j / wprime_j * 100, 1)
    feasibility = "ok" if used_pct <= 100 else ("stretch" if used_pct <= 200 else "hard")

    return {
        "climb_work_kj": round(climb_work_j / 1000.0, 1),
        "wprime_kj": round(wprime_j / 1000.0, 1),
        "wprime_used_pct": used_pct,
        "feasibility": feasibility,
        "mass_kg": round(mass, 1),
    }


# ─── 7. GET /api/huawei/hrv/daily ───────────────────────────────────────────
# @app.get("/api/huawei/hrv/daily")
def api_huawei_daily(start: str = Query("2000-01-01"),
                      end: str = Query("2100-01-01")):
    """GET DailyHRV in un range di date."""
    try:
        from huawei_api import api_huawei_daily
        return {"rows": api_huawei_daily(start, end)}
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 8. GET /api/huawei/hrv/debug ────────────────────────────────────────────
# @app.get("/api/huawei/hrv/debug")
def api_huawei_debug_ep(path: str = Query(...)):
    """GET trace debug SOURCE→FIELD→RAW→NORM→CALC→DEST."""
    try:
        from huawei_api import api_huawei_debug
        return api_huawei_debug(path)
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 9. GET /api/huawei/hrv/export ───────────────────────────────────────────
# @app.get("/api/huawei/hrv/export")
def api_huawei_export_ep(format: str = Query("csv"),
                         start: str = Query("2000-01-01"),
                         end: str = Query("2100-01-01")):
    """GET export DailyHRV come CSV o JSON."""
    try:
        from huawei_api import api_huawei_export
        data = api_huawei_export(format=format, start=start, end=end)
        if format == "json":
            return Response(content=data, media_type="application/json")
        return Response(content=data, media_type="text/csv")
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 10. GET /api/huawei/hrv/summary ─────────────────────────────────────────
# @app.get("/api/huawei/hrv/summary")
def api_huawei_summary_ep(end: str = Query("2100-01-01")):
    """GET riepilogo HRV: ultimo valore + baseline 7/14/30 + deviazione + trend."""
    try:
        from huawei_api import api_huawei_summary
        return api_huawei_summary(end=end)
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 11. POST /api/huawei/hrv ────────────────────────────────────────────────
# @app.post("/api/huawei/hrv")
def api_huawei_hrv_calc(body: dict = Body(default={})):
    """POST /api/huawei/hrv — calcola metriche HRV da RR/NN inviati."""
    try:
        from huawei_api import api_huawei_hrv_calculate
        return api_huawei_hrv_calculate(body)
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 12. POST /api/huawei/hrv/manual ─────────────────────────────────────────
# @app.post("/api/huawei/hrv/manual")
def api_huawei_manual_hrv(body: dict = Body(default={})):
    """POST scrittura manuale dati HRV su Intervals.icu."""
    try:
        from huawei_api import api_huawei_manual_hrv
        return api_huawei_manual_hrv(body)
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 13. POST /api/huawei/health-sync ────────────────────────────────────────
# @app.post("/api/huawei/health-sync")
def api_huawei_health_sync(body: dict = Body(default={})):
    """POST normalizza un record Health Sync."""
    try:
        from huawei_api import health_sync_to_hrv
        return health_sync_to_hrv(body)
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 14. POST /api/huawei/import ─────────────────────────────────────────────
# @app.post("/api/huawei/import")
def api_huawei_import(body: dict = Body(default={})):
    """POST /api/huawei/import — importa un export Huawei dal disco."""
    try:
        from huawei_api import api_huawei_import as _imp
        path = body.get("path")
        if not path or not os.path.exists(path):
            return {"error": "path_non_trovato", "path": path}
        return _imp(
            path,
            source=body.get("source", "huawei_health"),
            sync_to_icu=bool(body.get("sync_to_icu", False)),
            athlete_id=body.get("athlete_id"),
            api_key=body.get("api_key"),
        )
    except Exception as e:
        return {"error": f"internal:{type(e).__name__}"}


# ─── 21. POST /api/plan/delete-session ───────────────────────────────────────
# @app.post("/api/plan/delete-session")
async def api_plan_delete_session(request: Request):
    """v4.4 — elimina una sessione dal piano per data."""
    try:
        body = await _get_json_body(request)
    except Exception:
        body = {}
    day_iso = str(body.get("date") or "").strip()
    stype = str(body.get("session_type") or "").strip() or None
    if not day_iso:
        return JSONResponse({"error": "date (YYYY-MM-DD) required"}, 400)
    try:
        date.fromisoformat(day_iso)
    except ValueError:
        return JSONResponse({"error": "Invalid date format (use YYYY-MM-DD)"}, 400)
    json_path = _plan_dir() / "current_plan.json"
    if not json_path.exists():
        return JSONResponse({"error": "No active plan found"}, 404)
    with open(json_path, encoding="utf-8") as f:
        plan = json.load(f)
    removed = 0
    for week in plan.get("weeks", []):
        sessions = week.get("sessions", [])
        keep = []
        for s in sessions:
            if s.get("day") == day_iso and (stype is None
                                            or s.get("session_type") == stype):
                removed += 1
                continue
            keep.append(s)
        if removed and len(keep) < len(sessions):
            if not any(s.get("day") == day_iso for s in keep):
                keep.append({"day": day_iso, "session_type": "rest",
                             "duration_min": 0, "tss_estimate": 0,
                             "description": "Rest (sessione eliminata)",
                             "zwo_file": "", "zwo_name": ""})
            week["sessions"] = keep
    if not removed:
        return JSONResponse({"error": f"No session at {day_iso}"
                             + (f" ({stype})" if stype else "")}, 404)
    tp.atomic_write_plan(json_path, plan)
    return {"ok": True, "day": day_iso, "removed": removed}


# ─── 22. GET /api/upstream/check ─────────────────────────────────────────────
# @app.get("/api/upstream/check")
def api_upstream_check():
    """Check upstream Domestique for new releases."""
    from upstream_check import check_upstream
    result = check_upstream()
    return result


# ─── 23. POST /api/self-update ───────────────────────────────────────────────
# @app.post("/api/self-update")
async def api_self_update(request: Request):
    """PCC — auto-aggiornamento reale tramite GitHub Releases."""
    import shutil
    import subprocess
    import tempfile
    import httpx

    info = api_update_check(force=1)
    dl = info.get("download_url")
    if not dl:
        return JSONResponse(status_code=400, content={"ok": False, "error": "Nessun asset scaricabile per questa piattaforma"})
    plat = sys.platform
    try:
        td = tempfile.mkdtemp(prefix="pcc-update-")
        fname = info.get("asset_name") or ("PCC-Setup.exe" if plat == "win32" else "PCC.dmg")
        dest = os.path.join(td, fname)
        async with httpx.AsyncClient(timeout=300) as client:
            r = await client.get(dl, follow_redirects=True)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
        if plat == "win32" and fname.lower().endswith(".exe"):
            try:
                subprocess.Popen([dest, "/S"], shell=False)
            except OSError as e:
                needs_admin = (getattr(e, "winerror", None) == 740
                               or "740" in str(e) or "elevated" in str(e).lower())
                return JSONResponse(status_code=200, content={
                    "ok": False, "launched": False,
                    "needs_admin": bool(needs_admin),
                    "mode": "windows-installer-blocked",
                    "release_url": info.get("release_url") or dl,
                    "manual_url": info.get("release_url") or dl,
                    "error": ("L'aggiornamento silenzioso richiede i privilegi di "
                              "amministratore (Windows scrive in Program Files). "
                              "Apri la release e installa PCC-Setup.exe come admin, "
                              "oppure riavvia PCC come amministratore.")
                             if needs_admin else str(e),
                })
            prog = os.environ.get("ProgramFiles", r"C:\Program Files")
            inst_dir = os.path.join(prog, "PCC")
            exe_path = os.path.join(inst_dir, "PCC.exe")
            bat = os.path.join(td, "update.bat")
            try:
                with open(bat, "w", encoding="utf-8") as bf:
                    bf.write("@echo off\n")
                    bf.write("timeout /t 4 /nobreak >nul\n")
                    bf.write('"%s" /S\n' % dest.replace("/", "\\"))
                    bf.write('if exist "%s" start "" "%s"\n' % (exe_path, exe_path))
                DETACHED = 0x00000008
                # v1.4.6 FIX (bandit B602): niente shell=True; cmd.exe esplicito.
                subprocess.Popen(["cmd.exe", "/c", bat], creationflags=DETACHED)
            except Exception as e:
                return JSONResponse(status_code=200, content={
                    "ok": False, "launched": False,
                    "release_url": info.get("release_url") or dl,
                    "manual_url": info.get("release_url") or dl,
                    "error": "Impossibile avviare l'aggiornamento: " + str(e),
                })
            return JSONResponse(status_code=200, content={
                "ok": True, "closing": True, "mode": "windows-installer",
                "msg": "Aggiornamento in corso: l'app si chiude e riapre con la nuova versione.",
                "release_url": info.get("release_url") or dl,
            }, background=BackgroundTask(lambda: os._exit(0)))
        elif plat == "darwin" and fname.lower().endswith(".dmg"):
            subprocess.Popen(["open", dest])
            return {"ok": True, "launched": True, "mode": "macos-dmg",
                    "msg": "DMG aperta: trascina PCC in Applicazioni per aggiornare."}
        else:
            import webbrowser
            webbrowser.open(info.get("release_url") or dl)
            return {"ok": True, "launched": True, "mode": "manual",
                    "msg": "Aperta la pagina della release."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


# ─── 24. GET /oauth/terra/start ──────────────────────────────────────────────
# @app.get("/oauth/terra/start")
def api_terra_start(return_to: str = Query("/")):
    """Start the Terra auth flow — redirect to Huawei consent page."""
    from fastapi.responses import RedirectResponse
    import terra_sync
    url = terra_sync.build_auth_url(return_to)
    return RedirectResponse(url)


# ─── 25. GET /oauth/terra/callback ───────────────────────────────────────────
# @app.get("/oauth/terra/callback")
def api_terra_callback(user_id: str = Query(""), reference_id: str = Query(""),
                       error: str = Query("")):
    """Terra redirects here after Huawei consent. Exchange + bounce to app."""
    from fastapi.responses import RedirectResponse
    import terra_sync
    ok, return_to, reason = terra_sync.handle_callback(user_id, reference_id)
    sep = "&" if "?" in return_to else "?"
    if error:
        return RedirectResponse(url=f"{return_to}{sep}terra=error&reason=denied")
    if not ok:
        return RedirectResponse(url=f"{return_to}{sep}terra=error&reason={reason}")
    return RedirectResponse(url=f"{return_to}{sep}terra=connected")


# ─── 26a. GET /api/terra/status ──────────────────────────────────────────────
# @app.get("/api/terra/status")
def api_terra_status():
    """Connection status for the Terra (Huawei Health) integration."""
    import terra_sync
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    env = pm._env or {}
    return {
        "configured": terra_sync.is_configured(),
        "connected": terra_sync.get_connected(env),
        "user_id": (env.get("TERRA_USER_ID") or ""),
        "expires_at": (env.get("TERRA_EXPIRES_AT") or ""),
    }


# ─── 26b. POST /api/terra/sync ──────────────────────────────────────────────
# @app.post("/api/terra/sync")
async def api_terra_sync(request: Request):
    """Pull the last N days of sleep/body/activity from Terra into PCC."""
    import terra_sync
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    env = pm._env or {}
    if not terra_sync.get_connected(env):
        return {"ok": False, "error": "Terra non collegato"}
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    days = int(body.get("days") or 14)
    days = max(1, min(days, 90))
    w = terra_sync.sync_wellness(env, days)
    a = terra_sync.sync_activities(env, days)
    return {"ok": True, **w, **a, "days": days}


# ─── 26c. POST /api/terra/disconnect ─────────────────────────────────────────
# @app.post("/api/terra/disconnect")
def api_terra_disconnect():
    """Remove the Terra user/tokens from the active profile."""
    import terra_sync
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    terra_sync.disconnect(pm._env or {})
    return {"ok": True}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTE REGISTRATION — call this from app.py to register all routes
# ═══════════════════════════════════════════════════════════════════════════════

def register_pcc_routes(app: FastAPI):
    """Register all extracted PCC routes on the given FastAPI app."""

    # v1.4.6 FIX (F821): rilegatura reale dei placeholder dichiarati a inizio
    # modulo (vedi blocco commentato sopra). Sovrascrive sempre: i placeholder
    # None non devono sopravvivere se app li ha davvero.
    import sys as _sys
    _app_mod = _sys.modules.get("app")
    if _app_mod is not None:
        _g = globals()
        for _name in ("cached", "clear_cache", "DATA_DIR", "ROUTE_PROFILES_INDEX",
                      "_compute_local_atl", "_sync_icu_activities", "_setup_marker",
                      "_get_json_body", "SETUP_LIMITS",
                      "api_activities", "api_readiness_composite",
                      "api_update_check", "db", "config", "tp"):
            if hasattr(_app_mod, _name):
                _g[_name] = getattr(_app_mod, _name)

    app.post("/api/activity/rpe")(api_activity_rpe)
    app.get("/api/activity-insights")(api_activity_insights)
    app.get("/api/custom-charts")(api_custom_charts_list)
    app.post("/api/custom-charts")(api_custom_charts_save)
    app.delete("/api/custom-charts/{chart_id}")(api_custom_charts_delete)
    app.get("/api/custom-charts/data/{chart_id}")(api_custom_charts_data)
    app.get("/api/dashboard/home")(api_dashboard_home)
    app.get("/api/onboarding/status")(api_onboarding_status)
    app.post("/api/onboarding/complete")(api_onboarding_complete)
    app.get("/api/profile")(api_profile_get)
    app.post("/api/profile")(api_profile_put)
    app.get("/api/route-wprime")(api_route_wprime)
    app.get("/api/huawei/hrv/daily")(api_huawei_daily)
    app.get("/api/huawei/hrv/debug")(api_huawei_debug_ep)
    app.get("/api/huawei/hrv/export")(api_huawei_export_ep)
    app.get("/api/huawei/hrv/summary")(api_huawei_summary_ep)
    app.post("/api/huawei/hrv")(api_huawei_hrv_calc)
    app.post("/api/huawei/hrv/manual")(api_huawei_manual_hrv)
    app.post("/api/huawei/health-sync")(api_huawei_health_sync)
    app.post("/api/huawei/import")(api_huawei_import)
    app.post("/api/plan/delete-session")(api_plan_delete_session)
    app.get("/api/upstream/check")(api_upstream_check)
    app.get("/oauth/terra/start")(api_terra_start)
    app.get("/oauth/terra/callback")(api_terra_callback)
    app.get("/api/terra/status")(api_terra_status)
    app.post("/api/terra/sync")(api_terra_sync)
    app.post("/api/terra/disconnect")(api_terra_disconnect)
