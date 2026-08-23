"""CPSL Adaptive Decision Engine (ADE) — explainable daily governance (v1.5.0).

Concepts adapted from intervalsicugptcoach-public ("Montis") © 2026
Clive King (MIT), ADE v2.21: start from a 100-point budget and apply
explicit penalties / supports with per-item reasons so every decision is
auditable ("il motore decide, l'AI spiega"). Penalty VALUES are
recalibrated on CPSL's own readiness thresholds (adaptive_planner,
config.TSB_*) — they are NOT copied verbatim from upstream.

Directives by final score:
    >= 80  train_through   full planned load
    65-79  maintain        planned load, watch flags
    50-64  reduce          cut volume/intensity
    35-49  recovery_day    active recovery only
    < 35   off             rest day

Every signal is optional: missing signals simply don't score and lower
confidence. The module never mutates state and has no I/O.
"""

from __future__ import annotations

VERSION = "cpsl-ade-1.0"

_DIRECTIVES = [
    (80, "train_through", "Carico completo — spingi sul piano"),
    (65, "maintain", "Mantieni il carico pianificato"),
    (50, "reduce", "Riduci volume o intensità"),
    (35, "recovery_day", "Giorno di recupero attivo"),
    (-999, "off", "Riposo — non allenarti oggi"),
]

# Ramp-rate bands (CTL gained / week). Aligned with the app's existing
# ACWR guidance rather than upstream values.
_RAMP_HIGH = 8.0
_RAMP_WARN = 5.0

_WPRBAL_DIVERGENCE_FLAG = 0.10


def _directive_for(score: int) -> tuple[str, str]:
    for floor, key, label in _DIRECTIVES:
        if score >= floor:
            return key, label
    return _DIRECTIVES[-1][1], _DIRECTIVES[-1][2]


def compute_ade(context: dict) -> dict:
    """Govern a single training-day decision from athlete context.

    Args:
        context: optional keys —
            tsb, ctl, atl                 form (freshness = TSB)
            ramp_rate                     CTL change over 7 days
            monotony                      Foster monotony
            hrv_ratio                     today's RMSSD / baseline (0.x)
            sleep_score                   last night 0-100
            operational_state             override: recovery_priority |
                                          load_accepting | normal
            risk_flag                     high | moderate | normal
            fatigue_forecast              red | amber | green
            load_trend                    increasing | stable | decreasing
            days_to_event, event_tsb      taper governance
            espe_state                    progression | plateau | ...
            w_prime_divergence            mean W'bal depletion - baseline

    Returns:
        Governed decision dict: score, directive, drivers[], notes[],
        confidence, version.
    """
    get = context.get

    score = 100
    drivers: list[dict] = []
    notes: list[str] = []
    available_signals = 0

    def add(delta: int, item: str, reason: str) -> None:
        nonlocal score
        score += delta
        drivers.append({"item": item, "delta": delta, "reason": reason})

    # ── Operational state ────────────────────────────────────────────────
    op_state = get("operational_state")
    if op_state is None:
        # Derive from TSB when not supplied explicitly.
        tsb_v = get("tsb")
        if isinstance(tsb_v, (int, float)):
            if tsb_v <= -30:
                op_state = "recovery_priority"
            elif tsb_v >= 25:
                op_state = "load_accepting"
            else:
                op_state = "normal"
        else:
            op_state = "unknown"

    if op_state == "recovery_priority":
        add(-30, "operational_state",
            "TSB ≤ -30: fatica accumulata — recupero prioritario")
        available_signals += 1
    elif op_state == "load_accepting":
        add(+5, "operational_state",
            "TSB ≥ +25: forma alta — corpo pronto ad accettare carico")
        available_signals += 1
    elif op_state == "normal":
        available_signals += 1

    # ── Risk flag ────────────────────────────────────────────────────────
    risk = get("risk_flag")
    if risk == "high":
        add(-30, "risk_flag", "Flag rischio alto (infortunio/malattia)")
    elif risk == "moderate":
        add(-15, "risk_flag", "Flag rischio moderato")
    elif risk == "normal":
        add(+5, "risk_flag", "Nessun fattore di rischio rilevato")
    if risk is not None:
        available_signals += 1

    # ── Fatigue forecast ─────────────────────────────────────────────────
    ff = get("fatigue_forecast")
    if ff == "red":
        add(-25, "fatigue_forecast", "Previsione fatica rossa sui prossimi giorni")
    elif ff == "amber":
        add(-12, "fatigue_forecast", "Previsione fatica ambra — attenzione al cumulo")
    elif ff == "green":
        add(+5, "fatigue_forecast", "Previsione fatica verde — margine disponibile")
    if ff is not None:
        available_signals += 1

    # ── Load trend vs state conflict ─────────────────────────────────────
    trend = get("load_trend")
    if trend == "increasing" and op_state in (
            "recovery_priority", "unknown") :
        add(-10, "load_trend",
            "Il carico sta crescendo mentre lo stato chiede prudenza")
    elif trend == "increasing" and op_state == "load_accepting":
        add(+3, "load_trend", "Carico crescente su stato che lo tollera")
    if trend is not None:
        available_signals += 1

    # ── HRV ratio ────────────────────────────────────────────────────────
    hrv = get("hrv_ratio")
    if isinstance(hrv, (int, float)) and hrv > 0:
        available_signals += 1
        if hrv < 0.90:
            add(-8, "hrv_ratio",
                f"HRV al {hrv * 100:.0f}% della baseline — recupero incompleto")
        elif hrv >= 1.00:
            add(+3, "hrv_ratio",
                f"HRV al {hrv * 100:.0f}% della baseline — sistema simpatico scarico")

    # ── Sleep ────────────────────────────────────────────────────────────
    sleep = get("sleep_score")
    if isinstance(sleep, (int, float)):
        available_signals += 1
        if sleep < 60:
            add(-6, "sleep_score", f"Sonno scarso ({sleep:.0f}/100)")
        elif sleep > 85:
            add(+3, "sleep_score", f"Sonno ottimo ({sleep:.0f}/100)")

    # ── Form (TSB) fine-tuning beyond the state gate ─────────────────────
    tsb = get("tsb")
    if isinstance(tsb, (int, float)):
        available_signals += 1
        if -30 < tsb < -15:
            add(-8, "tsb", f"TSB negativo ({tsb:+.0f}) — monitora la fatica")
        elif tsb > 25:
            pass  # already supported via load_accepting

    # ── Monotony / ramp rate ─────────────────────────────────────────────
    mono = get("monotony")
    if isinstance(mono, (int, float)) and mono > 2.0:
        add(-5, "monotony", f"Monotonia alta ({mono:.1f}) — varia gli stimoli")
    if isinstance(mono, (int, float)):
        available_signals += 1

    ramp = get("ramp_rate")
    if isinstance(ramp, (int, float)):
        available_signals += 1
        if ramp > _RAMP_HIGH:
            add(-10, "ramp_rate",
                f"Ramp CTL {ramp:+.0f}/sett — sopra la soglia sicura ({_RAMP_HIGH:.0f})")
        elif ramp > _RAMP_WARN:
            add(-5, "ramp_rate",
                f"Ramp CTL {ramp:+.0f}/sett — zona di attenzione")

    # ── Taper governance ─────────────────────────────────────────────────
    dte = get("days_to_event")
    ev_tsb = get("event_tsb")
    if isinstance(dte, (int, float)) and dte >= 0:
        available_signals += 1
        if dte <= 21 and isinstance(tsb, (int, float)) and tsb > 25 \
                and trend == "increasing":
            add(-8, "taper",
                f"Gara tra {dte:.0f}g con TSB {tsb:+.0f}: troppa forma troppo presto, "
                "il carico dovrebbe calare")
        elif dte <= 7 and isinstance(tsb, (int, float)) and tsb > 25:
            notes.append("Sharpening controllato supportato: forma alta "
                         f"a {dte:.0f}g dalla gara")
        if isinstance(ev_tsb, (int, float)) and isinstance(
                tsb, (int, float)) and abs(tsb - ev_tsb) <= 5 \
                and trend == "increasing":
            add(-8, "taper",
                "TSB già nel range target dell'evento: non aumentare il carico")

    # ── ESPE / W′bal signals (advisory in v1) ────────────────────────────
    espe = get("espe_state")
    if espe == "plateau":
        notes.append("ESPE: plateau nella progressione della curva — "
                     "considera un blocco di stimoli diversi")
    elif espe == "regressing":
        notes.append("ESPE: curva in regressione — verifica recupero e "
                     "coerenza del piano")
    wpd = get("w_prime_divergence")
    if isinstance(wpd, (int, float)) and wpd > _WPRBAL_DIVERGENCE_FLAG:
        add(-5, "w_prime_bal",
            f"Depletazione anaerobica sopra baseline (+{wpd * 100:.0f}pt) — "
            "settimana già intensa lato anaerobico")

    score = max(0, min(100, score))
    directive, label = _directive_for(score)

    n_possible = 11  # operational_state, risk, forecast, trend, hrv, sleep,
    #                  tsb, monotony, ramp, taper, wprimebal
    confidence = round(available_signals / n_possible * 100.0, 0)

    return {
        "ok": True,
        "score": int(score),
        "directive": directive,
        "directive_label": label,
        "operational_state": op_state,
        "risk_flag": risk or "not_assessed",
        "fatigue_forecast": ff or "not_assessed",
        "load_trend": trend or "not_assessed",
        "drivers": drivers,
        "notes": notes,
        "confidence": confidence,
        "signals_available": available_signals,
        "version": VERSION,
    }
