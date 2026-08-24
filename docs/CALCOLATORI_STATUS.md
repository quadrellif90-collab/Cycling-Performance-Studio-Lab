# Stato calcolatori CPSL — Audit vs letteratura (2024–2026)

Audit completo dei moduli di calcolo/fisiologia di CPSL e allineamento alle
recenti pubblicazioni. Tutte le modifiche sono **additive o backward-compatible**
(niente rotture di API/schema); dove possibile è stato mantenuto il fallback.

## Migliorati in questa passata

| Modulo | Cambiamento | Riferimento |
|---|---|---|
| `advanced_metrics.fit_critical_power` (prima passata) | CP/W′ ora 3-parametri Morton non-lineare + fallback lineare 1/t | Morton 2006; Jones 2019 |
| `advanced_metrics.w_balance` | τ di recupero **time-varying** Skiba 2015: `τ = 546·exp(−0.01·(CP−P)) + 316 s` (prima fisso 228 s) | Skiba 2015 IJSPP |
| `advanced_metrics.dfa_alpha1` | α1 a **due scale** standard: short 4–16 / long 16–64 battiti (prima scala unica ampia) | Gronwald 2020 |
| `advanced_metrics.load_distribution` | raggruppamento esplicito Z1–2 / Z3–4 / Z5+ e classificazione polarizzato vs **Seiler 80/20** | Seiler & Kjerland 2006 |
| `breakthrough_detector` | ricostituzione W′ corretta (era "~33%/s", fisicamente errata) → esponenziale Skiba coerente con `w_balance` | Skiba 2015 |
| `durability_score` | picco "tired" ancorato sul **lavoro cumulato (kJ ≥1500)** invece che sul solo tempo, con fallback temporale | Muriel 2022; Valenzuela 2022; Pinot 2014 |
| `hrv_engine` | percorso **ln(RMSSD)** in baseline e deviazione (scala statisticamente preferita) accanto a RMSSD grezzo | Shaffer & Ginsberg 2017; Buchheit 2014 |
| `tau_fitting` | soglia di accettazione NLS r² 0.40 → **0.50** (riduce fit rumorosi; fallback τ convenzionali invariato) | Hellard 2006 |

## Già allineati (nessuna modifica necessaria)

| Modulo | Stato |
|---|---|
| `strain_score` | Modello 3D Kontro 2026; usa già `τ=546·exp(−0.01·DCP)+316` → coerente con `advanced_metrics` |
| `espe` | Progressione sistemi energetici (concetto supportato da Kontro 2026); band/heuristic → mantenuto, aggiunto flag di affidabilità |
| `fitness_estimation` | FTP 0.95×20min (Valenzuela 2023); Monod 2P CP/W′; HIE/LTP euristici — mantenuto |
| `cp_models` | Morton 3P grid-search R²≥0.90 — mantenuto |
| `power_curve` | fatigue_resistance kJ-anchored (Pinot 2014) — già coerente con la nuova durability |
| `nutrition` | Periodizzazione carb 3–12 g/kg, 30–90 g/h during, supplementi — attuale (Burke 2018; Jeukendrup/UCI 2026) |
| `phenotype` | Radar vs ancore elite (euristico) — mantenuto |
| `route_archetypes` | Generazione procedurale euristica (no modello fisico gradiente→potenza) — accettabile per scopo UI |

## Note di attivazione
Le modifiche sono nel codice Python del backend. Per riflettersi nelle API del fork
(`/api/...`) è necessario **riavviare il server CPSL** (il processo su `:22400`
deve ricaricare i moduli). Il frontend MontisFork non richiede rebuild (nessun
cambiamento lato UI).

## Priorità future (non urgenti, rischio medio)
- Durability: esporre il punteggio kJ-ancorato anche in `power_curve.fatigue_resistance`.
- `route_archetypes`: derivare l'intensità reale da modello potenza (Crr, CdA, ρ).
- `phenotype`/`cp_models`: ricalibrare le ancore elite su Pinot & Grappe 2011 / Vallier 2015.
