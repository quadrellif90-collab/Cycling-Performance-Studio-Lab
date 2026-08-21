"""Fueling planner — rifornimento per sessione basato su evidenze 2024-2026.

Implementa la "fueling revolution" (90-120 g/h multi-trasportatore), la tabella
per durata, il protocollo di gut training progressivo e il recupero 3:1.

Riferimenti: docs/SCIENCE_UPDATES_2025.md §1.
"""
from __future__ import annotations

from typing import Optional

# ── Tabelle evidence-based ──────────────────────────────────────────────────

def cho_rate_per_hour(duration_min: float, intensity: str = "moderate") -> float:
    """Grammi CHO/ora raccomandati per durata (e intensità) della sessione.

    Tabella da docs/SCIENCE_UPDATES_2025.md §1. intensity: 'low'|'moderate'|'high'.
    """
    d = max(0.0, float(duration_min or 0))
    if d < 45:
        return 0.0
    if d < 75:
        # mouth rinse / piccolo gel solo su effort hard
        return 30.0 if intensity == "high" else 0.0
    if d < 150:
        return 60.0 if intensity == "high" else 45.0
    if d < 240:
        return 75.0
    return 105.0  # 90-120 range: default prudente a 105


def carb_blend(duration_min: float) -> str:
    """Miscela consigliata in funzione della durata."""
    d = float(duration_min or 0)
    if d < 150:
        return "glucosio/maltodestrina (single transporter)"
    if d < 240:
        return "mix 2:1 glucosio:fruttosio"
    return "multi-trasportatore (glucosio+fruttosio+galattosio)"


def recovery_plan(duration_min: float, weight_kg: float = 70.0) -> dict:
    """Protocollo recupero 3:1 CHO:PROT entro 30-60 min per sessioni >60 min.

    CHO = ~1.0-1.2 g/kg per sessioni lunghe; proteine ~CHO/3 (min 20 g).
    """
    d = float(duration_min or 0)
    w = max(30.0, float(weight_kg or 70))
    if d <= 60:
        return {"required": False,
                "note": "Sessione ≤60 min: idratazione normale e pasto regolare."}
    cho = round(min(1.2, 0.8 + d / 300) * w)   # 0.8→1.2 g/kg con la durata
    prot = max(20, round(cho / 3))
    return {
        "required": True,
        "window_min": 45,
        "ratio": "3:1",
        "cho_g": cho,
        "protein_g": prot,
        "note": ("Entro 45 min dalla fine: "
                 f"{cho} g CHO + {prot} g proteine (rapporto ~3:1)."),
    }


def gut_training_phase(current_target_cho_h: float, goal_cho_h: float = 90.0,
                       weeks_done: int = 0) -> dict:
    """Progressione gut training: +10-15 g/h ogni 2 settimane verso il target.

    Protocollo 4-8 settimane (Costa 2017; linee guida 2026). Il target default
    è 90 g/h; atleti gut-trained possono spingersi a 105-120.
    """
    cur = float(current_target_cho_h or 30)
    goal = float(goal_cho_h or 90)
    weeks = int(weeks_done or 0)
    steps = []
    t = cur
    while t < goal and len(steps) < 8:
        t = min(goal, t + 15)
        steps.append(t)
    idx = min(len(steps), weeks // 2)          # un passo ogni 2 settimane
    next_target = steps[idx] if idx < len(steps) else goal
    done = idx >= len(steps)
    return {
        "current": cur,
        "goal": goal,
        "weeks_done": weeks,
        "next_target": next_target,
        "complete": done,
        "steps": steps,
        "note": ("Gut training completato — mantieni con 1-2 sessioni/settimana "
                 "al volume target.") if done else
                f"Prossimo step: {next_target} g/h nelle sessioni ≥{max(75, int(next_target))} min. "
                "+10-15 g/h ogni 2 settimane.",
    }


def session_fueling_plan(duration_min: float,
                         intensity: str = "moderate",
                         weight_kg: float = 70.0,
                         gut_trained_to: float = 60.0) -> dict:
    """Piano completo pre/durante/post per una sessione.

    Args:
        duration_min: durata attesa (min).
        intensity: 'low'|'moderate'|'high'.
        weight_kg: peso atleta.
        gut_trained_to: volume CHO/h già tollerato (da tracker gut training).
    """
    rate = cho_rate_per_hour(duration_min, intensity)
    # Il piano non supera mai ciò che l'intestino ha imparato a tollerare
    effective_rate = min(rate, float(gut_trained_to or 0)) if rate > 0 else 0.0
    hours = max(0.0, float(duration_min or 0)) / 60.0
    total_during = round(effective_rate * hours)

    plan = {
        "duration_min": duration_min,
        "intensity": intensity,
        "recommended_cho_per_hour": rate,
        "tolerated_cho_per_hour": gut_trained_to,
        "effective_cho_per_hour": effective_rate,
        "total_during_g": total_during,
        "blend": carb_blend(duration_min) if effective_rate > 0 else None,
        "during": [],
        "pre": [],
        "recovery": recovery_plan(duration_min, weight_kg),
        "notes": [],
    }

    if effective_rate <= 0:
        plan["during"].append("Solo acqua (sessione breve o bassa intensità).")
    else:
        # suddividi in prese ogni ~20-25 min
        n_intakes = max(1, round(hours * 60 / 22))
        per_intake = round(effective_rate * hours * 60 / (n_intakes * 22) * 22 / 60 *
                           60 / 60 * (effective_rate / max(1, n_intakes)), 0)
        per_intake = round(effective_rate / n_intakes)
        for i in range(1, n_intakes + 1):
            plan["during"].append(
                f"min {i * 22}: {per_intake} g CHO ({plan['blend'].split(' (')[0]})")
        if rate > effective_rate:
            plan["notes"].append(
                f"Il target teorico è {rate} g/h ma il tuo gut training copre "
                f"{effective_rate} g/h — aumenta gradualmente (+10-15 g/h ogni 2 sett).")

    # Pre-sessione
    if duration_min >= 75:
        plan["pre"] = [
            "2-3 h prima: pasto moderato di carboidrati a bassa fibra (~2 g/kg).",
            "≤60 min prima: snack leggero o gel se necessario.",
        ]
    return plan
