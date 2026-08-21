# CPSL v1.4.0 — Science Update

**Tipo:** feature release · **Fonte:** sintesi delle evidenze scientifiche 2024-2026 in endurance, nutrizione, recupero e forza → [`docs/SCIENCE_UPDATES_2025.md`](docs/SCIENCE_UPDATES_2025.md)

## 🍎 Fueling Planner — la "fueling revolution"
- Piano CHO/ora per sessione dalla tabella evidence-based (fino a 90-120 g/h con miscele multi-trasportatore glucosio+fruttosio+galattosio)
- **Gut training progressivo**: +10-15 g/h ogni 2 settimane verso il tuo target, con piano prese ogni ~22 min
- **Recupero 3:1** (CHO:proteine) entro 45 min calcolato su peso e durata
- Esempio reale (180' moderate, 72 kg): target 75 g/h → 60 g/h effettivi secondo il tuo gut training · recupero 86 g CHO + 29 g PROT

## 💪 4 workout Durability (evidenze Muriel 2022, Spragg 2023)
| Sessione | Struttura |
|----------|-----------|
| Negative Split 120' | 2h con ultimi 40' a Z3 su gambe stanche |
| Late Hill Reps 105' | 60' Z2 + 4×5' @100% FTP a fatica accumulata |
| Prefatigued Intervals 150' | 3×8' @106% all'inizio, poi lunga Z2 nelle condizioni ottimali di ossidazione grassi |
| Muscular Endurance 90' | 3×15' Z3 continuativo |

## 📶 Alert instabilità HRV da CV
Il coefficiente di variazione 7g vs 28g è l'allarme precoce più sensibile dell'affaticamento accumulato; deviazioni bidirezionali (HRV paradossalmente alta = possibile saturazione parasimpatica). Integrato nel digest giornaliero.

## 🎯 Calibrazione livello atleta nel planner
Rivera-Köfler 2025 (JSCR): il vantaggio polarizzato è élite-only. Con `athlete_level=amateur` il planner suggerisce pyramidal equipollente; elite/trained mantengono polarized.

## 🌡️ Protocollo heat training
Per eventi in clima caldo a 14-30 giorni, il countdown gara suggerisce l'acclimatazione 10 giorni (VO2max +5-8%, TT +6-8% anche al fresco).

## 🕘 Cronologia versioni piano
Le ultime 7 snapshot del piano consultabili e ripristinabili dal tab Plan ("🕘 Cronologia"). Restore validato e sicuro: il piano attuale viene ruotato in .bak, mai perso.

## 📚 Documentazione
- Nuovo: `docs/SCIENCE_UPDATES_2025.md` — sintesi citata delle evidenze implementate
- Portati dal lignaggio PCC: SCIENCE, SCIENCE_REVIEW, SYSTEM, DEBUGGING, HUAWEI_HRV, OCR_SETUP, RESEARCH_TRAINING_PLANNER, windows_build, workout_sources
- README GitHub completamente riscritto

## ✅ Verifiche
Fueling endpoint live ✓ · adaptive amateur→pyramidal / elite→polarized ✓ · CV alert robusto su dati parziali ✓ · 4 ZWO parsati dal player CPSL ✓ · suite completa verde (246 test) · JS validato Node ✓
