"""v0.9.0 — Power-Duration Model (WKO5 / INSCYD style).

Mathematical fitting of the maximal power-duration relationship.
Derives mFTP, FRC, Pmax, and TTE from the rider's best-effort curve.

References:
  - Coggan AP (2015). "New WKO5 Power Duration Model (PDM V2)."
  - Coggan AP (2016). "Time to Exhaustion (TTE) — a new metric."
  - Jones AM, Burnley M, Black MI, Poole DC, Vanhatalo A (2019).
    "The Critical Power Concept and the Determinants of Endurance Exercise
    Performance." Front Physiol 10:306.
  - Morton RH (2006). "The critical power and related whole-body
    bioenergetic models." Eur J Appl Physiol 96:339-354.

The model fits the classic 3-parameter hyperbolic function:
    P(t) = CP + W' / (t + tau)
where:
  CP  = Critical Power (W) — highest sustainable power (mFTP equivalent)
  W'  = Anaerobic work capacity above CP (J)
  tau = Time constant for W' depletion (s)

Additionally derives:
  Pmax  = instantaneous peak power (from the 1-5 s data point)
  TTE   = Time to Exhaustion at CP (from the fitted curve)

v0.9.0 introduced: covers WKO5 PDM, phenotype classification, radar chart.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# Standard durations for fitting (seconds). We use 2-60 min range primarily.
# Short durations (<2 min) help anchor Pmax; long durations (>60 min) anchor CP.
_FIT_DURATIONS_S: list[int] = [5, 15, 30, 60, 120, 180, 300, 480, 600, 1200, 1800, 3600]

# Physiological bounds
_CP_FLOOR_W: float = 80.0        # Minimum plausible CP
_CP_CEIL_RATIO: float = 0.99     # CP must be < 99% of lowest short effort
_WPRIME_MIN_J: float = 5000.0    # Minimum plausible W'
_WPRIME_MAX_J: float = 80000.0   # Maximum plausible W'
_PMAX_FLOOR_W: float = 200.0     # Minimum plausible Pmax
_TAU_MIN_S: float = 0.0          # Minimum tau
_TAU_MAX_S: float = 120.0        # Maximum tau


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PowerDurationFit:
    """Result of a Power-Duration Model fit."""
    # Core parameters
    cp_w: float                     # Critical Power (W) ≈ mFTP
    wprime_j: float                 # W' — anaerobic work capacity (J)
    tau_s: float                    # Time constant for W' depletion (s)
    pmax_w: float                   # Instantaneous peak power (W)
    tte_s: float                    # Time to Exhaustion at CP (s)
    # Derived metrics
    wprime_kj: float                # W' in kJ (convenience)
    frc_j: float                    # Functional Reserve Capacity (J) — alias of wprime_j
    mftp_w: float                   # Modeled FTP — alias of cp_w
    # Fit quality
    r_squared: float                # Goodness of fit
    n_points_used: int              # Number of data points used
    fit_method: str                 # e.g. "least_squares_3p"
    # Population benchmarks (%)
    cp_pct_population: Optional[float] = None   # vs age-group median
    pmax_pct_population: Optional[float] = None
    # Raw curve points used
    curve_points: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "cp_w": round(self.cp_w, 1),
            "mftp_w": round(self.mftp_w, 1),
            "wprime_j": round(self.wprime_j, 0),
            "wprime_kj": round(self.wprime_kj, 2),
            "frc_j": round(self.frc_j, 0),
            "tau_s": round(self.tau_s, 1),
            "pmax_w": round(self.pmax_w, 1),
            "tte_s": round(self.tte_s, 0),
            "tte_min": round(self.tte_s / 60.0, 1),
            "r_squared": round(self.r_squared, 4),
            "n_points_used": self.n_points_used,
            "fit_method": self.fit_method,
            "cp_pct_population": self.cp_pct_population,
            "pmax_pct_population": self.pmax_pct_population,
            "curve_points": self.curve_points,
        }


# ══════════════════════════════════════════════════════════════════════════════
# MODEL: P(t) = CP + W' / (t + tau)
# ══════════════════════════════════════════════════════════════════════════════

def _model_power(t: float, cp: float, wprime: float, tau: float) -> float:
    """Predict power at duration t from the 3P model."""
    if t + tau <= 0:
        return 0.0
    return cp + wprime / (t + tau)


def _residuals_3p(params: tuple[float, float, float],
                  durations: list[float],
                  powers: list[float]) -> list[float]:
    """Sum of squared residuals for the 3P model."""
    cp, wprime, tau = params
    ss = 0.0
    for t, p_obs in zip(durations, powers):
        p_pred = _model_power(t, cp, wprime, tau)
        ss += (p_obs - p_pred) ** 2
    return [ss]


def _r_squared(durations: list[float], powers: list[float],
               cp: float, wprime: float, tau: float) -> float:
    """Compute R² goodness of fit."""
    if len(powers) < 3:
        return 0.0
    p_mean = sum(powers) / len(powers)
    ss_tot = sum((p - p_mean) ** 2 for p in powers) or 1e-12
    ss_res = sum((p - _model_power(t, cp, wprime, tau)) ** 2
                 for t, p in zip(durations, powers))
    return max(0.0, 1.0 - ss_res / ss_tot)


# ══════════════════════════════════════════════════════════════════════════════
# FITTING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def fit_power_duration(best_efforts: dict[int, int],
                       weight_kg: Optional[float] = None) -> Optional[PowerDurationFit]:
    """Fit the 3-parameter Power-Duration Model to the rider's curve.

    Args:
        best_efforts: {duration_s: watts} mean-max best efforts.
        weight_kg:   Rider body mass (kg) for W/kg calculations.

    Returns:
        PowerDurationFit or None if insufficient data.
    """
    if not best_efforts or len(best_efforts) < 4:
        return None

    # Filter to usable durations
    durations_f = []
    powers_f = []
    for d in _FIT_DURATIONS_S:
        w = best_efforts.get(d)
        if w and w > 0:
            durations_f.append(float(d))
            powers_f.append(float(w))

    if len(durations_f) < 4:
        return None

    # Pmax = best 1- or 5-second power
    pmax_w = 0.0
    for short_d in (1, 5):
        w = best_efforts.get(short_d)
        if w and w > 0:
            pmax_w = float(w)
            break
    if pmax_w <= 0:
        pmax_w = max(powers_f) if powers_f else 0.0

    # Grid search for optimal (CP, W', tau)
    powers_sorted = sorted(powers_f)
    p_min = powers_sorted[0]
    p_max = powers_sorted[-1]

    cp_lo = max(_CP_FLOOR_W, 0.50 * p_min)
    cp_hi = min(0.98 * p_min, p_max * 0.95)
    if cp_hi <= cp_lo:
        cp_hi = cp_lo + 10.0

    best_score = -1e30
    best_params = (0.0, 0.0, 0.0)

    # Coarse grid first
    cp_step = (cp_hi - cp_lo) / 30.0
    tau_step = 5.0
    for cp in [cp_lo + i * cp_step for i in range(31)]:
        for tau in [j * tau_step for j in range(0, 25)]:  # 0..120 s
            # For each candidate CP+tau, solve W' via linear least squares
            # P(t) = CP + W'/(t+tau) => P(t)-CP = W'/(t+tau)
            # Let y = P(t)-CP, x = 1/(t+tau) => y = W'*x (no intercept)
            xs = []
            ys = []
            valid = True
            for t, p in zip(durations_f, powers_f):
                denom = t + tau
                if denom <= 0:
                    valid = False
                    break
                x = 1.0 / denom
                y = p - cp
                if y <= 0:
                    valid = False
                    break
                xs.append(x)
                ys.append(y)
            if not valid:
                continue

            # W' = sum(x*y) / sum(x²)
            n = len(xs)
            sxy = sum(x * y for x, y in zip(xs, ys))
            sxx = sum(x * x for x in xs)
            if sxx <= 1e-12:
                continue
            wprime = sxy / sxx

            if wprime < _WPRIME_MIN_J or wprime > _WPRIME_MAX_J:
                continue

            # Score = R² (we want to maximise)
            r2 = _r_squared(durations_f, powers_f, cp, wprime, tau)
            if r2 > best_score:
                best_score = r2
                best_params = (cp, wprime, tau)

    cp, wprime, tau = best_params
    if cp < _CP_FLOOR_W or wprime < _WPRIME_MIN_J:
        return None

    # Refine with local search
    cp_lo_r = max(cp - 5.0, _CP_FLOOR_W)
    cp_hi_r = cp + 5.0
    tau_lo_r = max(tau - 5.0, _TAU_MIN_S)
    tau_hi_r = min(tau + 5.0, _TAU_MAX_S)

    for cp in [cp_lo_r + (cp_hi_r - cp_lo_r) * i / 20 for i in range(21)]:
        for tau in [tau_lo_r + (tau_hi_r - tau_lo_r) * j / 20 for j in range(21)]:
            xs = []
            ys = []
            valid = True
            for t, p in zip(durations_f, powers_f):
                denom = t + tau
                if denom <= 0:
                    valid = False
                    break
                x = 1.0 / denom
                y = p - cp
                if y <= 0:
                    valid = False
                    break
                xs.append(x)
                ys.append(y)
            if not valid:
                continue
            n = len(xs)
            sxy = sum(x * y for x, y in zip(xs, ys))
            sxx = sum(x * x for x in xs)
            if sxx <= 1e-12:
                continue
            wprime = sxy / sxx
            if wprime < _WPRIME_MIN_J or wprime > _WPRIME_MAX_J:
                continue
            r2 = _r_squared(durations_f, powers_f, cp, wprime, tau)
            if r2 > best_score:
                best_score = r2
                best_params = (cp, wprime, tau)

    cp, wprime, tau = best_params

    # TTE at CP: solve P(t) = CP => CP + W'/(t+tau) = CP => impossible.
    # TTE is the duration at which power = CP. From the model:
    # P(t) = CP + W'/(t+tau). As t→∞, P→CP. TTE is defined as the
    # duration where P(t) = CP * (1 + epsilon) for small epsilon.
    # Practically: TTE ≈ W'/CP (for tau=0) or more precisely,
    # the time at which the athlete's sustainable power drops to CP.
    # We solve: P(t) = CP => CP + W'/(t+tau) = CP => no finite solution.
    # TTE in WKO5 is the maximum duration for which power = mFTP can be
    # maintained. We approximate it as the fitted curve value at 3600s
    # if the 3600s data point exists, or extrapolate.
    # For the WKO definition: TTE = duration at which power = mFTP.
    # Since P(t) = CP + W'/(t+tau) and CP is the asymptote, TTE is
    # conceptually infinite. However, WKO5 defines TTE as the point
    # where the power-duration curve crosses below CP (the "kink").
    # We approximate: TTE = W' / (CP * 0.05) + tau (time to lose 5% above CP)
    # Or more simply: TTE = W' / (p_at_300s - CP) * 300 (scaling from 5min)
    # Standard approximation from Coggan: TTE = W' / (0.05 * CP) if we
    # define TTE as the duration at which power drops to CP + 0.05*CP.
    # Actually the most practical: TTE = time at which power = CP (asymptote).
    # We use: TTE = W' / CP + tau (approximate total sustainable duration above CP).
    # Better: use the fitted curve to find where power = CP * 1.001
    tte_s = 0.0
    for t in range(100, 7200):
        p_t = _model_power(float(t), cp, wprime, tau)
        if p_t <= cp * 1.001:
            tte_s = float(t)
            break
    if tte_s <= 0:
        tte_s = wprime / cp + tau  # fallback approximation

    # Build curve_points for the fitted curve
    curve_points = []
    for d in sorted(set(_FIT_DURATIONS_S + [int(tte_s)])):
        p_fit = _model_power(float(d), cp, wprime, tau)
        p_actual = best_efforts.get(d)
        curve_points.append({
            "duration_s": d,
            "duration_min": round(d / 60.0, 1),
            "fitted_watts": round(p_fit, 1),
            "actual_watts": p_actual,
            "residual": round((p_actual - p_fit) if p_actual else 0, 1),
        })

    r2 = best_score

    # Population benchmarks (approximate age-group medians for trained males)
    # CP ~ 3.5-4.0 W/kg, Pmax ~ 12-14 W/kg at age 30-40
    if weight_kg and weight_kg > 0:
        wkg_cp = cp / weight_kg
        wkg_pmax = pmax_w / weight_kg
        # Rough percentile vs population (untrained 2.5 W/kg CP, elite 5.5 W/kg)
        cp_pct = max(0, min(100, 100.0 * (wkg_cp - 2.5) / (5.5 - 2.5)))
        pmax_pct = max(0, min(100, 100.0 * (wkg_pmax - 8.0) / (18.0 - 8.0)))
    else:
        cp_pct = None
        pmax_pct = None

    return PowerDurationFit(
        cp_w=cp,
        wprime_j=wprime,
        tau_s=tau,
        pmax_w=pmax_w,
        tte_s=tte_s,
        wprime_kj=wprime / 1000.0,
        frc_j=wprime,
        mftp_w=cp,
        r_squared=r2,
        n_points_used=len(durations_f),
        fit_method="least_squares_3p_grid",
        cp_pct_population=round(cp_pct, 1) if cp_pct is not None else None,
        pmax_pct_population=round(pmax_pct, 1) if pmax_pct is not None else None,
        curve_points=curve_points,
    )


# ══════════════════════════════════════════════════════════════════════════════
# POWER AT ANY DURATION (from the fitted model)
# ══════════════════════════════════════════════════════════════════════════════

def predict_power(fit: PowerDurationFit, duration_s: float) -> float:
    """Predict maximal sustainable power at ``duration_s`` from the fitted model."""
    return _model_power(duration_s, fit.cp_w, fit.wprime_j, fit.tau_s)


def predict_power_curve(fit: PowerDurationFit,
                        durations: list[int] | None = None) -> list[dict]:
    """Generate a fitted power-duration curve at standard durations."""
    if durations is None:
        durations = [1, 5, 15, 30, 60, 120, 300, 480, 600, 1200, 1800, 3600]
    out = []
    for d in durations:
        p = predict_power(fit, float(d))
        out.append({
            "duration_s": d,
            "duration_min": round(d / 60.0, 1),
            "fitted_watts": round(p, 1),
            "fitted_wkg": round(p / 70.0, 2) if 70.0 > 0 else None,  # placeholder
        })
    return out
