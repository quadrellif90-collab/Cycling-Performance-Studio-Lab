"""CPSL ESPE — Energy System Progression Engine (v1.5.0).

Concepts adapted from intervalsicugptcoach-public ("Montis") © 2026
Clive King (MIT): compare two equal rolling windows of the power curve
(default 84 days) and classify the progression per energy system.

Energy-system anchors:
    anaerobic          <- delta P1m
    vo2                <- delta P5m
    threshold          <- delta P20m
    aerobic_durability <- delta P60m

Classification bands (Ride profile, ±%):
    anaerobic/vo2 : strong >=3.0  moderate >=1.5  mild >=0.8  decline <=-1.5
    threshold     : strong >=2.0  moderate >=1.0  mild >=0.5  decline <=-1.0
    aerobic       : strong >=1.5  moderate >=0.7  mild >=0.4  decline <=-1.0
    neutral band  : |delta| < 0.75 -> stable

Derived metrics:
    glycolytic_bias      = P1m / P20m        (ideal ~ 1.8)
    durability_gradient  = P60m / P20m
    vo2_reserve_ratio    = P5m / CP (when cp_w provided)
    plateau              = all valid anchor deltas within +-1.0%
    curve_profile        = log-log slope -> phenotype bucket
                           (time_trialist -0.48 .. anaerobic_specialist -0.85)

All functions are defensive and return plain dicts.
"""

from __future__ import annotations

import datetime as _dt
import math

# Anchor durations in seconds: 60, 300, 1200, 3600 (5s excluded — too noisy
# across indoor/outdoor setups).
_ANCHORS_S: tuple[int, ...] = (60, 300, 1200, 3600)

_SYSTEM_BY_ANCHOR = {
    60: "anaerobic",
    300: "vo2",
    1200: "threshold",
    3600: "aerobic_durability",
}

# Bands per system: (strong, moderate, mild, decline) thresholds in ±%.
_BANDS = {
    "anaerobic": (3.0, 1.5, 0.8, -1.5),
    "vo2": (3.0, 1.5, 0.8, -1.5),
    "threshold": (2.0, 1.0, 0.5, -1.0),
    "aerobic_durability": (1.5, 0.7, 0.4, -1.0),
}
_NEUTRAL_PCT = 0.75
_PLATEAU_TOL_PCT = 1.0

_GLYCOLYTIC_IDEAL = 1.8

# Curve-profile buckets from log-log slope (Ride profile, Montis cheat sheet):
# slope more negative => more anaerobic-specialist; less negative =>
# time-trialist / endurance monster.
_CURVE_PROFILES = [
    (-0.48, "time_trialist"),
    (-0.58, "endurance_monster"),
    (-0.65, "all_rounder"),
    (-0.72, "climber"),
    (-0.78, "sprinter_puncheur"),
    (-10.0, "anaerobic_specialist"),
]


def _ride_best_efforts(ride: dict) -> dict[int, float]:
    """Extract per-ride best efforts {duration_s: watts} from a stored ride.

    Accepted sources (first available wins):
      - ``best_efforts`` dict already keyed by duration seconds;
      - ``efforts`` list of ICU highlights [{"secs": int, "watts": float}];
      - ``power_stream`` list of 1 Hz watts (sliding-window scan).
    """
    be = ride.get("best_efforts")
    if isinstance(be, dict) and be:
        out: dict[int, float] = {}
        for k, v in be.items():
            try:
                d = int(float(k))
                w = float(v)
            except (TypeError, ValueError):
                continue
            if d > 0 and w > 0:
                out[d] = max(out.get(d, 0.0), w)
        if out:
            return out

    eff = ride.get("efforts")
    if isinstance(eff, list) and eff:
        out = {}
        for e in eff:
            if not isinstance(e, dict):
                continue
            try:
                secs = int(float(e.get("secs") or e.get("seconds") or 0))
            except (TypeError, ValueError):
                continue
            try:
                watts = float(e.get("watts") or e.get("power") or 0)
            except (TypeError, ValueError):
                continue
            if secs > 0 and watts > 0:
                out[secs] = max(out.get(secs, 0.0), watts)
        if out:
            return out

    stream = ride.get("power_stream")
    if isinstance(stream, list) and len(stream) >= 600:
        return _best_mean_powers([int(p or 0) for p in stream])

    return {}


def _best_mean_powers(power: list[int]) -> dict[int, float]:
    """Best mean power for the anchor durations from a 1 Hz power stream."""
    n = len(power)
    out: dict[int, float] = {}
    for dur in _ANCHORS_S + (5,):
        if n < dur:
            continue
        s = sum(power[:dur])
        best = s
        for i in range(dur, n):
            s += power[i] - power[i - dur]
            if s > best:
                best = s
        mean = best / dur
        if mean > 0:
            out[dur] = mean
    return out


def _classify(delta_pct: float, system: str) -> str:
    strong, moderate, mild, decline = _BANDS[system]
    if abs(delta_pct) < _NEUTRAL_PCT:
        return "stable"
    if delta_pct >= strong:
        return "strong_gain"
    if delta_pct >= moderate:
        return "moderate_gain"
    if delta_pct >= mild:
        return "mild_gain"
    if delta_pct <= decline:
        return "decline"
    return "stable"


def _curve_profile(points: list[tuple[float, float]]) -> str | None:
    """Map the current window's curve to a phenotype via log-log slope."""
    pts = [(math.log(d), math.log(w)) for d, w in points if d > 1 and w > 0]
    if len(pts) < 3:
        return None
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in pts) / sxx
    for limit, name in _CURVE_PROFILES:
        if slope >= limit:
            return name
    return None


def compute_espe(rides: list[dict], window_days: int = 84,
                 today=None, cp_w: float | None = None) -> dict:
    """Compare the current vs previous power-curve windows.

    Args:
        rides: Stored ride dicts (need ``date`` plus one of ``best_efforts``,
            ``efforts``, ``power_stream``).
        window_days: Length of each comparison window (default 84).
        today: Anchor date (defaults to real today); injectable for tests.
        cp_w: Current critical power (W) for the VO2-reserve ratio.

    Returns:
        Dict with per-system timeline entries, derived metrics, plateau flag,
        curve profile and adaptation summary. Empty-friendly when data is
        missing.
    """
    anchor = today or _dt.date.today()
    cur_start = anchor - _dt.timedelta(days=window_days)
    prev_start = cur_start - _dt.timedelta(days=window_days)

    cur_best: dict[int, float] = {}
    prev_best: dict[int, float] = {}
    n_cur_rides = n_prev_rides = 0

    for r in rides:
        try:
            d = _dt.date.fromisoformat(str(r.get("date", ""))[:10])
        except ValueError:
            continue
        if d > anchor or d < prev_start:
            continue
        rb = _ride_best_efforts(r)
        if not rb:
            continue
        if d >= cur_start:
            n_cur_rides += 1
            for dur, w in rb.items():
                cur_best[dur] = max(cur_best.get(dur, 0.0), w)
        else:
            n_prev_rides += 1
            for dur, w in rb.items():
                prev_best[dur] = max(prev_best.get(dur, 0.0), w)

    systems_out: list[dict] = []
    valid_deltas: list[float] = []
    for dur in _ANCHORS_S:
        sys_name = _SYSTEM_BY_ANCHOR[dur]
        pc, pp = cur_best.get(dur), prev_best.get(dur)
        entry: dict = {
            "system": sys_name,
            "anchor_label": f"{dur // 60}m",
            "current_w": round(pc, 1) if pc else None,
            "previous_w": round(pp, 1) if pp else None,
            "delta_pct": None,
            "classification": "insufficient_data",
        }
        if pc and pp and pp > 0:
            delta = round(100.0 * (pc - pp) / pp, 2)
            entry["delta_pct"] = delta
            entry["classification"] = _classify(delta, sys_name)
            valid_deltas.append(delta)
        systems_out.append(entry)

    # Derived metrics from the CURRENT window only (absolute shape).
    p1, p5 = cur_best.get(60), cur_best.get(300)
    p20, p60 = cur_best.get(1200), cur_best.get(3600)
    glycolytic_bias = round(p1 / p20, 2) if p1 and p20 else None
    durability_gradient = round(p60 / p20, 2) if p60 and p20 else None
    vo2_reserve = round(p5 / cp_w, 2) if p5 and cp_w else None

    balance_score = None
    if glycolytic_bias is not None:
        balance_score = round(
            max(0.0, 100.0 - 100.0 * abs(glycolytic_bias - _GLYCOLYTIC_IDEAL)
                / _GLYCOLYTIC_IDEAL), 1)

    plateau = (
        bool(valid_deltas)
        and len(valid_deltas) == len(_ANCHORS_S)
        and all(abs(dv) < _PLATEAU_TOL_PCT for dv in valid_deltas)
    )

    curve_profile_input = [
        (dur * 60, cur_best[dur * 60])
        for dur in (1, 5, 20, 60) if cur_best.get(dur * 60)
    ]
    profile = _curve_profile(curve_profile_input)

    gains = [s["classification"] for s in systems_out
             if s["classification"].endswith("_gain")]
    declines = [s["classification"] for s in systems_out
                if s["classification"] == "decline"]
    if not valid_deltas:
        adaptation_state = "insufficient_data"
        adaptation_bias = None
    elif plateau:
        adaptation_state = "plateau"
        adaptation_bias = "balanced"
    elif declines and not gains:
        adaptation_state = "regressing"
        adaptation_bias = "none"
    elif len(gains) > len(declines):
        adaptation_state = "progressing"
        top = max((s for s in systems_out if s["delta_pct"] is not None),
                  key=lambda s: s["delta_pct"])
        adaptation_bias = top["system"]
    else:
        adaptation_state = "stable"
        adaptation_bias = None

    return {
        "ok": bool(valid_deltas),
        "window_days": window_days,
        "rides_current_window": n_cur_rides,
        "rides_previous_window": n_prev_rides,
        "systems": systems_out,
        "glycolytic_bias": glycolytic_bias,
        "glycolytic_ideal": _GLYCOLYTIC_IDEAL,
        "balance_score": balance_score,
        "durability_gradient": durability_gradient,
        "vo2_reserve_ratio": vo2_reserve,
        "plateau": plateau,
        "curve_profile": profile,
        "adaptation_state": adaptation_state,
        "adaptation_bias": adaptation_bias,
    }
