# API Endpoints

Riferimento completo di tutti gli endpoint HTTP di Cycling Performance Studio Lab.

**Base URL:** `http://127.0.0.1:22400`

**Totale: 224 endpoints** (191 in app.py + 5 in session_manager.py + 2 in gpx_parser.py + 28 in pcc_routes_v2.py)

---

## Autenticazione

Tutti gli endpoint API sono accessibili senza autenticazione in modalita sviluppo.
Per la produzione, implementare middleware di autenticazione personalizzato.

---

## Indice

1. [Version & Health](#version--health)
2. [Dashboard](#dashboard)
3. [Profiles](#profiles)
4. [Fitness](#fitness)
5. [Training Plan](#training-plan)
6. [Analysis](#analysis)
7. [HRV](#hrv)
8. [Nutrition](#nutrition)
9. [BIA & Body](#bia--body)
10. [Strength & Mobility](#strength--mobility)
11. [Field Tests](#field-tests)
12. [CP Models](#cp-models)
13. [Activity Insights](#activity-insights)
14. [Injury](#injury)
15. [Calendar](#calendar)
16. [Export](#export)
17. [Sync Targets](#sync-targets)
18. [Custom Charts](#custom-charts)
19. [Huawei HRV](#huawei-hrv)
20. [Terra](#terra)
21. [Onboarding](#onboarding)
22. [Upstream](#upstream)
23. [Sessions](#sessions)
24. [GPX](#gpx)
25. [Workouts](#workouts)
26. [Courses](#courses)
27. [Settings](#settings)

---

## Version & Health

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/version` | 200 | Versione app (app: "cpsl") |
| GET | `/api/diag/health` | 200 | Health check |

---

## Dashboard

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/dashboard/home` | 200 | Home dashboard con TID heatmap, daily adapt, strength, calendar |
| GET | `/api/activity-insights` | 200 | Insights ultima sessione |

---

## Profiles

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/profiles` | 200 | Lista tutti i profili |
| POST | `/api/profiles` | 201 | Crea nuovo profilo |
| POST | `/api/profiles/{id}/switch` | 200 | Cambia profilo attivo |
| DELETE | `/api/profiles/{id}` | 200 | Elimina profilo |
| GET | `/api/profiles/{id}/athlete` | 200 | Ottieni dati atleta |
| POST | `/api/profiles/{id}/athlete` | 200 | Salva dati atleta |
| POST | `/api/profiles/{id}/env` | 200 | Salva credenziali .env |
| GET | `/api/profile` | 200 | Profilo atleta corrente |

---

## Fitness

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| POST | `/api/fitness/estimate-ftp` | 200 | Stima FTP dai best efforts |
| POST | `/api/fitness/signature` | 200 | Calcola firma fitness completa |
| POST | `/api/fitness/cp-wprime` | 200 | Analisi CP/W' Monod-Scherrer |
| POST | `/api/fitness/power-curve` | 200 | Curva potenza personalizzata |
| POST | `/api/fitness/aerobic-decoupling` | 200 | Analisi decoupling aerobico |
| POST | `/api/fitness/ramp-test` | 200 | Advisory ramp test FTP |
| GET | `/api/fitness/readiness` | 200 | Readiness score composito |
| GET | `/api/fitness/strain` | 200 | Strain score ultima sessione |

---

## Training Plan

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/plan` | 200 | Piano corrente |
| POST | `/api/plan/generate` | 200 | Genera nuovo piano |
| POST | `/api/plan/recalculate` | 200 | Ricalcola piano esistente |
| POST | `/api/plan/adjust` | 200 | Aggiustamento manuale |
| DELETE | `/api/plan` | 200 | Elimina piano |
| POST | `/api/plan/re-draw` | 200 | Ridisegna settimana |
| POST | `/api/plan/taper` | 200 | Applica taper |
| GET | `/api/plan/block-model` | 200 | Raccomandazioni blocchi |
| GET | `/api/plan/daily-adjust` | 200 | Adjustment giornaliero |
| POST | `/api/plan/delete-session` | 200 | Elimina sessione dal piano |

---

## Analysis

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/analysis/latest` | 200 | Analisi ultima sessione |
| GET | `/api/analysis/history` | 200 | Storico analisi |
| GET | `/api/analysis/weekly-summary` | 200 | Riepilogo settimanale |
| GET | `/api/analysis/tid-weekly` | 200 | TID (Training Impact Distribution) settimanale |

---

## HRV

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/hrv/summary` | 200 | Riepilogo HRV |
| GET | `/api/hrv/daily` | 200 | Dati HRV giornalieri |
| GET | `/api/hrv/trend` | 200 | Trend HRV |
| GET | `/api/hrv/baseline` | 200 | Baseline HRV |

---

## Nutrition

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/nutrition-full` | 200 | Piano nutrizionale completo |
| GET | `/api/nutrition/macros` | 200 | Macro giornalieri |
| GET | `/api/nutrition/supplements` | 200 | Raccomandazioni integratori |
| GET | `/api/diet` | 200 | Piano alimentare |
| GET | `/api/diet-weekly` | 200 | Piano alimentare settimanale |

---

## BIA & Body

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/bia/history` | 200 | Storico BIA |
| GET | `/api/bia/latest` | 200 | Ultimo lettura BIA |
| POST | `/api/bia/import` | 200 | Importa BIA da PDF |
| POST | `/api/bia/manual` | 200 | Inserimento manuale BIA |
| GET | `/api/bia-history` | 200 | Storico BIA (alias) |

---

## Strength & Mobility

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/strength-plan` | 200 | Piano forza |
| GET | `/api/strength/summary` | 200 | Riepilogo forza per fase |
| GET | `/api/mobility-plan` | 200 | Piano mobilita |
| GET | `/api/mobility/today` | 200 | Routine mobilita oggi |

---

## Field Tests

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/field-test/protocols` | 200 | Lista protocolli test campo |
| GET | `/api/field-test/{id}` | 200 | Dettaglio protocollo |
| POST | `/api/field-test/start` | 200 | Inizia test |
| POST | `/api/field-test/complete` | 200 | Completa test |

---

## CP Models

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/cp-models` | 200 | Modelli CP disponibili |
| POST | `/api/cp-models/fit` | 200 | Fitta modello CP |
| GET | `/api/cp-models/latest` | 200 | Ultimo modello CP |

---

## Activity Insights

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/activity-insights` | 200 | Insights sessione |
| POST | `/api/activity/rpe` | 200 | Log RPE per sessione |
| GET | `/api/activity/rpe-history` | 200 | Storico RPE |

---

## Injury

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/injuries` | 200 | Lista infortuni |
| POST | `/api/injuries` | 201 | Crea infortunio |
| GET | `/api/injuries/{id}` | 200 | Dettaglio infortunio |
| PUT | `/api/injuries/{id}` | 200 | Aggiorna infortunio |
| DELETE | `/api/injuries/{id}` | 200 | Elimina infortunio |
| GET | `/api/injuries/summary` | 200 | Riepilogo infortuni |
| GET | `/api/injury/blocks` | 200 | Blocchi infortunio attivi |

---

## Calendar

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/calendar.ics` | 200 | Esporta piano in formato ICS |

---

## Export

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/export/backup` | 200 | Backup completo profilo |
| GET | `/api/export/bundle` | 200 | Bundle ZIP con tutti i dati |
| GET | `/api/export/metrics-csv` | 200 | Metriche in formato CSV |

---

## Sync Targets

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/sync-targets` | 200 | Lista sync targets disponibili |
| GET | `/api/sync-targets/{id}` | 200 | Dettaglio sync target |
| POST | `/api/sync-targets/{id}/push` | 200 | Push dati a target |
| POST | `/api/sync-targets/{id}/pull` | 200 | Pull dati da target |

---

## Custom Charts

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/custom-charts` | 200 | Lista grafici custom |
| POST | `/api/custom-charts` | 201 | Crea grafico custom |
| PUT | `/api/custom-charts/{id}` | 200 | Aggiorna grafico |
| DELETE | `/api/custom-charts/{id}` | 200 | Elimina grafico |

---

## Huawei HRV

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/huawei/status` | 200 | Stato connessione Huawei |
| GET | `/api/huawei/hrv/summary` | 200 | Riepilogo HRV Huawei |
| GET | `/api/huawei/hrv/daily` | 200 | Dati HRV giornalieri Huawei |
| GET | `/api/huawei/hrv/export` | 200 | Esporta HRV Huawei |
| GET | `/api/huawei/hrv/debug` | 422* | Debug dati HRV (richiede query params) |
| POST | `/api/huawei/import` | 200 | Importa dati Huawei |
| GET | `/api/huawei/devices` | 200 | Lista dispositivi Huawei |
| GET | `/api/huawei/activities` | 200 | Attivita Huawei |

---

## Terra

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/terra/status` | 500* | Stato Terra (richiede credenziali) |
| POST | `/api/terra/auth` | 200 | Genera URL auth Terra |
| POST | `/api/terra/callback` | 200 | Callback Terra OAuth |
| POST | `/api/terra/disconnect` | 200 | Disconnetti Terra |
| GET | `/api/terra/data` | 200 | Dati Terra |

*\* 500 = nessuna credenziale Terra configurata (expected)*

---

## Onboarding

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/onboarding/status` | 500* | Stato onboarding |
| POST | `/api/onboarding/complete` | 200 | Completa onboarding |
| POST | `/api/onboarding/skip` | 200 | Skip onboarding |

*\* 500 = nessun dato onboarding (expected)*

---

## Upstream

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/upstream/check` | 200 | Verifica aggiornamenti |

---

## Sessions (session_manager.py)

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/sessions` | 200 | Lista sessioni |
| POST | `/api/sessions` | 201 | Crea sessione |
| GET | `/api/sessions/{id}` | 200 | Dettaglio sessione |
| PUT | `/api/sessions/{id}` | 200 | Aggiorna sessione |
| GET | `/api/audit-log` | 200 | Audit log |

---

## GPX (gpx_parser.py)

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| POST | `/api/gpx/import` | 200 | Upload e parsing file GPX |
| GET | `/api/gpx/activities` | 200 | Attivita GPX importate |

---

## Workouts

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/workouts` | 200 | Libreria workout |
| GET | `/api/workouts/{id}` | 200 | Dettaglio workout |
| POST | `/api/workouts/import` | 200 | Importa workout |
| GET | `/api/workouts/stats` | 200 | Statistiche libreria |

---

## Courses

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/courses` | 200 | Lista percorsi |
| GET | `/api/courses/{id}` | 200 | Dettaglio percorso |
| POST | `/api/courses` | 201 | Crea percorso |
| PUT | `/api/courses/{id}` | 200 | Aggiorna percorso |
| DELETE | `/api/courses/{id}` | 200 | Elimina percorso |

---

## Settings

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/settings` | 200 | Impostazioni correnti |
| PUT | `/api/settings` | 200 | Aggiorna impostazioni |
| POST | `/api/settings/icu` | 200 | Salva credenziali ICU |
| GET | `/api/settings/icu/status` | 200 | Stato connessione ICU |

---

## Metabolic Profile

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/metabolic-profile` | 200 | Profilo metabolico |

---

## Recommendations

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/athlete/recommendations` | 200 | Raccomandazioni personalizzate |

---

## Pedal Asymmetry

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/pedal-latest` | 200 | Ultima lettura asimmetria |
| GET | `/api/pedal-history` | 200 | Storico asimmetria |

---

## CPEP (CP Event Protocol)

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/cpep-latest` | 200 | Ultimo CPEP record |

---

## Route Analysis

| Method | Path | Status | Descrizione |
|--------|------|--------|-------------|
| GET | `/api/route-wprime` | 422* | Analisi W' per percorso (richiede query params) |

*\* 422 = parametri query mancanti (expected)*

---

## Errori Comuni

| Status | Significato |
|--------|-------------|
| 200 | Successo |
| 404 | Endpoint non trovato |
| 422 | Parametri mancanti o non validi |
| 500 | Errore interno (spesso expected: nessun dato/credenziali) |

---

## Note

- **Base URL**: `http://127.0.0.1:22400`
- **Formato risposta**: JSON (tranne `/api/calendar.ics` che ritorna `text/calendar`)
- **CORS**: Abilitato per tutti gli origin
- **Autenticazione**: Nessuna in modalita sviluppo
- **Docs**: `http://127.0.0.1:22400/docs` (Swagger UI) e `http://127.0.0.1:22400/redoc` (ReDoc)
