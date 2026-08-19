"""
Missing Routes — features present in Domestique/PCC but missing from CPSL.

These routes fill the gaps identified in the comparison analysis.
"""

import json
import os
import math
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Request, Query, Body
from fastapi.responses import JSONResponse


def register_missing_routes(app):
    """Register all missing routes on the FastAPI app."""

    # ── 1. BIA Manual Entry ──────────────────────────────────────────────
    @app.post("/api/bia/manual")
    async def bia_manual_entry(request: Request):
        """Insert a manual BIA reading."""
        try:
            body = await request.json()
            from bia_parser import BIAReading
            reading = BIAReading(
                date=body.get("date", datetime.now().strftime("%Y-%m-%d")),
                weight_kg=body.get("weight_kg"),
                fat_mass_pct=body.get("fat_mass_pct"),
                muscle_mass_kg=body.get("muscle_mass_kg"),
                hydration_pct=body.get("hydration_pct"),
                visceral_fat=body.get("visceral_fat"),
                phase_angle=body.get("phase_angle"),
                source="manual",
            )
            from user_home import cpsl_home
            bia_path = cpsl_home / "bia_history.json"
            history = []
            if bia_path.exists():
                history = json.loads(bia_path.read_text(encoding="utf-8"))
            history.append(reading.to_dict())
            bia_path.parent.mkdir(parents=True, exist_ok=True)
            bia_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
            return {"status": "ok", "reading": reading.to_dict()}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 2. Nutrition Periodization ───────────────────────────────────────
    @app.get("/api/nutrition/periodization")
    async def nutrition_periodization():
        """Return periodized nutrition targets by training phase."""
        try:
            from nutrition import day_macros, supplement_doses
            from user_home import cpsl_home
            athlete_path = cpsl_home / "profiles" / "default" / "athlete.json"
            athlete = {}
            if athlete_path.exists():
                athlete = json.loads(athlete_path.read_text(encoding="utf-8"))
            weight = athlete.get("weight_kg", 75)
            height = athlete.get("height_cm", 180)
            age = athlete.get("age", 30)
            sex = athlete.get("sex", "m")
            phases = {
                "base": {"day_type": "endurance", "goal": "maintain"},
                "build1": {"day_type": "moderate", "goal": "maintain"},
                "build2": {"day_type": "high_intensity", "goal": "maintain"},
                "peak": {"day_type": "high_intensity", "goal": "maintain"},
                "taper": {"day_type": "rest", "goal": "maintain"},
                "recovery": {"day_type": "rest", "goal": "maintain"},
            }
            result = {}
            for phase, cfg in phases.items():
                macros = day_macros(cfg["day_type"], cfg["goal"], weight, height, age, sex)
                result[phase] = {
                    "kcal": macros["target_kcal"],
                    "carb_g": macros["carb_g"],
                    "protein_g": macros["protein_g"],
                    "fat_g": macros["fat_g"],
                    "carb_per_kg": round(macros["carb_g"] / weight, 1) if weight else 0,
                    "protein_per_kg": round(macros["protein_g"] / weight, 1) if weight else 0,
                }
            supplements = supplement_doses(weight)
            return {"phases": result, "supplements": supplements, "weight_kg": weight}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 3. Inject Multidiscipline ────────────────────────────────────────
    @app.post("/api/plan/inject-multidiscipline")
    async def plan_inject_multidiscipline(request: Request):
        """Inject multi-discipline sessions (MTB, running, swim, strength, mobility) into plan."""
        try:
            body = await request.json()
            discipline = body.get("discipline", "strength")
            day = body.get("day", 0)
            duration_min = body.get("duration_min", 45)
            allowed = ["cycling", "running", "mtb", "swim", "strength", "mobility"]
            if discipline not in allowed:
                return JSONResponse({"error": f"Invalid discipline. Allowed: {allowed}"}, status_code=400)
            from user_home import cpsl_home
            plan_path = cpsl_home / "profiles" / "default" / "plans" / "current_plan.json"
            if not plan_path.exists():
                return JSONResponse({"error": "No active plan"}, status_code=404)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            weeks = plan.get("weeks", [])
            if day < 0 or day >= 7:
                return JSONResponse({"error": "Day must be 0-6"}, status_code=400)
            for week in weeks:
                sessions = week.get("sessions", [])
                if day < len(sessions):
                    sessions[day]["discipline"] = discipline
                    sessions[day]["duration_min"] = duration_min
                    sessions[day]["type"] = f"{discipline}_{sessions[day].get('type', 'session')}"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            return {"status": "ok", "discipline": discipline, "day": day, "duration_min": duration_min}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 4. Pedal Asymmetry (expose existing module) ─────────────────────
    @app.post("/api/pedal-import")
    async def pedal_import(request: Request):
        """Import pedal asymmetry data."""
        try:
            body = await request.json()
            from pedal_asymmetry import parse_pedal_json, save_record
            record = parse_pedal_json(body)
            save_record(record)
            return {"status": "ok", "record": record}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/api/pedal-latest")
    async def pedal_latest():
        """Get latest pedal asymmetry reading."""
        try:
            from pedal_asymmetry import load_latest
            record = load_latest()
            return record or {"error": "No pedal data"}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/api/pedal-history")
    async def pedal_history():
        """Get pedal asymmetry history."""
        try:
            from pedal_asymmetry import load_history
            history = load_history()
            return {"history": history}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 5. Workout Classification ────────────────────────────────────────
    @app.get("/api/workouts/classify")
    async def workouts_classify():
        """Classify all workouts by content type (16-type system)."""
        try:
            from user_home import cpsl_home
            workouts_dir = cpsl_home / "workouts"
            if not workouts_dir.exists():
                workouts_dir = Path("workouts")
            from classify_library_content import classify_all
            classifications = classify_all(workouts_dir)
            return {"classifications": classifications, "count": len(classifications)}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/api/workouts/classify/{filename}")
    async def workout_classify_one(filename: str):
        """Classify a single workout by content type."""
        try:
            from user_home import cpsl_home
            workouts_dir = cpsl_home / "workouts"
            if not workouts_dir.exists():
                workouts_dir = Path("workouts")
            from classify_library_content import classify_zwo_v104
            zwo_path = workouts_dir / filename
            if not zwo_path.exists():
                return JSONResponse({"error": "Workout not found"}, status_code=404)
            result = classify_zwo_v104(zwo_path)
            return result
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 6. Route Archetypes ──────────────────────────────────────────────
    @app.get("/api/route-archetypes")
    async def route_archetypes():
        """List all available route archetypes."""
        try:
            from route_archetypes import ARCHETYPE_REGISTRY
            archetypes = []
            for name, spec in ARCHETYPE_REGISTRY.items():
                archetypes.append({
                    "name": name,
                    "family": spec.family,
                    "description": spec.short_description,
                    "dist_min_km": spec.dist_min_km,
                    "dist_max_km": spec.dist_max_km,
                })
            return {"archetypes": archetypes, "count": len(archetypes)}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/api/route-archetypes/{name}")
    async def route_archetype_detail(name: str):
        """Get details for a specific route archetype."""
        try:
            from route_archetypes import ARCHETYPE_REGISTRY
            if name not in ARCHETYPE_REGISTRY:
                return JSONResponse({"error": f"Unknown archetype: {name}"}, status_code=404)
            spec = ARCHETYPE_REGISTRY[name]
            return {
                "name": name,
                "family": spec.family,
                "description": spec.short_description,
                "dist_min_km": spec.dist_min_km,
                "dist_max_km": spec.dist_max_km,
                "max_grade_cap": spec.max_grade_cap,
                "min_grade_floor": spec.min_grade_floor,
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 7. Drag-Drop Session Reorder ─────────────────────────────────────
    @app.post("/api/plan/move-session")
    async def plan_move_session(request: Request):
        """Move a session from one day/week to another (drag-drop reorder)."""
        try:
            body = await request.json()
            from_week = body.get("from_week", 0)
            from_day = body.get("from_day", 0)
            to_week = body.get("to_week", 0)
            to_day = body.get("to_day", 0)
            from user_home import cpsl_home
            plan_path = cpsl_home / "profiles" / "default" / "plans" / "current_plan.json"
            if not plan_path.exists():
                return JSONResponse({"error": "No active plan"}, status_code=404)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            weeks = plan.get("weeks", [])
            if from_week >= len(weeks) or to_week >= len(weeks):
                return JSONResponse({"error": "Week index out of range"}, status_code=400)
            from_sessions = weeks[from_week].get("sessions", [])
            to_sessions = weeks[to_week].get("sessions", [])
            if from_day >= len(from_sessions):
                return JSONResponse({"error": "From day out of range"}, status_code=400)
            session = from_sessions.pop(from_day)
            to_sessions.insert(to_day, session)
            weeks[from_week]["sessions"] = from_sessions
            weeks[to_week]["sessions"] = to_sessions
            plan["weeks"] = weeks
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            return {"status": "ok"}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 8. Plan Drift Detection ──────────────────────────────────────────
    @app.get("/api/plan/drift")
    async def plan_drift():
        """Check if actual training has drifted from the plan (CTL drift >15%)."""
        try:
            from user_home import cpsl_home
            plan_path = cpsl_home / "profiles" / "default" / "plans" / "current_plan.json"
            if not plan_path.exists():
                return {"drift_pct": 0, "status": "no_plan", "alert": False}
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            planned_ctl = plan.get("target_ctl", 0)
            actual_ctl = 0
            try:
                from fitness_estimation import estimate_ftp
                from ride_storage import load_recent_rides
                rides = load_recent_rides(days=28)
                if rides:
                    total_tss = sum(r.get("tss", 0) for r in rides if r.get("tss"))
                    actual_ctl = total_tss / 7 if total_tss else 0
            except Exception:
                pass
            if planned_ctl and actual_ctl:
                drift_pct = abs(actual_ctl - planned_ctl) / planned_ctl * 100
            else:
                drift_pct = 0
            return {
                "drift_pct": round(drift_pct, 1),
                "planned_ctl": planned_ctl,
                "actual_ctl": round(actual_ctl, 1),
                "alert": drift_pct > 15,
                "status": "ok"
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 9. Recovery Ramp + Stepback Week ─────────────────────────────────
    @app.get("/api/plan/recovery-weeks")
    async def plan_recovery_weeks():
        """Identify recovery/deload weeks in the current plan."""
        try:
            from user_home import cpsl_home
            plan_path = cpsl_home / "profiles" / "default" / "plans" / "current_plan.json"
            if not plan_path.exists():
                return {"recovery_weeks": [], "count": 0}
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            weeks = plan.get("weeks", [])
            recovery_weeks = []
            for i, week in enumerate(weeks):
                phase = week.get("phase", "")
                tss_target = week.get("tss_target", 0)
                if phase in ("recovery", "taper", "deload"):
                    recovery_weeks.append({"week": i, "phase": phase, "tss_target": tss_target})
                elif i > 0 and tss_target > 0:
                    prev_tss = weeks[i - 1].get("tss_target", 0)
                    if prev_tss > 0 and tss_target < prev_tss * 0.7:
                        recovery_weeks.append({"week": i, "phase": "stepback", "tss_target": tss_target})
            return {"recovery_weeks": recovery_weeks, "count": len(recovery_weeks)}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 10. B/C Race Taper ───────────────────────────────────────────────
    @app.post("/api/plan/add-race")
    async def plan_add_race(request: Request):
        """Add a B/C race to the plan with automatic taper + recovery."""
        try:
            body = await request.json()
            race_week = body.get("race_week", 0)
            race_type = body.get("race_type", "C")  # A, B, or C
            from user_home import cpsl_home
            plan_path = cpsl_home / "profiles" / "default" / "plans" / "current_plan.json"
            if not plan_path.exists():
                return JSONResponse({"error": "No active plan"}, status_code=404)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            weeks = plan.get("weeks", [])
            if race_week >= len(weeks):
                return JSONResponse({"error": "Race week out of range"}, status_code=400)
            taper_weeks = {"A": 2, "B": 1, "C": 0}
            recovery_weeks = {"A": 1, "B": 1, "C": 0}
            tw = taper_weeks.get(race_type, 0)
            rw = recovery_weeks.get(race_type, 0)
            for i in range(max(0, race_week - tw), race_week):
                weeks[i]["phase"] = "taper"
                weeks[i]["tss_target"] = int(weeks[i].get("tss_target", 500) * 0.6)
                weeks[i]["race_taper"] = True
            weeks[race_week]["phase"] = "race"
            weeks[race_week]["race_type"] = race_type
            for i in range(race_week + 1, min(len(weeks), race_week + 1 + rw)):
                weeks[i]["phase"] = "recovery"
                weeks[i]["tss_target"] = int(weeks[i].get("tss_target", 500) * 0.5)
                weeks[i]["race_recovery"] = True
            plan["weeks"] = weeks
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            return {
                "status": "ok",
                "race_week": race_week,
                "race_type": race_type,
                "taper_weeks": tw,
                "recovery_weeks": rw,
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 11. Ride Analytics (Decoupling + EF) ─────────────────────────────
    @app.get("/api/ride/{ride_id}/analytics")
    async def ride_analytics(ride_id: str):
        """Compute ride analytics: decoupling, efficiency factor, NP, IF."""
        try:
            from user_home import cpsl_home
            rides_dir = cpsl_home / "profiles" / "default" / "rides"
            ride_file = rides_dir / f"{ride_id}.json"
            if not ride_file.exists():
                return JSONResponse({"error": "Ride not found"}, status_code=404)
            ride = json.loads(ride_file.read_text(encoding="utf-8"))
            samples = ride.get("samples", ride.get("power_data", []))
            hr_data = ride.get("hr_data", [])
            if not samples:
                return {"error": "No power data"}
            powers = [s.get("power", 0) if isinstance(s, dict) else s for s in samples]
            valid_powers = [p for p in powers if p > 0]
            np_val = 0
            if valid_powers:
                rolling_avg = []
                for i in range(len(valid_powers)):
                    window = valid_powers[max(0, i - 29):i + 1]
                    avg = sum(window) / len(window)
                    rolling_avg.append(avg ** 4)
                np_val = (sum(rolling_avg) / len(rolling_avg)) ** 0.25 if rolling_avg else 0
            ftp = 250
            athlete_path = cpsl_home / "profiles" / "default" / "athlete.json"
            if athlete_path.exists():
                athlete = json.loads(athlete_path.read_text(encoding="utf-8"))
                ftp = athlete.get("ftp", 250)
            if_val = np_val / ftp if ftp else 0
            decoupling = 0
            ef_first = 0
            ef_second = 0
            if hr_data and len(hr_data) > 10:
                mid = len(hr_data) // 2
                first_half_powers = valid_powers[:mid] if len(valid_powers) >= mid else valid_powers
                second_half_powers = valid_powers[mid:] if len(valid_powers) >= mid else valid_powers
                first_half_hr = hr_data[:mid]
                second_half_hr = hr_data[mid:]
                avg_p1 = sum(first_half_powers) / len(first_half_powers) if first_half_powers else 0
                avg_p2 = sum(second_half_powers) / len(second_half_powers) if second_half_powers else 0
                avg_hr1 = sum(first_half_hr) / len(first_half_hr) if first_half_hr else 0
                avg_hr2 = sum(second_half_hr) / len(second_half_hr) if second_half_hr else 0
                ef_first = avg_p1 / avg_hr1 if avg_hr1 else 0
                ef_second = avg_p2 / avg_hr2 if avg_hr2 else 0
                if ef_first > 0:
                    decoupling = (ef_second - ef_first) / ef_first * 100
            return {
                "ride_id": ride_id,
                "np": round(np_val, 1),
                "if": round(if_val, 3),
                "decoupling_pct": round(decoupling, 1),
                "ef_first_half": round(ef_first, 2),
                "ef_second_half": round(ef_second, 2),
                "duration_s": len(valid_powers),
                "avg_power": round(sum(valid_powers) / len(valid_powers), 1) if valid_powers else 0,
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 12. Execution Score Route ────────────────────────────────────────
    @app.get("/api/ride/{ride_id}/execution")
    async def ride_execution_score(ride_id: str):
        """Compute execution score for a ride (prescribed vs actual)."""
        try:
            from execution_score import score_ride
            from user_home import cpsl_home
            rides_dir = cpsl_home / "profiles" / "default" / "rides"
            ride_file = rides_dir / f"{ride_id}.json"
            if not ride_file.exists():
                return JSONResponse({"error": "Ride not found"}, status_code=404)
            ride = json.loads(ride_file.read_text(encoding="utf-8"))
            planned = ride.get("planned_session", {})
            if not planned:
                return {"score": None, "message": "No planned session to compare"}
            result = score_ride(planned, ride, "power")
            return result
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 13. Rider Stats Grid ─────────────────────────────────────────────
    @app.get("/api/rider-stats")
    async def rider_stats():
        """Full rider stats grid with all metrics."""
        try:
            from user_home import cpsl_home
            athlete_path = cpsl_home / "profiles" / "default" / "athlete.json"
            athlete = {}
            if athlete_path.exists():
                athlete = json.loads(athlete_path.read_text(encoding="utf-8"))
            ftp = athlete.get("ftp", 0)
            weight = athlete.get("weight_kg", 75)
            lthr = athlete.get("lthr", 0)
            max_hr = athlete.get("max_hr", 0)
            w_kg = round(ftp / weight, 2) if weight and ftp else 0
            cp = athlete.get("cp", ftp)
            wprime = athlete.get("wprime", 0)
            pmax = athlete.get("pmax", 0)
            season_tss = 0
            season_rides = 0
            try:
                from user_home import cpsl_home
                rides_dir = cpsl_home / "profiles" / "default" / "rides"
                if rides_dir.exists():
                    for f in rides_dir.glob("*.json"):
                        try:
                            ride = json.loads(f.read_text(encoding="utf-8"))
                            season_tss += ride.get("tss", 0)
                            season_rides += 1
                        except Exception:
                            pass
            except Exception:
                pass
            season_hours = round(season_tss / 40, 1) if season_tss else 0
            return {
                "ftp": ftp,
                "w_kg": w_kg,
                "weight_kg": weight,
                "lthr": lthr,
                "max_hr": max_hr,
                "cp": cp,
                "wprime": wprime,
                "pmax": pmax,
                "season_tss": season_tss,
                "season_rides": season_rides,
                "season_hours": season_hours,
                "source": "athlete.json",
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 14. Season Totals ────────────────────────────────────────────────
    @app.get("/api/season-totals")
    async def season_totals():
        """Aggregate season totals (rides, hours, TSS, distance)."""
        try:
            from user_home import cpsl_home
            rides_dir = cpsl_home / "profiles" / "default" / "rides"
            totals = {
                "rides": 0,
                "tss": 0,
                "duration_s": 0,
                "distance_m": 0,
                "hours": 0,
                "avg_power": 0,
                "elev_gain_m": 0,
            }
            if rides_dir.exists():
                powers = []
                for f in rides_dir.glob("*.json"):
                    try:
                        ride = json.loads(f.read_text(encoding="utf-8"))
                        totals["rides"] += 1
                        totals["tss"] += ride.get("tss", 0)
                        totals["duration_s"] += ride.get("duration_s", 0)
                        totals["distance_m"] += ride.get("distance_m", 0)
                        totals["elev_gain_m"] += ride.get("elev_gain_m", 0)
                        avg_p = ride.get("avg_power", 0)
                        if avg_p:
                            powers.append(avg_p)
                    except Exception:
                        pass
                if powers:
                    totals["avg_power"] = round(sum(powers) / len(powers), 1)
            totals["hours"] = round(totals["duration_s"] / 3600, 1)
            totals["distance_km"] = round(totals["distance_m"] / 1000, 1)
            return totals
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 15. Power-Duration Model ──────────────────────────────────────────
    @app.get("/api/analytics/power-duration-model")
    async def power_duration_model(
        window_days: int = Query(90, ge=7, le=365),
    ):
        """Fit the Power-Duration Model (mFTP, FRC, Pmax, TTE) to the rider's curve."""
        try:
            from power_duration_model import fit_power_duration, predict_power_curve
            from power_curve import aggregate_power_curve
            curve = aggregate_power_curve(window_days=window_days)
            rider_curve = curve.get("rider_curve", [])
            best_efforts = {pt["duration_s"]: pt["watts"] for pt in rider_curve}
            if not best_efforts:
                return {"error": "No power data available", "fit": None}
            fit = fit_power_duration(best_efforts, curve.get("weight_kg", 70.0))
            if fit is None:
                return {"error": "Insufficient data for model fitting", "fit": None}
            return {"fit": fit.to_dict(), "source": "power_duration_model"}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 16. Phenotype Classification & Radar Chart ────────────────────────
    @app.get("/api/analytics/phenotype")
    async def phenotype_classification(
        window_days: int = Query(90, ge=7, le=365),
    ):
        """Classify athlete phenotype and return radar chart data."""
        try:
            from phenotype import classify_phenotype, get_radar_chart_data
            from power_curve import aggregate_power_curve
            curve = aggregate_power_curve(window_days=window_days)
            rider_curve = curve.get("rider_curve", [])
            best_efforts = {pt["duration_s"]: pt["watts"] for pt in rider_curve}
            if not best_efforts:
                return {"error": "No power data available", "phenotype": None}
            result = classify_phenotype(best_efforts, curve.get("weight_kg", 70.0))
            radar = get_radar_chart_data(best_efforts, curve.get("weight_kg", 70.0))
            return {"phenotype": result.to_dict() if result else None, "radar": radar}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 17. Breakthrough Detection ────────────────────────────────────────
    @app.get("/api/analytics/breakthrough")
    async def breakthrough_detection(
        ride_id: str = Query(..., description="Ride ID to analyze"),
    ):
        """Detect fitness breakthroughs in a ride."""
        try:
            from breakthrough_detector import detect_breakthrough
            from user_home import cpsl_home
            ride_path = cpsl_home / "profiles" / "default" / "rides" / f"{ride_id}.json"
            if not ride_path.exists():
                return {"error": "Ride not found"}
            ride = json.loads(ride_path.read_text(encoding="utf-8"))
            power_stream = ride.get("streams", {}).get("watts", [])
            if not power_stream:
                return {"error": "No power stream data", "result": None}
            sig = {
                "cp_w": ride.get("ftp_at_ride", 200),
                "wprime_j": 20000,
                "pmax_w": ride.get("max_power", 600),
                "tau_s": 30.0,
            }
            result = detect_breakthrough(power_stream, sig, ride.get("weight_kg", 70.0))
            return {"result": result.to_dict()}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 18. Durability Score ──────────────────────────────────────────────
    @app.get("/api/analytics/durability")
    async def durability_score(
        window_days: int = Query(365, ge=30, le=365),
    ):
        """Compute durability score (power fade on long rides)."""
        try:
            from durability_score import compute_durability_score
            from power_curve import _load_cached_rides, _filter_rides_by_window, _ride_power_stream
            from power_curve import _profile_ftp_weight
            all_rides = _load_cached_rides()
            rides = _filter_rides_by_window(all_rides, window_days)
            ride_data = []
            for r in rides:
                duration = r.get("duration_s", 0)
                if duration < 7200:
                    continue
                stream = _ride_power_stream(r)
                ride_data.append({
                    "duration_s": duration,
                    "power_stream": stream,
                    "started_at": r.get("started_at", ""),
                })
            _, weight = _profile_ftp_weight()
            result = compute_durability_score(ride_data, weight)
            return {"result": result.to_dict()}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 19. Training Phase Detection ──────────────────────────────────────
    @app.get("/api/analytics/training-phases")
    async def training_phase_detection():
        """Detect training phases from weekly summary data."""
        try:
            from training_phase_detector import detect_training_phases
            from user_home import cpsl_home
            weekly_path = cpsl_home / "profiles" / "default" / "weekly_summary.json"
            if not weekly_path.exists():
                return {"error": "No weekly summary data", "result": None}
            weekly_data = json.loads(weekly_path.read_text(encoding="utf-8"))
            if not isinstance(weekly_data, list):
                weekly_data = weekly_data.get("weeks", [])
            result = detect_training_phases(weekly_data)
            return {"result": result.to_dict()}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 20. Custom Alerts ─────────────────────────────────────────────────
    @app.get("/api/alerts/rules")
    async def get_alert_rules():
        """Get all custom alert rules."""
        try:
            from custom_alerts import load_rules
            from user_home import cpsl_home
            rules = load_rules(cpsl_home)
            return {"rules": [r.to_dict() for r in rules]}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/alerts/rules")
    async def create_alert_rule(request: Request):
        """Create a new custom alert rule."""
        try:
            from custom_alerts import create_rule, save_rules, load_rules, SUPPORTED_METRICS, OPERATORS
            from user_home import cpsl_home
            body = await request.json()
            rule = create_rule(
                name=body.get("name", "Unnamed Alert"),
                metric=body.get("metric", "power_w"),
                operator=body.get("operator", ">"),
                value=float(body.get("value", 0)),
                value2=body.get("value2"),
                streak_seconds=int(body.get("streak_seconds", 0)),
            )
            rules = load_rules(cpsl_home)
            rules.append(rule)
            save_rules(rules, cpsl_home)
            return {"status": "ok", "rule": rule.to_dict(),
                    "supported_metrics": list(SUPPORTED_METRICS.keys()),
                    "operators": OPERATORS}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.delete("/api/alerts/rules/{rule_id}")
    async def delete_alert_rule(rule_id: str):
        """Delete a custom alert rule."""
        try:
            from custom_alerts import load_rules, save_rules
            from user_home import cpsl_home
            rules = load_rules(cpsl_home)
            rules = [r for r in rules if r.id != rule_id]
            save_rules(rules, cpsl_home)
            return {"status": "ok", "deleted": rule_id}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 21. Adaptive Training Recommendation ──────────────────────────────
    @app.get("/api/analytics/adaptive-recommendation")
    async def adaptive_recommendation(
        goal: str = Query("general_fitness", description="Training goal"),
    ):
        """Generate adaptive training recommendation."""
        try:
            from adaptive_planner import generate_adaptive_recommendation, GOAL_PROFILES
            from analytics import polarization_index
            from user_home import cpsl_home
            profile_path = cpsl_home / "profiles" / "default" / "athlete.json"
            athlete = {}
            if profile_path.exists():
                athlete = json.loads(profile_path.read_text(encoding="utf-8"))
            result = generate_adaptive_recommendation(
                goal=goal,
                hrv_rmssd_pct=None,
                sleep_score=None,
                tsb=None,
                current_weekly_tss=300,
                current_weekly_hours=6,
            )
            return {
                "recommendation": result.to_dict(),
                "available_goals": {k: v["label"] for k, v in GOAL_PROFILES.items()},
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── 22. Polarization Index (per-ride) ──────────────────────────────────
    @app.get("/api/analytics/polarization")
    async def polarization_analytics(
        window_days: int = Query(90, ge=7, le=365),
    ):
        """Compute polarization index and intensity distribution analytics."""
        try:
            from analytics import polarization_index, treff_polarization_index, classify_distribution
            from power_curve import _load_cached_rides, _filter_rides_by_window
            all_rides = _load_cached_rides()
            rides = _filter_rides_by_window(all_rides, window_days)
            zones_data = []
            for r in rides:
                zones = r.get("zones", {})
                z1z2 = zones.get("z1_pct", 0) + zones.get("z2_pct", 0)
                z3z4 = zones.get("z3_pct", 0) + zones.get("z4_pct", 0)
                z5plus = zones.get("z5_pct", 0) + zones.get("z6_pct", 0) + zones.get("z7_pct", 0)
                if z1z2 + z3z4 + z5plus > 0:
                    pi_add = polarization_index(z1z2, z3z4, z5plus)
                    pi_mult = treff_polarization_index(z1z2, z3z4, z5plus)
                    classification = classify_distribution(z1z2, z3z4, z5plus, pi_add)
                    zones_data.append({
                        "date": r.get("started_at", "")[:10],
                        "z1z2_pct": round(z1z2, 1),
                        "z3z4_pct": round(z3z4, 1),
                        "z5plus_pct": round(z5plus, 1),
                        "pi_additive": pi_add,
                        "pi_multiplicative": pi_mult,
                        "classification": classification,
                    })
            return {"rides": zones_data, "n_rides": len(zones_data)}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
