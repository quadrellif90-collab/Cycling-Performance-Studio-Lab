# Release v1.4.7 — Analisi statica completa + hardening

CPSL v1.4.7 chiude il ciclo di analisi statica e di sicurezza avviato con la
suite di tooling (ruff, bandit, radon, pytest) su tutto il codebase.

## Correzioni

### NameError latenti (F821)
- `pcc_routes_v2.py`: 15 global di app (`cached`, `db`, `config`, `tp`,
  `api_activities`, …) referenziate ma mai definite → iniettore di contesto a
  registration + placeholder dichiarati. Diverse route PCC erano NameError
  garantiti a runtime.
- `missing_routes.py`: import mancanti nei 3 endpoint HRV avanzati.
- `ai_coach/plan_generator.py`: chiamava una classe inesistente
  (`WeeklyLoadRecommendations`); ora usa il planner nativo reale
  (`generate_adaptive_recommendation`).
- `ai_coach/weekly_analysis.py`: `detect_phase` → `detect_training_phases`
  con costruzione delle weekly summaries.
- `huawei_api.py`: un decorator Flask-legacy rompeva l'import dell'intero
  modulo → gli endpoint HRV manuale Huawei sono di nuovo raggiungibili.
- `hrv_engine.py`, `training.py`, `app.py`: logger, pathlib, json locali.

### Closure catturate nel loop (B023 ×21)
Tutte le funzioni/lambda definite in loop che catturavano variabili di
iterazione ora le legano via default args — comportamento identico, codice
blindato contro refactor futuri.

### Sicurezza (bandit)
- Hash SHA1/MD5 non-security (seed RNG, cache key): `usedforsecurity=False`.
- Lancio .bat auto-update: eliminato `shell=True` (`cmd.exe /c` esplicito).
- Risultato: **0 finding HIGH** nel codice proprietario.

### API
- `/api/nutrition/daily-targets`: 500 → 200 (firme corrette di
  `day_macros`/`supplement_doses`, mapping phase→day_type).

## Verifica scientifica (fonti online 2024–2026)
| Algoritmo CPSL | Riferimento | Esito |
|---|---|---|
| CTL τ=42d, ATL τ=7d, TSB=CTL−ATL | Coggan PMC / Banister | ✅ |
| TSS = t·IF²·100, IF=NP/FTP | TrainingPeaks standard | ✅ |
| DFA α1 soglie 0.75 (VT1) / 0.5 (VT2), scale 4–16 battiti | Rogers et al. 2020-21, review CHF 2025 | ✅ |
| Fueling 60–90 g/h, 2:1 glucosio:fruttosio | Jeukendrup; consensus 2025-26 | ✅ |
| Polarizzato per élite, piramidale/soglia per amatori | Meta-analisi Sports Medicine 2024-25 | ✅ già calibrato |
| Durability = ratio fresh/tired power su ride ≥2h | Xert-style, letteratura durability | ✅ |

Nota minore: finestra DFA α1 di default 64 battiti vs ~120 (2 min) degli studi
originali — stima leggermente più rumorosa ma nella gamma delle implementazioni
pratiche (HRV Logger, Runalyze); documentata come scelta consapevole.

## Quality gates
- ruff F821/B023: 0 · bandit HIGH: 0 · radon survey completata
- pytest: 285/285 · QA A→Z: 25/25 · sweep console: pulita

**Download**: `CyclingPerformanceStudioLab-v1.4.7-win-x64.zip`
