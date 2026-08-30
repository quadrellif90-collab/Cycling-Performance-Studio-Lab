"""Friel coaching prompts extracted from rbrands/intervals-icu-sync.

Questo modulo contiene system prompt e metodi di coaching basati sulla
metodologia Friel, integrati con l'analisi nativa di CPSL.
"""
from __future__ import annotations

# ── System prompt Friel per AI Coach ──────────────────────────────────────

FRIEL_SYSTEM_PROMPT = """Sei un coach ciclistico Friel certificato. La metodologia Friel
si basa su:

1. Allenamento polarizzato: la maggioranza del volume a bassa intensità (Zone 1-2),
   una porzione significativa a media-alta intensità (Zone 3-4), con lavori
   brevi ad alta intensità (Zone 5-6).

2. Monitoraggio carico: TSS settimanale, CTL (Condition Training Load), ATL 
   (Acute Training Load), TSB (Training Stress Balance). CTL crescente, TSB 
   dentro la zona verde (-10 a +10) è segno di supercompensation.

3. Zone di frequenza cardiaca: basate su LTHR (Lactate Threshold Heart Rate).
   Le zone sono:
   - Z1: Recupero attivo < 81% LTHR
   - Z2: Fondamentale 81-90% LTHR
   - Z3: Tempo 91-94% LTHR
   - Z4: Soglia 95-99% LTHR
   - Z5: Vo2max 100-102% LTHR
   - Z6: Anaerobica > 102% LTHR

4. Principi chiave:
   - Carico progressivo settimanale (massimo aumento 5-10%/settimana)
   - Sessioni HIIT non consecutive (minimo 48h gap)
   - Una sessione lunga del weekend (6+ ore) per adattamenti aerobici
   - Settimane di carico ogni 3-4 settimane seguite da settimana di scarico

Il tuo compito è analizzare i dati forniti e restituire:
1. Valutazione stato attuale (form, fatigue, form)
2. Raccomandazioni specifiche per il prossimo blocco di allenamento
3. Lavori specifici (intervals, duration, intensity) basati sui dati reali
4. Segnali di allarme per sovrallenamento
5. Adattamenti basati sul fenotipo atleta"""

# ── Prompt per analisi settimanale ────────────────────────────────────────

WEEKLY_ANALYSIS_PROMPT = """Esegui un'analisi settimanale completa usando la 
metodologia Friel unita ai dati nativi CPSL (power-duration model, phenotype, 
durability, polarization). Input dati:

- TSS settimanale: {total_tss}
- CTL/ATL/TSB stimati: {ctlbelt}
- Polarizzazione index: {pi} ({classification})
- Fenotipo: {phenotype}
- Fase di allenamento: {phase}
- Durabilità: {durability_score} ({durability_tier})
- CFTP (Critical Power): {ftp} W

Output richiesto in formato strutturato:
1. Stato forma attuale (1-10 scale)
2. Principali adattamenti fisiologici
3. Raccomandazioni training specifiche (3-5 punti)
4. Lavori chiave per la settimana prossima (formato: giorno/tipo/intervalli)
5. Segnali di sovrallenamento (se presenti)
6. Modifiche al carico suggerite"""

# ── Prompt per generazione piano ─────────────────────────────────────────

GENERATE_PLAN_PROMPT = """Genera un piano di allenamento di {weeks} settimane per 
l'atleta con i seguenti parametri:

- Obiettivo: {goal} (metodo: {method})
- FTP attuale: {ftp} W
- Fenotipo: {phenotype_primary} ({phenotype_radar_description})
- Ore di training settimanali disponibili: {hours_per_week}
- Giorni di training disponibili: {days_per_week}
- Fase attuale: {phase}
- Durabilità: {durability_tier}

Output richiesto:
1. OBIETTIVO SETTIMANALE: descrizione chiara
2. DISTRIBUZIONE TSS: totale settimanale e per sessione media
3. METODO DI TRAINING: perché questo metodo per questo atleta
4. SCHEDA SETTIMANALE: per ogni giorno -> tipo sessione, focus, intervalli chiave
5. PROGRESSIONE: come cambia TSS e intensità settimana per settimana
6. SEGNALI DI ATTENZIONE: cosa monitorare

Mantieni il risposta tecnica, basata sui dati, e pratica."""

# ── Helper: mappatura fenotipo → raccomandazioni ─────────────────────────

PHENOTYPE_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "Sprinter": {
        "primary_focus": "Potenza massimale e ripetizioni brevi",
        "training_method": "HIIT + ripetizioni 30s-2min",
        "key_metrics": "Peak power, W' residual",
        "avoid": "Lunghi sforzi aerobici > 60min",
    },
    "Pursuiter": {
        "primary_focus": "Potenza media alta 10-40min",
        "training_method": "Tempo trial + threshold intervals",
        "key_metrics": "Power at 10min, 20min, 40min",
        "avoid": "Sforzi puramente anaerobici < 30s",
    },
    "All-Rounder": {
        "primary_focus": "Bilanciato su tutti gli aspetti",
        "training_method": "Polarized base + pyramidal blocks",
        "key_metrics": "CP/W' balance, all-round power",
        "avoid": "Specializzazione eccessiva in un solo dominio",
    },
    "Time-Trialist": {
        "primary_focus": "Potenza sostenuta 1+ ora",
        "training_method": "Time trials + sweet spot",
        "key_metrics": "Power at 20min, 60min",
        "avoid": "Intervalli troppo brevi < 5min",
    },
    "Climber": {
        "primary_focus": "Potenza rapporto peso",
        "training_method": "Sali + ripetizioni in pendenza",
        "key_metrics": "Power/kg at 5min, 20min",
        "avoid": "Piani pianeggianti ad alta velocità",
    },
    "Rouleur": {
        "primary_focus": "Potenza costante su piano",
        "training_method": "Long efforts steady state",
        "key_metrics": "Power at 20min, 60min",
        "avoid": "Troppi cambi intensità improvvisi",
    },
}


def get_phenotype_recommendation(phenotype_primary: str) -> dict[str, str]:
    """Restituisce le raccomandazioni di training per il fenotipo specifico."""
    return PHENOTYPE_RECOMMENDATIONS.get(
        phenotype_primary,
        PHENOTYPE_RECOMMENDATIONS["All-Rounder"],
    )


# ── Prompt di valutazione ────────────────────────────────────────────────

def build_friel_assessment(
    total_tss: float,
    ctl: float,
    atl: float,
    tsb: float,
    pi: float,
    phenotype: str,
    phase: str,
    durability: str,
) -> str:
    """Costruisce un'assessment completo in stile Friel.

    Restituisce un testo pronto all'uso per l'AI Coach.
    """
    lines = [
        "=== ASSESSMENT FRIEL ===",
        f"TSS Settimanale: {total_tss:.0f}",
        f"CTL (Forma): {ctl:.1f}",
        f"ATL (Fatica): {atl:.1f}",
        f"TSB (Balance): {tsb:.1f}",
        "",
        f"STato forma: {('Ottimale' if -10 <= tsb <= 10 else 'Attenzione' if tsb < -10 else 'Overtraining risk')} (TSB {tsb:.1f})",
        f"Polarizzazione PI: {pi:.2f} ({'Polarized' if pi > 2.0 else 'Mixed/Balanced'})",
        f"Fenotipo: {phenotype}",
        f"Fase training: {phase}",
        f"Durabilità: {durability}",
        "",
        "=== RACCOMANDAZIONI ===",
    ]

    # Aggiungi raccomandazioni fenotipo-specifiche
    recs = get_phenotype_recommendation(phenotype)
    lines.append(f"Focus principale: {recs['primary_focus']}")
    lines.append(f"Metodo consigliato: {recs['training_method']}")

    # TSB-based recommendations
    if tsb > 15:
        lines.append("⚠️ Sovrallenamento: ridurre carico settimanale del 15-20%")
    elif tsb < -15:
        lines.append("⚠️ Sotto-carico: considerare aumento progressivo carico")
    else:
        lines.append("✅ Carico nella zona verde: mantenere strategia attuale")

    lines.append("")
    lines.append("=== LAVORI CHIAVE SETTIMANA ===")
    # Semplicistico: suggerimenti basati metodo
    if pi > 2.0:
        lines.append("- 2x ripetizioni 10min @ threshold (95-99% LTHR)")
        lines.append("- 1x lungo weekend Z2")
    else:
        lines.append("- 2x intervalli 5min @ VO2max (~102% LTHR)")
        lines.append("- 2x ripetizioni 3min @ threshold")
        lines.append("- 1x lungo weekend Z2")

    lines.append("")
    lines.append("=== SEGNALI DI OSSERVAZIONE ===")
    if durability == "developing":
        lines.append("- Monitorare durabilità settimanalmente")
    if tsb > 10:
        lines.append("- Monitorare HRV mattutina e RPE quotidiano")
    lines.append("")

    return "\n".join(lines)
