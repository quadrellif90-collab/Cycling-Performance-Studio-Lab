"""AI Coach training plan generation module.

Genera piani di allenamento personalizzati basati su:
1. L'analisi settimanale dell'LLM
2. Gli obiettivi dell'atleta (goal profile)
3. I dati nativi CPSL (phenotype, CP/W', durability, phase)
4. Le metodologie di training (polarized, pyramidal, threshold, HIIT, sweet_spot)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from adaptive_planner import GOAL_PROFILES, WeeklyLoadRecommendation


# ── Goal profile mapping ───────────────────────────────────────────────────

GOAL_TO_METHOD = {
    "base_build": "polarized",
    "performance": "polarized",
    "recovery": "pyramidal",
    "spring_classic": "polarized",
    "time_trial": "pyramidal",
    "climbing": "pyramidal",
    "time_trial_brief": "sweet_spot",
    "generic": "polarized",
}


def _resolve_method(preferred: str | None, goal: str | None, phenotype: dict) -> str:
    """Determina il metodo di training preferibile."""
    if preferred and preferred in {"polarized", "pyramidal", "threshold", "HIIT", "sweet_spot"}:
        return preferred
    if goal and goal in GOAL_PROFILES:
        return GOAL_TO_METHOD.get(goal, "polarized")
    # Default: polarized per la maggioranza degli atleti
    return "polarized"


# ── Piano settimanale ─────────────────────────────────────────────────────

def generate_weekly_plan(
    analysis: dict,
    goal: str | None = None,
    preferred_method: str | None = None,
    days_per_week: int = 5,
    client: object | None = None,
) -> dict:
    """Genera un piano di allenamento settimanale personalizzato.

    Args:
        analysis: Risultato di generate_weekly_analysis().
        goal: Goal profile name (es. "base_build", "performance", "recovery").
        preferred_method: Metodo preferito (polarized, pyramidal, threshold, HIIT, sweet_spot).
        days_per_week: Numero di giorni di allenamento a settimana.
        client: Client LLM per eventuale raffinamento (opzionale).

    Returns:
        Dizionario con il piano settimanale completo.
    """
    # 1. Determinare il metodo di training
    method = _resolve_method(preferred_method, goal, analysis.get("phenotype", {}))

    # 2. Raccomandazioni carico settimanale dal planner nativo CPSL
    try:
        recs = WeeklyLoadRecommendations(
            method=method,
            phenotype=analysis.get("phenotype", {}).get("primary", "All-Rounder"),
            tss_current=analysis.get("total_tss", 0),
            training_phase=analysis.get("training_phase", "Build"),
        )
        weekly_tss = recs.target_tss
        session_tss = recs.per_session_tss
        rest_days = recs.rest_day_recommendations
    except Exception:
        weekly_tss = 400.0
        session_tss = 80.0
        rest_days = [False] * days_per_week

    # 3. Build the weekly schedule structure
    schedule = {
        "method": method,
        "goal": goal or "generic",
        "weekly_tss": round(weekly_tss, 1),
        "days_per_week": days_per_week,
        "sessions": [],
        "rest_day_flags": rest_days[:days_per_week],
    }

    # 4. Generate session summaries
    training_days = []
    for i in range(days_per_week):
        is_rest = rest_days[i % len(rest_days)] if rest_days else False
        if not is_rest:
            training_days.append(i)
    remaining_tss = weekly_tss
    session_idx = 0

    for day_idx in range(days_per_week):
        is_rest = rest_days[day_idx % len(rest_days)] if rest_days else False
        if is_rest:
            schedule["sessions"].append({
                "day": day_idx + 1,
                "day_name": _day_name(day_idx),
                "type": "Rest",
                "tss": 0,
                "focus": "Recovery",
            })
            continue

        # Assegna TSS basato su metodo
        if method == "polarized":
            tss_this = min(round(remaining_tss / max(1, len(training_days)), 1), 100)
            remaining_tss -= tss_this
            focus = "Mixed (endurance + VO2max)"
        elif method == "pyramidal":
            tss_this = min(round(remaining_tss / max(1, len(training_days)), 1), 80)
            remaining_tss -= tss_this
            focus = "Build + VO2max"
        else:
            # threshold/HIIT
            tss_this = min(round(remaining_tss / max(1, len(training_days)), 1), 90)
            remaining_tss -= tss_this
            focus = "Threshold/HIIT"

        schedule["sessions"].append({
            "day": day_idx + 1,
            "day_name": _day_name(day_idx),
            "type": method,
            "tss": tss_this,
            "focus": focus,
        })

    # 5. Chiamata LLM per raffinamento (opzionale)
    if client is not None:
        try:
            weeks_str = str(weeks) if weeks else "unknown"
            goal_str = str(goal) if goal else "generic"
            method_str = str(method) if method else "polarized"
            current_fitness_str = str(analysis.get("ftp", 200)) if analysis.get("ftp") else "200"

            system_prompt = "Genera un piano di " + weeks_str + " settimane per l'obiettivo " + goal_str + \
                ". Metodo: " + method_str + ". Usa i dati fitness attuali: " + current_fitness_str + \
                ". Restituisci in formato JSON con:"
            json_format = "- settimane: number\n- weekly_plan: array di oggetti [week, method, tss_target, focus, key_sessions]\n- progression: description of TSS progression\n- target_athlete: description of target athlete for this goal"
            messages = [{"role": "user", "content": system_prompt + "\n" + json_format}]
            response = client.chat(messages=messages, system=None)
            schedule["llm_refinement"] = response
        except Exception:
            schedule["llm_refinement"] = "Refinement unavailable"
    else:
        schedule["llm_refinement"] = "Not requested"

    return schedule


def _day_name(idx: int) -> str:
    """Restituisce il nome giorno dall'indice 0=lunedì."""
    days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    return days[idx % 7]


# ── Piano obiettivo ────────────────────────────────────────────────────────

def generate_goal_plan(
    goal: str,
    current_fitness: dict,
    phenotype: dict | None = None,
    weeks: int = 4,
    client: object | None = None,
) -> dict:
    """Genera un piano per un obiettivo specifico (es. per X settimane).

    Args:
        goal: Nome goal profile ("base_build", "performance", "recovery", etc.).
        current_fitness: Dizionario CP, W', FTP, ecc.
        phenotype: Dizionario fenotipo atleta.
        weeks: Numero settimane del piano.
        client: Client LLM opzionale.

    Returns:
        Dizionario con il piano multi-settimana.
    """
    method = GOAL_TO_METHOD.get(goal, "polarized")

    # Adatta il metodo in base al fenotipo
    if phenotype and phenotype.get("primary") in {"Climber", "Rouleur"}:
        if method == "polarized":
            method = "pyramidal"  # Adattamento per fenotipi specifici

    plan = {
        "goal": goal,
        "weeks": weeks,
        "method": method,
        "weekly_tss_estimate": [],
        "weekly_focus": [],
        "sessions_total": 0,
    }

    # Genera settimane successive con progressione TSS
    base_tss = current_fitness.get("ftp", 200) * 2  # approssimazione
    for w in range(1, weeks + 1):
        progression = w / weeks  # 0.25 a 1.0
        tss_this = round(base_tss * progression * 0.8, 1)  # 80% del picco finale
        focus_map = {
            "base_build": "Base aerobica + build",
            "performance": "Performance specifica",
            "recovery": "Recupero e mantenimento",
            "generic": "Training generale",
        }
        plan["weekly_tss_estimate"].append(tss_this)
        plan["weekly_focus"].append(focus_map.get(goal, "Training generale"))

    # Genera sintesi sessioni totali
    plan["sessions_total"] = sum(range(1, weeks + 1)) * 5  # 5 sessioni/settimana approssimative

    # Chiamata LLM per raffinamento
    if client is not None:
        try:
            weeks_str = str(weeks)
            goal_str = str(goal)
            method_str = str(method)
            current_fitness_str = str(current_fitness)

            system_prompt = "Genera un piano di " + weeks_str + " settimane per l'obiettivo " + goal_str + \
                ". Metodo: " + method_str + ". Usa i dati fitness attuali: " + current_fitness_str + \
                ". Restituisci in formato JSON con:"
            json_format = "- settimane: number\n- weekly_plan: array di oggetti [week, method, tss_target, focus, key_sessions]\n- progression: description of TSS progression\n- target_athlete: description of target athlete for this goal"
            messages = [{"role": "user", "content": system_prompt + "\n" + json_format}]
            response = client.chat(messages=messages, system=None)
            plan["llm_refinement"] = response
        except Exception:
            plan["llm_refinement"] = "Unavailable"
    else:
        plan["llm_refinement"] = "Not requested"

    return plan