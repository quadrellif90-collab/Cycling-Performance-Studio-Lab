"""CPSL advanced metrics (v1.3.0) — GoldenCheetah-inspired.

- Critical Power / W' via the 3-parameter non-linear Morton model
  (CP + W'/(t + W'/Pmax)) when scipy is available, with a robust linear 1/t
  fallback (P = CP + W'/t). Fitted on best-mean-power points from streams.
- DFA α1 proxy from HRV beat-intervals during exercise (rough estimate).
- Load distribution: time-in-zones vs polarised/pyramidal classification.

All functions are defensive and return plain dicts.
"""
from __future__ import annotations

import math

# ─────────────────────────────────────────────────────────────────────────────
# Critical Power / W' (3-parameter non-linear model)
# ─────────────────────────────────────────────────────────────────────────────

def _best_mean_power(power: list[int], window_s: int) -> float | None:
    """Best average power over any contiguous ``window_s`` of samples (1 Hz)."""
    n = len(power)
    if n < window_s or window_s <= 0:
        return None
    # sliding sum
    s = sum(power[:window_s])
    best = s
    for i in range(window_s, n):
        s += power[i] - power[i - window_s]
        if s > best:
            best = s
    return best / window_s


def _fit_cp_3param(pts):
    """Morton 3-parameter non-linear CP model: P(t) = CP + W'/(t + W'/Pmax).

    Returns {cp_w, w_prime_joules, p_max_w, r2} or None on failure. This is the
    physiologically complete formulation (adds Pmax) per Morton (1986) / the
    "CP/W'/Pmax" models favoured in recent literature.
    """
    try:
        from scipy.optimize import curve_fit
        import numpy as np

        ts = np.array([t for t, _ in pts], dtype=float)
        ps = np.array([p for _, p in pts], dtype=float)

        def model(t, CP, Wp, Pmax):
            return CP + Wp / (t + Wp / Pmax)

        p0 = [max(50.0, float(ps.min())), max(1000.0, float(ps.max()) * 60.0), max(500.0, float(ps.max()) * 2.0)]
        popt, _ = curve_fit(model, ts, ps, p0=p0, maxfev=40000, bounds=([0, 0, 0], [np.inf, np.inf, np.inf]))
        CP, Wp, Pmax = (float(v) for v in popt)
        if CP > 0 and Wp > 0 and Pmax > CP:
            pred = model(ts, *popt)
            ss_res = float(np.sum((ps - pred) ** 2))
            ss_tot = float(np.sum((ps - ps.mean()) ** 2))
            r2 = 1.0 - ss_res / ss_tot if ss_tot else 0.0
            return {"cp_w": round(CP, 1), "w_prime_joules": round(Wp, 0), "p_max_w": round(Pmax, 1), "r2": round(r2, 3)}
    except Exception:
        return None
    return None


def fit_critical_power(power: list[int], windows=(60, 180, 300, 480, 720, 1200)) -> dict:
    """Fit CP and W' from a power stream.

    Primary estimator: 3-parameter non-linear Morton model (CP + W'/(t + W'/Pmax))
    when scipy is available. Falls back to the robust linear 1/t model
    (P = CP + W'/t) when the non-linear fit is unstable or scipy is missing.

    Returns {ok, cp_w, w_prime_joules, p_max_w, r2, model, points}.
    """
    pts = []
    for t in windows:
        bmp = _best_mean_power(power, int(t))
        if bmp and bmp > 0:
            pts.append((float(t), bmp))
    if len(pts) < 3:
        return {"ok": False, "error": "not_enough_data", "points": len(pts)}

    # Linear 1/t baseline (P = CP + W'/t -> y=P, x=1/t)
    xs = [1.0 / t for t, _ in pts]
    ys = [p for _, p in pts]
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return {"ok": False, "error": "degenerate_fit"}
    slope_lin = sxy / sxx           # = W'
    cp_lin = my - slope_lin * mx    # intercept = CP
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res_lin = sum((y - (cp_lin + slope_lin * x)) ** 2 for x, y in zip(xs, ys))
    r2_lin = 1 - ss_res_lin / ss_tot if ss_tot else 0.0
    pmax_lin = cp_lin + slope_lin / xs[0] if xs else None

    # Prefer the 3-parameter non-linear fit when it is at least as good.
    nl = _fit_cp_3param(pts)
    if nl and nl["r2"] >= r2_lin and nl["cp_w"] > 0 and nl["w_prime_joules"] > 0:
        return {
            "ok": bool(nl["cp_w"] > 0 and nl["w_prime_joules"] > 0 and nl["r2"] > 0.5),
            "cp_w": nl["cp_w"],
            "w_prime_joules": nl["w_prime_joules"],
            "p_max_w": nl["p_max_w"],
            "r2": nl["r2"],
            "model": "3param_morton",
            "points": [{"t_s": t, "power_w": round(p, 1)} for t, p in pts],
        }

    return {
        "ok": bool(cp_lin > 0 and slope_lin > 0 and r2_lin > 0.5),
        "cp_w": round(cp_lin, 1),
        "w_prime_joules": round(slope_lin, 0),
        "p_max_w": round(pmax_lin, 1) if pmax_lin else None,
        "r2": round(r2_lin, 3),
        "model": "linear_1t",
        "points": [{"t_s": t, "power_w": round(p, 1)} for t, p in pts],
    }


def w_balance(power_stream: list[int], cp_w: float, w_prime_j: float,
              tau: float | None = None) -> dict:
    """W' balance over a ride (Skiba integral model).

    Default uses the *time-varying* recovery time constant from Skiba et al.
    (2015/2016, "implications of variability in W'"):

        tau = 546 * exp(-0.01 * (CP - P)) + 316   [seconds]

    which shortens recovery as intensity approaches CP — the literature-standard
    improvement over the original fixed tau=228 s. Pass an explicit ``tau`` to
    force the classic constant-recovery model.
    """
    dcp = max(0.0, cp_w)
    wbal = float(w_prime_j)
    wmin = wbal; wsum = 0.0; n = 0
    dt = 1.0
    for p in power_stream:
        if p > dcp:
            wbal -= (p - dcp) * dt
        else:
            if tau is None:
                deficit = max(0.0, dcp - p)
                tau_eff = 546.0 * math.exp(-0.01 * deficit) + 316.0
            else:
                tau_eff = tau
            wbal += (w_prime_j - wbal) * (dt / tau_eff)
        wbal = max(0.0, min(w_prime_j, wbal))
        wmin = min(wmin, wbal); wsum += wbal; n += 1
    return {
        "ok": n > 0,
        "w_min_j": round(wmin, 0),
        "w_mean_j": round(wsum / n, 0) if n else None,
        "w_final_j": round(wbal, 0),
        "depletion_pct": round(100 * (w_prime_j - wmin) / w_prime_j, 1) if w_prime_j else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DFA α1 proxy (from RR intervals)
# ─────────────────────────────────────────────────────────────────────────────

def _dfa_alpha_scales(seg: list[float], s_min: int, s_max: int) -> float | None:
    """α exponent over a window for scales in [s_min, s_max] beats (linear DFA)."""
    n = len(seg)
    if n < s_max * 2:
        return None
    mean = sum(seg) / n
    y = []
    acc = 0.0
    for v in seg:
        acc += v - mean
        y.append(acc)
    scales = [s for s in range(s_min, s_max + 1) if n // s >= 2]
    if len(scales) < 2:
        return None
    xs, fs = [], []
    for s in scales:
        m = n // s
        f = 0.0
        for k in range(m):
            chunk = y[k * s:(k + 1) * s]
            idx = list(range(s))
            mi = sum(idx) / s; mv = sum(chunk) / s
            num = sum((i - mi) * (v - mv) for i, v in zip(idx, chunk))
            den = sum((i - mi) ** 2 for i in idx)
            sl = num / den if den else 0.0
            it = mv - sl * mi
            for i, v in zip(idx, chunk):
                f += (v - (sl * i + it)) ** 2
            f /= s
        f = math.sqrt(f / m)
        xs.append(math.log(s)); fs.append(math.log(f) if f > 0 else 0.0)
    if len(xs) < 2:
        return None
    mx = sum(xs) / len(xs); mf = sum(fs) / len(fs)
    num = sum((x - mx) * (ff - mf) for x, ff in zip(xs, fs))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else None


def dfa_alpha1(rr_ms: list[float], window: int = 64, step: int = 16) -> dict:
    """Detrended Fluctuation Analysis α1 from RR intervals (standard 2-scale).

    Reports the short-term (4–16 beats) and long-term (16–64 beats) α1 exponents
    (Gronwald 2020 convention) plus a broad mean for backward compatibility.
    Aerobic threshold is typically near short-term α1 ≈ 0.75 (proxy only).
    """
    rr = [r for r in rr_ms if 300 <= r <= 2000]
    if len(rr) < window * 3:
        return {"ok": False, "error": "not_enough_rr", "n": len(rr)}

    short, long = [], []
    for i in range(0, len(rr) - window + 1, step):
        a_s = _dfa_alpha_scales(rr[i:i + window], 4, 16)
        a_l = _dfa_alpha_scales(rr[i:i + window], 16, 64)
        if a_s is not None:
            short.append(a_s)
        if a_l is not None:
            long.append(a_l)

    if not short and not long:
        return {"ok": False, "error": "alpha_computation_failed"}
    avg_short = sum(short) / len(short) if short else None
    avg_long = sum(long) / len(long) if long else None
    all_a = short + long
    avg = sum(all_a) / len(all_a)
    return {
        "ok": True,
        "alpha1_short": round(avg_short, 3) if avg_short is not None else None,
        "alpha1_long": round(avg_long, 3) if avg_long is not None else None,
        "alpha1_mean": round(avg, 3),
        "alpha1_min": round(min(all_a), 3),
        "alpha1_max": round(max(all_a), 3),
        "windows": len(all_a),
        "note": "α1_short ≈ 0.75 proxy soglia aerobica (stima indicativa)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Load distribution (polarised vs pyramidal)
# ─────────────────────────────────────────────────────────────────────────────

def load_distribution(time_in_zones: dict[str, float], ftp_w: float | None = None) -> dict:
    """Classify training intensity distribution (TID).

    ``time_in_zones``: seconds per zone key like z1..z7 (or 'easy','moderate','hard').
    Groups into low (Z1–Z2), moderate (Z3–Z4) and high (Z5+) intensity and
    classifies against Seiler's polarised 80/20 reference (Seiler & Kjerland 2006):
      - polarised:  low >= 80% and high <= 20% (the rest moderate)
      - pyramidal:  moderate > high and low < 80% (triangular, substantial tempo)
      - threshold:  high > 20% with dominant moderate/high share
    """
    if not time_in_zones:
        return {"ok": False, "error": "no_zones"}
    total = sum(v for v in time_in_zones.values() if v)
    if total <= 0:
        return {"ok": False, "error": "empty"}
    pct = {k: round(100 * v / total, 1) for k, v in time_in_zones.items() if v}

    def in_group(key: str, groups) -> bool:
        kl = key.lower()
        for g in groups:
            if kl.startswith(g):
                return True
        return False

    keys = list(pct.keys())
    if any(in_group(k, ("z1", "z2", "z3", "z4", "z5", "z6", "z7")) for k in keys):
        low = sum(pct.get(k, 0) for k in keys if in_group(k, ("z1", "z2")))
        mid = sum(pct.get(k, 0) for k in keys if in_group(k, ("z3", "z4")))
        hi = sum(pct.get(k, 0) for k in keys if in_group(k, ("z5", "z6", "z7")))
    else:
        low = sum(pct.get(k, 0) for k in keys if in_group(k, ("easy", "low", "z1", "z2")))
        mid = sum(pct.get(k, 0) for k in keys if in_group(k, ("moderate", "mid", "z3", "z4")))
        hi = sum(pct.get(k, 0) for k in keys if in_group(k, ("hard", "high", "z5", "z6", "z7")))

    if low >= 80 and hi <= 20:
        kind = "polarised"
    elif mid > hi and low < 80:
        kind = "pyramidal"
    else:
        kind = "threshold"

    return {
        "ok": True,
        "distribution_pct": pct,
        "type": kind,
        "easy_pct": round(low, 1),
        "moderate_pct": round(mid, 1),
        "hard_pct": round(hi, 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# v1.5.0 — Anaerobic repeatability (W′bal depletion statistics)
#
# Concepts adapted from intervalsicugptcoach-public ("Montis") © 2026
# Clive King (MIT): 7-day W′-balance depletion statistics per session.
# The 0.30 baseline for the divergence metric is a Montis heuristic (not
# peer-reviewed literature) — kept configurable, see config.WPRBAL_BASELINE.
# ─────────────────────────────────────────────────────────────────────────────

def anaerobic_repeatability(rides: list[dict], days: int = 7,
                            w_prime_joules: float | None = None,
                            baseline: float = 0.30, today=None) -> dict:
    """Weekly W′bal depletion repeatability stats.

    Source priority per ride:
      1. ``icu_w_prime`` + ``icu_max_wbal_depletion`` (Intervals.icu sync)
         -> pct = depletion / w_prime * 100          [source: icu]
      2. ``kj_above_ftp`` + fitted ``w_prime_joules`` -> estimated pct
                                                        [source: estimated]

    Returns dict with max/mean depletion %, moderate (>50%) and high (>60%)
    session counts, total kJ above FTP and ``w_prime_divergence``
    (= mean_depletion - baseline). Empty stats when no usable session.
    """
    import datetime as _dt

    anchor = today or _dt.date.today()
    cutoff = anchor - _dt.timedelta(days=days)

    pcts: list[float] = []
    sources: set[str] = set()
    sessions: list[dict] = []
    kj_total = 0.0
    have_kj = False

    for r in rides:
        try:
            d = _dt.date.fromisoformat(str(r.get("date", ""))[:10])
        except ValueError:
            continue
        if d < cutoff or d > anchor:
            continue

        wp = r.get("icu_w_prime")
        dep = r.get("icu_max_wbal_depletion")
        kj_a = r.get("kj_above_ftp")
        pct: float | None = None
        source = None
        joules_above: float | None = None

        if isinstance(wp, (int, float)) and wp > 0 and isinstance(
                dep, (int, float)) and dep > 0:
            pct = min(100.0, 100.0 * float(dep) / float(wp))
            source = "icu"
            joules_above = float(dep)
        elif isinstance(kj_a, (int, float)) and kj_a > 0 and isinstance(
                w_prime_joules, (int, float)) and w_prime_joules > 0:
            joules_above = float(kj_a) * 1000.0
            pct = min(100.0, 100.0 * joules_above / float(w_prime_joules))
            source = "estimated"

        if source is None or pct is None:
            continue
        sources.add(source)
        pcts.append(pct)
        if isinstance(kj_a, (int, float)) and kj_a > 0:
            kj_total += float(kj_a)
            have_kj = True
        sessions.append({
            "date": str(r.get("date"))[:10],
            "depletion_pct": round(pct, 1),
            "source": source,
        })

    if not pcts:
        return {
            "ok": False,
            "source": None,
            "max_depletion_pct": None,
            "mean_depletion_pct": None,
            "moderate_depletion_sessions": 0,
            "high_depletion_sessions": 0,
            "total_joules_above_ftp": None,
            "w_prime_divergence": None,
            "baseline": baseline,
            "window_days": days,
            "sessions": [],
        }

    mean_pct = sum(pcts) / len(pcts)
    return {
        "ok": True,
        "source": "mixed" if len(sources) > 1 else sources.pop(),
        "max_depletion_pct": round(max(pcts), 1),
        "mean_depletion_pct": round(mean_pct, 1),
        "moderate_depletion_sessions": sum(1 for p in pcts if p > 50),
        "high_depletion_sessions": sum(1 for p in pcts if p > 60),
        "total_joules_above_ftp": round(kj_total * 1000.0, 0) if have_kj else None,
        "w_prime_divergence": round(mean_pct / 100.0 - baseline, 3),
        "baseline": baseline,
        "window_days": days,
        "sessions": sorted(sessions, key=lambda s: s["date"]),
    }
