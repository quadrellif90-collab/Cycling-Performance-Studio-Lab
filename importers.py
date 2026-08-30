"""CPSL multi-source importers (v1.3.0).

- Garmin Connect: HRV / sleep / body battery / weight → wellness records
  (same ``<profile>/wellness/YYYY-MM-DD.json`` shape used by the ICU sync).
- FIT files: parse activity summaries (power, HR, duration) via ``fitparse``.
- GPX: reuse the project's own ``gpx_parser``.

All functions are defensive: they never raise on bad input, they return a
report dict so the API layer can surface what happened.
"""
from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from pathlib import Path

log = logging.getLogger("cpsl.importers")

# ─────────────────────────────────────────────────────────────────────────────
# Wellness record helpers (shared with ride_storage's ICU sync)
# ─────────────────────────────────────────────────────────────────────────────

def _wellness_dir() -> Path:
    from ride_storage import _wellness_dir as _wd
    return _wd()


def upsert_wellness_record(day_iso: str, updates: dict) -> dict:
    """Merge ``updates`` into the day's wellness JSON (create if missing)."""
    d = _wellness_dir()
    path = d / f"{day_iso}.json"
    rec: dict = {}
    if path.exists():
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            rec = {}
    if not rec.get("id"):
        rec["id"] = day_iso
    rec.update(updates)
    path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


# ─────────────────────────────────────────────────────────────────────────────
# Garmin Connect import (garminconnect lib — OAuth-like SSO session)
# ─────────────────────────────────────────────────────────────────────────────

def garmin_import(days: int = 28, email: str = "", password: str = "",
                  tokenstore: str | None = None) -> dict:
    """Pull recent HRV/sleep/weight from Garmin Connect into wellness records.

    Uses ``garminconnect``. On first run it needs email+password (device login);
    afterwards tokens are cached in ``tokenstore`` (default ~/.cpsl/garmin_tokens)
    and no credentials are needed. Credentials are NEVER stored.
    """
    report = {"ok": False, "imported": 0, "skipped": 0, "errors": []}
    try:
        from garminconnect import Garmin
    except ImportError:
        report["errors"].append("garminconnect not installed")
        return report

    try:
        ts = tokenstore or str(Path.home() / ".cpsl" / "garmin_tokens")
        client = None
        try:
            client = Garmin(tokenstore=ts)
            client.login()
        except Exception:
            if not (email and password):
                report["errors"].append("no_valid_session_and_no_credentials")
                return report
            client = Garmin(email=email, password=password)
            client.login()
            client.garth.dump(ts)

        today = date.today()
        for i in range(days):
            day = today - timedelta(days=i)
            day_iso = day.isoformat()
            updates: dict = {}
            # HRV (last night)
            try:
                hrv = client.get_hrv_data(day.isoformat())
                if hrv and hrv.get("hrvValue"):
                    updates["hrv"] = float(hrv["hrvValue"])
                    updates["hrvSDNN"] = float(hrv["hrvValue"])
                    updates["source_hrv"] = "garmin"
            except Exception:
                pass
            # Sleep + body battery
            try:
                sl = client.get_sleep_data(day.isoformat())
                data = (sl or {}).get("dailySleepDTO") or {}
                if data.get("sleepTimeSeconds"):
                    updates["sleepSeconds"] = int(data["sleepTimeSeconds"])
                bb = ((sl or {}).get("bodyBatteryMostRecentValue"))
                if bb is not None:
                    updates["bodyBattery"] = bb
                updates["source_sleep"] = "garmin"
            except Exception:
                pass
            # Weight
            try:
                wbs = client.get_weigh_ins(day.isoformat(), day.isoformat())
                w = (wbs or {}).get("weightInGrams") or (
                    (wbs.get("dateWeightList") or [{}])[0].get("weight") if isinstance(wbs, dict) else None)
                if w:
                    kg = float(w) / (1000.0 if float(w) > 3000 else 1.0)
                    updates["weightKg"] = round(kg, 2)
                    updates["source_weight"] = "garmin"
            except Exception:
                pass

            if updates:
                upsert_wellness_record(day_iso, updates)
                report["imported"] += 1
            else:
                report["skipped"] += 1
        report["ok"] = True
    except Exception as e:
        report["errors"].append(f"{type(e).__name__}: {e}")
    return report


# ─────────────────────────────────────────────────────────────────────────────
# FIT file import (activity summary)
# ─────────────────────────────────────────────────────────────────────────────

def parse_fit_summary(path: str) -> dict:
    """Extract a compact activity summary from a .FIT file."""
    out = {"ok": False}
    try:
        import fitparse
        f = fitparse.FitFile(path)
        started_at = None; duration_s = None; dist_m = None
        max_power = None; avg_hr = None; max_hr = None
        power_stream = []
        t0 = None
        for rec in f.get_messages():
            if rec.mesg_type == "session":
                for fld in rec.fields:
                    if fld.name == "start_time": started_at = fld.value
                    elif fld.name == "total_elapsed_time": duration_s = fld.value
                    elif fld.name == "total_distance": dist_m = fld.value
            elif rec.mesg_type == "record":
                ts = rec.get_value("timestamp"); p = rec.get_value("power"); hr = rec.get_value("heart_rate")
                if ts and t0 is None: t0 = ts
                if p is not None:
                    power_stream.append(int(p))
                if hr is not None:
                    if avg_hr is None: avg_hr = hr
                    max_hr = max(max_hr or 0, hr)
        if power_stream:
            max_power = max(power_stream)
        out.update({
            "ok": True,
            "started_at": started_at.isoformat() if hasattr(started_at, "isoformat") else started_at,
            "duration_s": int(duration_s) if duration_s else None,
            "distance_m": round(float(dist_m)) if dist_m else None,
            "max_power_w": max_power,
            "avg_hr": avg_hr, "max_hr": max_hr,
            "n_samples": len(power_stream),
        })
    except ImportError:
        out["error"] = "fitparse not installed"
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out


# ─────────────────────────────────────────────────────────────────────────────
# GPX import (project parser)
# ─────────────────────────────────────────────────────────────────────────────

def parse_gpx_summary(path: str) -> dict:
    """Compact summary of a GPX file using the project's gpx_parser."""
    out = {"ok": False}
    try:
        from gpx_parser import parse_gpx
        d = parse_gpx(path)
        out.update({
            "ok": True,
            "distance_km": round((d.total_distance or 0) / 1000, 2),
            "elevation_gain_m": round(d.total_elevation_gain or 0, 1),
            "tracks": d.total_tracks,
        })
        # duration from first/last point of first track, best-effort
        try:
            pts = d.tracks[0].segments[0].points
            if len(pts) >= 2 and pts[0].time and pts[-1].time:
                out["duration_s"] = int((pts[-1].time - pts[0].time).total_seconds())
        except Exception:
            pass
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out
