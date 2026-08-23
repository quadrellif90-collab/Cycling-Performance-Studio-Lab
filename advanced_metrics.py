"""CPSL advanced metrics (v1.3.0) — GoldenCheetah-inspired.

- Critical Power / W' via the non-linear 3-parameter model (Morton/CP-3param),
  fitted on best-mean-power points from power streams.
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


def fit_critical_power(power: list[int], windows=(60, 180, 300, 480, 720, 1200)) -> dict:
    """Fit CP and W' from a power stream using the linear CP model
    (P = CP + W'/t) over best-mean-power points — robust and fast.

    Returns {cp_w, w_prime_joules, p_max_w, r2, points}.
    """
    pts = []
    for t in windows:
        bmp = _best_mean_power(power, int(t))
        if bmp and bmp > 0:
            pts.append((float(t), bmp))
    if len(pts) < 3:
        return {"ok": False, "error": "not_enough_data", "points": len(pts)}

    # Linear regression on y = P, x = 1/t : P = CP + W' * (1/t)
    xs = [1.0 / t for t, _ in pts]
    ys = [p for _, p in pts]
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return {"ok": False, "error": "degenerate_fit"}
    slope = sxy / sxx            # = W'
    cp = my - slope * mx         # intercept = CP
    # R²
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (cp + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    p_max = cp + slope / xs[0] if xs else None  # at shortest window
    return {
        "ok": bool(cp > 0 and slope > 0 and r2 > 0.5),
        "cp_w": round(cp, 1),
        "w_prime_joules": round(slope, 0),
        "p_max_w": round(p_max, 1) if p_max else None,
        "r2": round(r2, 3),
        "points": [{"t_s": t, "power_w": round(p, 1)} for t, p in pts],
    }


def w_balance(power_stream: list[int], cp_w: float, w_prime_j: float,
              tau: float = 228.0) -> dict:
    """Approximate W' balance (Skiba model) over a ride.

    Returns min/mean/final W' balance in joules + depletion fraction.
    """
    dcp = max(0.0, cp_w)
    wbal = float(w_prime_j)
    wmin = wbal; wsum = 0.0; n = 0
    dt = 1.0
    for p in power_stream:
        if p > dcp:
            wbal -= (p - dcp) * dt
        else:
            wbal += (w_prime_j - wbal) * (dt / tau)
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

def dfa_alpha1(rr_ms: list[float], window: int = 64, step: int = 16) -> dict:
    """Detrended Fluctuation Analysis α1 over short RR windows.

    Standard practice: α1 computed on ~64-beat windows; aerobic threshold is
    often near α1 ≈ 0.75 (proxy only — not a medical measurement).
    """
    rr = [r for r in rr_ms if 300 <= r <= 2000]
    if len(rr) < window * 3:
        return {"ok": False, "error": "not_enough_rr", "n": len(rr)}

    def alpha(seg):
        n = len(seg)
        mean = sum(seg) / n
        y = []
        acc = 0.0
        for v in seg:
            acc += v - mean
            y.append(acc)
        # fluctuation at scales 4..n//4
        scales = [s for s in range(4, max(5, n // 4))]
        if len(scales) < 3:
            return None
        xs, fs = [], []
        for s in scales:
            m = n // s
            if m < 2:
                continue
            f = 0.0
            for k in range(m):
                chunk = y[k * s:(k + 1) * s]
                # linear fit
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
        if len(xs) < 3:
            return None
        mx = sum(xs) / len(xs); mf = sum(fs) / len(fs)
        num = sum((x - mx) * (ff - mf) for x, ff in zip(xs, fs))
        den = sum((x - mx) ** 2 for x in xs)
        return num / den if den else None

    alphas = []
    for i in range(0, len(rr) - window + 1, step):
        a = alpha(rr[i:i + window])
        if a is not None:
            alphas.append(a)
    if not alphas:
        return {"ok": False, "error": "alpha_computation_failed"}
    avg = sum(alphas) / len(alphas)
    return {
        "ok": True,
        "alpha1_mean": round(avg, 3),
        "alpha1_min": round(min(alphas), 3),
        "alpha1_max": round(max(alphas), 3),
        "windows": len(alphas),
        "note": "α1 ≈ 0.75 proxy soglia aerobica (stima indicativa)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Load distribution (polarised vs pyramidal)
# ─────────────────────────────────────────────────────────────────────────────

def load_distribution(time_in_zones: dict[str, float], ftp_w: float | None = None) -> dict:
    """Classify training intensity distribution.

    ``time_in_zones``: seconds per zone key like z1..z7 (or 'easy','moderate','hard').
    Returns percentages and the distribution type (polarised / pyramidal / threshold).
    """
    if not time_in_zones:
        return {"ok": False, "error": "no_zones"}
    total = sum(v for v in time_in_zones.values() if v)
    if total <= 0:
        return {"ok": False, "error": "empty"}
    pct = {k: round(100 * v / total, 1) for k, v in time_in_zones.items() if v}

    keys = sorted(pct.keys())
    lo = sum(pct.get(k, 0) for k in keys[:max(1, len(keys) // 2)])          # easy half
    mid = pct.get(keys[len(keys) // 2], 0) if len(keys) >= 3 else 0          # middle
    hi = sum(pct.get(k, 0) for k in keys[len(keys) // 2 + 1:])               # hard tail

    if hi > mid * 1.5 and lo > 70:
        kind = "polarised"
    elif mid >= hi:
        kind = "pyramidal"
    else:
        kind = "threshold"

    return {
        "ok": True,
        "distribution_pct": pct,
        "type": kind,
        "easy_pct": round(lo, 1),
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
