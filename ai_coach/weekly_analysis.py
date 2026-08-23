"""AI Coach weekly analysis module.

Genera un'analisi settimanale strutturata usando:
1. I dati nativi CPSL (power_duration_model, phenotype, durability, phase detection)
2. L'LLM scelto dall'utente (OpenAI/Anthropic/etc.)
3. I dati ICU (se MCP/credentials attivi)

L'analisi include:
- TSS settimanale, CTL/ATL/TSB
- Polarizzazione (Treff PI)
- Fenotipo atleta
- Livello di durabilità
- Fase di allenamento
- Raccomandazioni basate sui dati
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

import httpx

from analytics import polarization_index, classify_distribution
from power_duration_model import fit_power_duration
from phenotype import classify_phenotype
from durability_score import compute_durability_score
from training_phase_detector import detect_training_phases
from ai_coach import get_client


# ── Helpers interni ────────────────────────────────────────────────────────

def _format_duration(days: int) -> str:
    """Restituisce una stringa leggibile da un numero di giorni."""
    if days <= 0:
        return "nessun dato"
    if days == 1:
        return "1 giorno"
    return f"{days} giorni"


def _safe_float(val) -> float | None:
    """Converte in float se possibile, altrimenti None."""
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


# ── Analisi settimanale ────────────────────────────────────────────────────

def generate_weekly_analysis(
    rides: list[dict] | None = None,
    profile_data: dict | None = None,
    client: object | None = None,
) -> dict:
    """Genera un'analisi settimanale completa.

    Args:
        rides: Lista di diccionari ride (opzionale; se None si prova a caricare
            dal profilo attuale via API CPSL).
        profile_data: Dati profilo atleta (ftp, weight, hrv, ecc.).
        client: Client LLM già istanziato (se None, usa get_client()).

    Returns:
        Dizionario con l'analisi completa pronta per essere inviata all'LLM
        o visualizzata direttamente.
    """
    # 1. Caricare i dati se non forniti
    if rides is None:
        try:
            import httpx
            resp = httpx.get("http://127.0.0.1:22400/api/rides/recent", timeout=10.0)
            rides = resp.json() if resp.status_code == 200 else []
        except Exception:
            rides = []

    if profile_data is None:
        try:
            import httpx
            resp = httpx.get("http://127.0.0.1:22400/api/athlete/profile", timeout=10.0)
            profile_data = resp.json() if resp.status_code == 200 else {}
        except Exception:
            profile_data = {}

    # 2. Dati nativi CPSL
    tss_values = [_safe_float(r.get("tss")) for r in rides if _safe_float(r.get("tss")) is not None]
    total_tss = sum(tss_values) if tss_values else 0.0

    # CP/W' fitting da tutte le sessioni con dati potenza
    cp_w_prime_list = []
    for r in rides:
        wp = r.get("power_data") or r.get("w_model") or {}
        if wp:
            try:
                fit = fit_power_duration(wp.get("power_points", []))
                cp_w_prime_list.append(fit)
            except Exception:
                pass

    # Metriche derivate
    avg_tss_per_week = total_tss / max(len(rides), 1) * 7  # approssimazione settimana
    # Polarizzazione da ultima sessione completa
    last_ride = rides[-1] if rides else {}
    z1z2 = _safe_float(last_ride.get("z1_time")) + _safe_float(last_ride.get("z2_time"))
    z3z4 = _safe_float(last_ride.get("z3_time")) + _safe_float(last_ride.get("z4_time"))
    z5plus = _safe_float(last_ride.get("z5_time")) + _safe_float(last_ride.get("z6_time")) + _safe_float(last_ride.get("z7_time"))
    total_z = z1z2 + z3z4 + z5plus
    pi = polarization_index(z1z2, z3z4, z5plus) if total_z > 0 else 0.0
    classification = classify_distribution(z1z2, z3z4, z5plus, pi) if total_z > 0 else "base"

    # Fenotipo
    phenotype_data = {}
    if profile_data.get("ftp") and profile_data.get("weight_kg"):
        try:
            phenotype_data = classify_phenotype(
                ftp=_safe_float(profile_data["ftp"]),
                weight_kg=_safe_float(profile_data["weight_kg"]),
            )
        except Exception:
            phenotype_data = {"primary": "All-Rounder", "radar": [100]*5}

    # Durabilità
    durability = {}
    if len(rides) >= 2:
        try:
            # Primo e ultimo ride della settimana
            first_rides = rides[:1] if rides else []
            last_rides = rides[-1:] if rides else []
            # Simplified: use last ride power data
            last_power = (_safe_float(last_ride.get("power_average")) or 0)
            durability = compute_durability(
                fresh_power=last_power,
                fatigued_power=_safe_float(rides[-2].get("power_average")) if len(rides) >= 2 else last_power,
            )
        except Exception:
            durability = {"score": "N/A", "tier": "unknown"}

    # Fase di allenamento
    # v1.4.6 FIX (F821): "detect_phase" non esiste; il modulo importa
    # detect_training_phases (training_phase_detector), che però richiede
    # weekly_summaries [{week_start, tss, hours, if_avg, ride_count}] —
    # le costruiamo dalle ride degli ultimi 28 giorni.
    phase = "Unknown"
    if rides:
        try:
            from datetime import timedelta as _td
            _wk = defaultdict(lambda: {"tss": 0.0, "hours": 0.0, "ifs": [],
                                       "count": 0, "start": None})
            for r in rides:
                try:
                    d = datetime.fromisoformat(str(r.get("started_at") or r.get("date") or ""))[:10]
                except Exception:
                    continue
                monday = (datetime.fromisoformat(d) - _td(days=datetime.fromisoformat(d).weekday())).date().isoformat()
                w = _wk[monday]
                w["tss"] += float(r.get("tss") or 0)
                w["hours"] += float(r.get("duration_sec") or r.get("moving_time") or 0) / 3600.0
                if r.get("if_avg") is not None:
                    w["ifs"].append(float(r["if_avg"]))
                w["count"] += 1
                w["start"] = monday
            summaries = [{"week_start": s["start"], "tss": round(s["tss"], 1),
                          "hours": round(s["hours"], 2),
                          "if_avg": round(sum(s["ifs"]) / len(s["ifs"]), 3) if s["ifs"] else 0.0,
                          "ride_count": s["count"]}
                         for s in _wk.values() if s["count"]]
            if summaries:
                phase = detect_training_phases(summaries).current_phase or "Unknown"
        except Exception:
            phase = "Unknown"

    # 3. Prepara il contesto per l'LLM
    context = {
        "total_tss": round(total_tss, 1),
        "avg_tss_per_week": round(avg_tss_per_week, 1),
        "weekly_sessions": len(rides),
        "polarization_index": round(pi, 2),
        "polarization_class": classification,
        "phenotype": phenotype_data.get("primary", "All-Rounder"),
        "phenotype_radar": phenotype_data.get("radar", [100]*5),
        "durability_score": durability.get("score", "N/A"),
        "durability_tier": durability.get("tier", "unknown"),
        "training_phase": phase,
        "cp": _safe_float(profile_data.get("ftp")),
        "weight_kg": _safe_float(profile_data.get("weight_kg")),
        "hrv_baseline": _safe_float(profile_data.get("hrv_baseline_mean")),
        "rides_count": len(rides),
    }

    # 4. Chiamata LLM se client disponibile
    if client is None:
        from ai_coach import get_client
        client = get_client()

    if client is not None:
        try:
            system_prompt = """Sei un analista ciclismo esperto. Fornisci un'analisi 
settimanale strutturata e basata sui dati. Usa i valori seguenti e restituisci
un paragrafo sintetico (massimo 150 parole) con:
1. Stato di forma attuale
2. Punti di forza/debolezza
3. Raccomandazione per la settimana successiva
4. Eventuali segnali di sovrallenamento"""
            
            messages = [{"role": "user", "content": f"""Ecco i dati dell'analisi settimanale:

{context}

Fornisci l'analisi richiesta."""}]
            response = client.chat(messages=messages, system=system_prompt)
            context["llm_analysis"] = response
        except Exception as e:
            context["llm_analysis"] = f"Errore LLM: {e}"
    else:
        context["llm_analysis"] = "Client LLM non disponibile"

    return context


# ── Durabilità semplificata ────────────────────────────────────────────────

def compute_durability(fresh_power: float, fatigued_power: float) -> dict:
    """Calcola un punteggio di durabilità Xert-style.

    fresh_power: potenza media nelle prime 60min
    fatigued_power: potenza media dopo 120min di sforzo
    """
    if fatigued_power >= fresh_power:
        return {"score": 100, "tier": "exceptional"}

    drop_pct = ((fresh_power - fatigued_power) / fresh_power) * 100
    if drop_pct <= 10:
        tier = "exceptional"
    elif drop_pct <= 15:
        tier = "good"
    elif drop_pct <= 20:
        tier = "average"
    else:
        tier = "developing"

    # Normalizza punteggio 0-100
    score = max(0, 100 - drop_pct)
    return {"score": round(score, 1), "tier": tier}