# CPSL v1.5.0 — Montis port

Quattro nuovi moduli analitici ad alto valore, portati dai concetti di
Montis.icu (MIT) e ricalibrati sulle convenzioni CPSL.

## Novità

### 1. Progressione sistemi energetici (ESPE) — tab Analysis
Confronta la tua power curve degli ultimi 84 giorni con i precedenti 84:
- Delta per 1m / 5m / 20m / 60m → classificazione per sistema
  (anaerobico, VO2max, soglia, durabilità aerobica)
- Bias glicolitico (P1m/P20m, ideale ~1.8), balance score, detection plateau
- Profilo di curva: cronoman, all-rounder, scalatore, sprinter…

### 2. Repeatabilità anaerobica W′bal
Statistiche della settimana sulla depletazione W′bal per sessione:
media/max %, sessioni moderate (>50%) e alte (>60%), divergenza dalla
baseline endurance. Fonte: sync Intervals.icu; fallback stimato da kJ
sopra FTP + W′ locale.

### 3. Trend durabilità (decoupling firmato)
Classificazione settimanale del trend di resistenza dal decoupling
aerobico con evidenza ripetuta: improving / stable / drifting.

### 4. Decisione del giorno (governance ADE)
Punteggio trasparente da 100 con penalità/supporti itemizzati — HRV,
sonno, TSB, ramp rate, monotonia, taper, rischio — che produce una
directive chiara (carico completo → riposo) con motivazioni leggibili.
Il motore decide, l'AI spiega.

## Qualità
- Suite test completa: **304 passed** (19 nuovi)
- QA end-to-end dei 4 nuovi endpoint su server reale: OK
- Screenshot UI: `qa_shots/v150_analysis_cards.png`

## Attribuzione
Concetti adattati da intervalsicugptcoach-public © 2026 Clive King (MIT).
Vedi il file `NOTICE`.
