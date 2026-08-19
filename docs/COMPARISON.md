# Confronto Completo: Domestique vs PCC vs CPSL

Analisi dettagliata delle 3 applicazioni con gap analysis e raccomandazioni.

---

## Indice

1. [Panoramica Generale](#1-panoramica-generale)
2. [Confronto Features per Categoria](#2-confronto-features-per-categoria)
3. [Matrice Completa](#3-matrice-completa)
4. [Gap Analysis CPSL vs Domestique](#4-gap-analysis-cpsl-vs-domestique)
5. [Gap Analysis CPSL vs PCC](#5-gap-analysis-cpsl-vs-pcc)
6. [Features Uniche per App](#6-features-uniche-per-app)
7. [Raccomandazioni Prioritarie](#7-raccomandazioni-prioritarie)

---

## 1. Panoramica Generale

| Metrica | Domestique | PCC | CPSL (v0.6.0) |
|---------|-----------|-----|---------------|
| **Versione** | v4.x | v5.4.8 | v0.6.0 |
| **Framework** | FastAPI + pywebview | FastAPI + vanilla JS | FastAPI + vanilla JS |
| **Frontend** | 8 tab dashboard | SPA React + HTML | 13 tab dashboard |
| **API Routes** | ~180 | ~160 | 224 |
| **Moduli Python** | ~55 | ~50 | 68 |
| **Test** | 308 files | ~20 | 150 (6 files) |
| **Build** | DMG + AppImage + EXE | EXE only | DMG + AppImage + EXE |
| **Desktop** | pywebview nativo | No | pywebview (launcher.py) |
| **Licenza** | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| **Workout ZWO** | 1,753 bundled | ~50 | ~50 |
| **Route reali** | 50+ GPX | 0 | 0 |
| **OAuth ICU** | Completo | Completo | Completo |
| **Multi-profile** | Si | Si | Si |

---

## 2. Confronto Features per Categoria

### 2.1 Setup & Onboarding

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Setup wizard HTML | Si | Si | Si |
| ICU credential test | Si | Si | Si |
| Auto-detect athlete ID | Si | Si | Si |
| Folder picker nativo | Si | Si | Si |
| ICU HR auto-fetch | Si | Si | Si |
| Onboarding checklist | Si | Si | Si |
| **Profile reset** | Si | Si | **NO** |
| **Garmin sync check** | Si | Si | **NO** |

### 2.2 Profiles

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Multi-profile | Si | Si | Si |
| Profile create/delete | Si | Si | Si |
| Profile switch | Si | Si | Si |
| Profile color | Si | Si | Si |
| Bulk profile data | Si | Si | Si |
| **Profile reset (purge)** | Si | Si | **NO** |
| **Profile picker page** | Si | Si | **NO** |
| **Profile setup page** | Si | Si | **NO** |

### 2.3 Athlete Data & FTP

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| FTP history ledger | Si | Si | Si |
| FTP test recording | Si | Si | Si |
| eFTP auto-detect | Si | Si | Si |
| **FTP test type selection** | Si | Si | **NO** |
| **Rider stats card** | Si | Si | **NO** |
| **Tau fitting (NLS)** | Si | Si | **NO** |
| **Banister validation (OOS)** | Si | Si | **NO** |
| **Power curve (P&G baseline)** | Si | Si | **NO** |
| **Fatigue resistance (Pinot)** | Si | Si | **NO** |
| **Backfill history** | Si | Si | **NO** |
| **Backfill status polling** | Si | Si | **NO** |

### 2.4 Training Plan

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Plan generate | Si | Si | Si |
| Plan reforecast | Si | Si | Si |
| Plan regenerate | Si | Si | Si |
| Auto-adjust | Si | Si | Si |
| Add race | Si | Si | Si |
| Mark unavailable | Si | Si | Si |
| Move session | Si | Si | Si |
| Re-match workouts | Si | Si | Si |
| Re-draw session | Si | Si | Si |
| Preview/accept redraw | Si | Si | Si |
| Swap session type | Si | Si | Si |
| Delete session | Si | Si | Si |
| Dismiss session | Si | Si | Si |
| Daily adapt | Si | Si | Si |
| Auto-recalc | Si | Si | Si |
| Continuous deload revert | Si | Si | Si |
| Inject strength | Si | Si | Si |
| Inject multidiscipline | Si | Si | Si |
| Daily sync | Si | Si | Si |
| Weekly plan view | Si | Si | Si |
| Week summary | Si | Si | Si |
| Calendar data | Si | Si | Si |
| **Plan preview (dry-run)** | Si | Si | **Si** |
| **Entry scan** | Si | Si | **Si** |
| **Missed suggestions** | Si | Si | **Si** |
| **Plan adjusted (injury)** | Si | Si | **Si** |
| **Event projection** | Si | Si | **Si** |
| **Plan drift detection** | Si | Si | **Si** |
| **Recovery ramp** | Si | Si | **Si** |
| **Stepback/recovery week** | Si | Si | **Si** |
| **B/C race taper** | Si | Si | **Si** |
| **Drag-drop reorder** | Si | Si | **Si** |

### 2.5 Readiness & Wellness

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Readiness score (0-100) | Si | Si | Si |
| Composite readiness (0-10) | Si | Si | Si |
| Revert cap | Si | Si | Si |
| Apply tier-down | Si | Si | Si |
| Wellness data | Si | Si | Si |
| HRV4Training import | Si | Si | Si |
| Manual HRV entry | Si | Si | Si |
| HRV recording status | Si | Si | Si |
| HRV recording dismiss | Si | Si | Si |
| **3D fitness status** | Si | Si | **Si** |
| **Backfill 3D fitness** | Si | Si | **Si** |
| **Hooper composite** | Si | Si | **Si** |
| **Sleep inhibit** | Si | Si | **Si** |
| **Daily log (Hooper)** | Si | Si | **Si** |
| **Blood markers** | Si | Si | **Si** |
| **Metrics history** | Si | Si | **Si** |
| **Metrics latest** | Si | Si | **Si** |
| **Log metric** | Si | Si | **Si** |

### 2.6 Analysis & Power

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Power curve | Si | Si | Si |
| CP/W' analysis | Si | Si | Si |
| CP models (Morton) | Si | Si | Si |
| Metabolic profile | Si | Si | Si |
| Activity insights | Si | Si | Si |
| Activity RPE | Si | Si | Si |
| TID weekly | Si | Si | Si |
| **Energy system breakdown** | Si | Si | **Si** |
| **Tau-fit panel** | Si | Si | **Si** |
| **Banister validation** | Si | Si | **Si** |
| **Rider stats grid** | Si | Si | **Si** |
| **Season totals** | Si | Si | **Si** |
| **PR detection** | Si | Si | **Si** |
| **PR toast queue** | Si | Si | **Si** |
| **Execution score** | Si | Si | **Si** |
| **Structure fidelity** | Si | Si | **Si** |
| **Custom charts** | Si | Si | Si |
| **Rider profile stats** | Si | Si | **Si** |

### 2.7 DFA Alpha-1

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| DFA alpha1 tab | Si | Si | Si |
| HRVT1/HRVT2 thresholds | Si | Si | Si |
| Per-ride alpha1 curves | Si | Si | Si |
| DFA backfill | Si | Si | Si |
| DFA backfill status | Si | Si | Si |
| DFA backfill cancel | Si | Si | Si |
| **Aggregate view** | Si | Si | **Si** |
| **Algorithm versioning** | Si | Si | **Si** |

### 2.8 Nutrition & Diet

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Nutrition full | **NO** | Si | Si |
| Nutrition auto | **NO** | Si | Si |
| Diet plan | **NO** | Si | Si |
| Diet weekly | **NO** | Si | Si |
| Diet PDF import | **NO** | Si | Si |
| Supplement doses | **NO** | Si | Si |
| **Nutrition periodization** | **NO** | Si | **NO** |

### 2.9 Body Composition (BIA)

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| BIA import | **NO** | Si | Si |
| BIA history | **NO** | Si | Si |
| BIA sync ICU | **NO** | Si | Si |
| **BIA Vision (Cloud OCR)** | **NO** | Si | **NO** |
| **BIA manual entry** | **NO** | Si | **NO** |
| **Diet parser** | **NO** | Si | **NO** |

### 2.10 Strength & Mobility

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Strength plan | **NO** | Si | Si |
| Mobility plan | **NO** | Si | Si |
| Inject strength | **NO** | Si | Si |
| **Inject multidiscipline** | **NO** | Si | **NO** |
| **Strength periodization** | **NO** | Si | **NO** |

### 2.11 Workout Library

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Workout browse | Si | Si | Si |
| Workout tags | Si | Si | Si |
| Workout import | Si | Si | Si |
| Workout download | Si | Si | Si |
| Workout picker | Si | Si | Si |
| Bulk segments | Si | Si | Si |
| **Workout classification (16 types)** | Si | Si | **NO** |
| **Content-based classification** | Si | Si | **NO** |
| **Outdoor variant option** | Si | Si | **NO** |
| **Tokenized search** | Si | Si | **NO** |

### 2.12 Routes & Courses

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Real-world routes | Si | Si | Si |
| Virtual routes | Si | Si | Si |
| Route suggest | Si | Si | Si |
| Route regions | Si | Si | Si |
| Route surfaces | Si | Si | Si |
| Route profile | Si | Si | Si |
| Route W' | Si | Si | Si |
| Climb workout | Si | Si | Si |
| **Route archetypes (220+)** | Si | Si | **NO** |
| **Surface timeline** | Si | Si | **NO** |
| **Finish type filter** | Si | Si | **NO** |
| **Loop-only toggle** | Si | Si | **NO** |
| **Elevation gradient coloring** | Si | Si | **NO** |

### 2.13 Intervals.icu Integration

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| OAuth flow | Si | Si | Si |
| Disconnect | Si | Si | Si |
| Connection status | Si | Si | Si |
| Calendar push | Si | Si | Si |
| Push workout | Si | Si | Si |
| Athlete numbers | Si | Si | Si |
| **Sync status** | Si | Si | **NO** |
| **Sync progress** | Si | Si | **NO** |
| **Debounced push** | Si | Si | **NO** |
| **Daily reconcile** | Si | Si | **NO** |
| **Garmin auto-pull** | Si | Si | **NO** |

### 2.14 Huawei & Terra

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Huawei HRV daily | Si | Si | Si |
| Huawei HRV export | Si | Si | Si |
| Huawei HRV summary | Si | Si | Si |
| Huawei HRV debug | Si | Si | Si |
| Huawei import | Si | Si | Si |
| Terra status | **NO** | Si | Si |
| Terra OAuth | **NO** | Si | Si |
| Terra sync | **NO** | Si | Si |
| Terra disconnect | **NO** | Si | Si |
| **Huawei HRV manual** | Si | Si | **NO** |
| **Health Sync normalize** | Si | Si | **NO** |

### 2.15 Export & Calendar

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| ICS calendar | Si | Si | Si |
| Export backup | Si | Si | Si |
| Export bundle | Si | Si | Si |
| Export plan HTML | Si | Si | Si |
| **Export metrics CSV** | Si | Si | **NO** |
| **Export FIT workout** | Si | Si | **NO** |
| **Programme summary PNG** | Si | Si | **NO** |
| **Ride report PNG** | Si | Si | **NO** |
| **My calendar** | Si | Si | **NO** |
| **My push plan** | Si | Si | **NO** |

### 2.16 Settings & System

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Settings get/save | Si | Si | Si |
| HR zones save | Si | Si | Si |
| Version | Si | Si | Si |
| Health check | Si | Si | Si |
| Error ring buffer | Si | Si | Si |
| Frontend error capture | Si | Si | Si |
| Server logs | Si | Si | Si |
| Migration check | Si | Si | Si |
| **Update check** | Si | Si | **NO** |
| **Self-update** | Si | Si | **NO** |
| **GC status** | Si | Si | **NO** |
| **Programme summary** | Si | Si | **NO** |

### 2.17 Rides & Activities

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| List rides | Si | Si | Si |
| Ride detail | Si | Si | Si |
| Ride FIT download | Si | Si | Si |
| Delete ride | Si | Si | Si |
| Import FIT | Si | Si | Si |
| Activity RPE | Si | Si | Si |
| Ride PRs | Si | Si | Si |
| Recompute PRs | Si | Si | Si |
| **Ride analytics** | Si | Si | **NO** |
| **Decoupling analysis** | Si | Si | **NO** |
| **Efficiency factor** | Si | Si | **NO** |
| **Race flag toggle** | Si | Si | **NO** |
| **PR toast queue** | Si | Si | **NO** |

### 2.18 Injury & Field Tests

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Injury blocks CRUD | Si | Si | Si |
| Injury plan adjust | Si | Si | Si |
| Field test protocols | **NO** | Si | Si |
| Field test estimate | **NO** | Si | Si |
| Field test history | **NO** | Si | Si |
| **Pedal asymmetry** | **NO** | Si | **NO** |
| **CPEP import** | **NO** | Si | **NO** |

---

## 3. Matrice Completa

### Features Presenti in Tutte e 3 (38)

1. Setup wizard + ICU test
2. Multi-profile management
3. FTP history + test recording
4. Plan generate / reforecast / auto-adjust
5. Re-match / re-draw sessions
6. Add race / mark unavailable
7. Daily adapt / auto-recalc
8. Continuous deload revert
9. Readiness score (0-100 + 0-10)
10. Revert cap + tier-down
11. Wellness data (HRV/sleep/RHR)
12. HRV4Training import + manual HRV
13. Power curve
14. CP/W' analysis + CP models
15. Metabolic profile
16. Activity insights + RPE
17. TID weekly
18. DFA alpha1 tab + HRVT1/HRVT2
19. DFA backfill + status + cancel
20. Workout browse/tags/import/download
21. Workout picker
22. Bulk segments
23. Real-world + virtual routes
24. Route suggest/regions/surfaces/profile
25. Route W' + climb workout
26. ICU OAuth + disconnect + push
27. Push workout + athlete numbers
28. Huawei HRV (daily/export/summary/debug/import)
29. ICS calendar + export backup/bundle
30. Settings get/save + HR zones
31. Version + health check + error ring buffer
32. List rides + ride detail + FIT download
33. Delete ride + import FIT + activity RPE
34. Ride PRs + recompute PRs
35. Injury blocks CRUD
36. Custom charts
37. Calendar data
38. Inject strength

### Features Solo in Domestique e CPSL (non in PCC originale)

- Workout classification (16 content types)
- Route archetypes (220+ procedural routes)
- Surface timeline visualization
- Finish type filter
- Elevation gradient coloring
- Outdoor variant option
- Tokenized search
- Drag-drop session reorder
- Plan drift detection
- Recovery ramp
- Stepback/recovery week
- B/C race taper
- Sleep inhibit
- Daily log (Hooper composite)
- Blood markers
- Metrics history/latest/log
- Programme summary PNG
- Ride report PNG
- My calendar / My push plan
- Export metrics CSV
- Export FIT workout
- Update check / Self-update
- GC status
- PR detection + toast queue
- Ride analytics (decoupling, EF)
- Race flag toggle
- Sync status/progress
- Debounced push / Daily reconcile
- Garmin auto-pull
- Profile reset
- Profile picker/setup pages
- Plan preview (dry-run)
- Entry scan
- Missed suggestions
- Event projection
- Aggregate DFA view
- Algorithm versioning

### Features Solo in PCC e CPSL (non in Domestique originale)

- Nutrition full/auto/diet/diet-weekly
- Diet PDF import + supplements
- BIA import/history/sync ICU
- Strength plan + mobility plan
- Inject multidiscipline
- Field test protocols/estimate/history
- Terra integration (OAuth/sync/disconnect)
- PlanOptions selector (9 layers)
- Pedal asymmetry / CPEP import

### Features Solo in CPSL (unique)

- 13-tab dashboard (vs 8 in Domestique)
- HRV tab dedicato
- Nutrition tab dedicato
- BIA tab dedicato
- Profile tab dedicato
- What's New tab
- TID heatmap su home
- Daily adapt card su home
- Strength card su home
- Calendar card su home
- Assessment banner
- 150 tests (vs 308 in Domestique, ~20 in PCC)

---

## 4. Gap Analysis CPSL vs Domestique

### Gap Critici (Features Domestique mancanti in CPSL)

| # | Feature | Impatto | Sforzo |
|---|---------|---------|--------|
| 1 | **Workout classification (16 types)** | Alto | Medio |
| 2 | **Route archetypes (220+ procedural)** | Alto | Alto |
| 3 | **Surface timeline + finish type** | Medio | Medio |
| 4 | **Programme summary PNG** | Medio | Medio |
| 5 | **Ride report PNG** | Basso | Medio |
| 6 | **Export metrics CSV** | Medio | Basso |
| 7 | **Export FIT workout** | Medio | Medio |
| 8 | **My calendar / My push plan** | Basso | Basso |
| 9 | **Update check / Self-update** | Medio | Medio |
| 10 | **Ride analytics (decoupling, EF)** | Alto | Medio |
| 11 | **Race flag toggle** | Basso | Basso |
| 12 | **Sync status/progress** | Medio | Basso |
| 13 | **Debounced push / Daily reconcile** | Medio | Medio |
| 14 | **Profile reset** | Medio | Basso |

### Gap Non Critici (features simili o marginali)

- Workout ZWO bundled (Domestique ha 1,753, CPSL ~50) — risolvibile copiando
- Route GPX bundled (Domestique ha 50+, CPSL 0) — risolvibile copiando
- Domestique ha `scripts/` con utility (classify, surface mapper, route profiles) — CPSL no

---

## 5. Gap Analysis CPSL vs PCC

### Gap Critici (Features PCC mancanti in CPSL)

| # | Feature | Impatto | Sforzo |
|---|---------|---------|--------|
| 1 | **Pedal asymmetry (LEOMO MPI)** | Alto | Basso |
| 2 | **CPEP import** | Medio | Basso |
| 3 | **BIA Vision (Cloud OCR)** | Alto | Medio |
| 4 | **BIA manual entry** | Medio | Basso |
| 5 | **Diet parser (PDF OCR)** | Medio | Medio |
| 6 | **Nutrition periodization** | Medio | Medio |
| 7 | **Inject multidiscipline** | Alto | Medio |
| 8 | **Strength periodization detail** | Medio | Basso |
| 9 | **PlanOptions selector (9 layers)** | Medio | Medio |
| 10 | **Huawei HRV manual** | Basso | Basso |
| 11 | **Health Sync normalize** | Basso | Basso |

### Note

CPSL ha gia' integrato la maggior parte delle features PCC. I gap rimanenti sono:
- Moduli non ancora importati: `pedal_asymmetry` e `cpep_import` sono gia' nel codice ma i route non sono tutti testati
- BIA Vision e' in `bia_vision.py` ma il route non e' esposto
- Nutrition periodization e' in `nutrition.py` ma non ha un endpoint dedicato

---

## 6. Features Uniche per App

### Domestique Only (non in PCC/CPSL)

1. **Workout classification engine** — 16 content classes, content-based (not filename)
2. **Route archetypes** — 220+ procedural virtual route generation
3. **Surface timeline** — Per-km surface bar visualization
4. **Drag-drop session reorder** — Interactive plan editing
5. **Plan drift detection** — Alerts when CTL drifts >15%
6. **Recovery ramp** — Never catch-up spike in taper
7. **Stepback/recovery week** — Automatic deload weeks
8. **B/C race taper** — Race-specific taper + recovery
9. **Sleep inhibit** — Sleep-based training inhibition
10. **Daily log (Hooper)** — Sleep/fatigue/stress/mood composite
11. **Blood markers** — Hemoglobin, ferritin, etc.
12. **Metrics history** — Weight/FTP trend charts
13. **Programme summary PNG** — Literature-grounded recap
14. **Ride report PNG** — Per-ride visual report
15. **Export metrics CSV** — Spreadsheet export
16. **Export FIT workout** — Native device format
17. **My calendar** — Personal calendar view
18. **Update check / Self-update** — GitHub Releases auto-update
19. **PR detection** — Per-duration personal records
20. **Ride analytics** — Decoupling, efficiency factor
21. **Race flag toggle** — Tag activities as races
22. **1,753 ZWO workouts** — Massive workout library
23. **50+ GPX routes** — Real-world routes across 6 countries

### PCC Only (non in Domestique/CPSL)

1. **Pedal asymmetry (LEOMO MPI)** — L/R balance, TE, PS, MPI
2. **CPEP import** — Critical Power Event Protocol
3. **BIA Vision** — Cloud OCR for body composition PDFs
4. **BIA manual entry** — Manual body composition input
5. **Diet parser** — OCR extraction from diet PDFs
6. **Nutrition periodization** — GSSI/IOC evidence-based carb timing
7. **Inject multidiscipline** — MTB, running, swim, strength, mobility
8. **PlanOptions selector** — 9 toggleable enrichment layers
9. **Huawei HRV manual** — Manual HRV write to ICU
10. **Health Sync normalize** — Health Sync CSV format normalization

### CPSL Only (unique to merged app)

1. **13-tab dashboard** — Most comprehensive UI
2. **HRV dedicated tab** — Full HRV management
3. **Nutrition dedicated tab** — Diet plans + supplements
4. **BIA dedicated tab** — Body composition tracking
5. **Profile dedicated tab** — FTP history + tau + Banister
6. **What's New tab** — Version changelog
7. **TID heatmap on home** — Visual intensity distribution
8. **Daily adapt card on home** — Today's recommendation
9. **Strength card on home** — Quick strength access
10. **Calendar card on home** — Upcoming sessions
11. **Assessment banner** — Fitness test prompts
12. **150 tests** — Comprehensive test suite

---

## 7. Raccomandazioni Prioritarie

### Priorita 1 — Features critiche mancanti ( CPSL < Domestique)

| # | Azione | Sforzo |
|---|--------|--------|
| 1 | Copiare 1,753 ZWO workouts da Domestique | Basso |
| 2 | Copiare 50+ GPX routes da Domestique | Basso |
| 3 | Implementare workout classification (16 types) | Medio |
| 4 | Implementare drag-drop session reorder | Medio |
| 5 | Implementare plan drift detection | Basso |
| 6 | Implementare recovery ramp + stepback week | Basso |
| 7 | Implementare B/C race taper | Medio |
| 8 | Implementare ride analytics (decoupling, EF) | Medio |
| 9 | Implementare execution score | Medio |
| 10 | Implementare rider stats grid + season totals | Basso |

### Priorita 2 — Features importanti ( CPSL < Domestique)

| # | Azione | Sforzo |
|---|--------|--------|
| 11 | Implementare sleep inhibit | Basso |
| 12 | Implementare daily log (Hooper) | Basso |
| 13 | Implementare metrics history/latest/log | Basso |
| 14 | Implementare programme summary PNG | Medio |
| 15 | Implementare export metrics CSV | Basso |
| 16 | Implementare update check / self-update | Medio |
| 17 | Implementare PR detection + toast queue | Basso |
| 18 | Implementare route archetypes (220+) | Alto |
| 19 | Implementare surface timeline | Medio |
| 20 | Implementare plan preview (dry-run) | Basso |

### Priorita 3 — Features PCC mancanti

| # | Azione | Sforzo |
|---|--------|--------|
| 21 | Testare pedal asymmetry routes | Basso |
| 22 | Testare CPEP import routes | Basso |
| 23 | Esponere BIA Vision route | Basso |
| 24 | Implementare BIA manual entry | Basso |
| 25 | Implementare nutrition periodization | Medio |
| 26 | Testare inject multidiscipline | Basso |
| 27 | Implementare PlanOptions selector | Medio |

### Priorita 4 — Qualita e documentazione

| # | Azione | Sforzo |
|---|--------|--------|
| 28 | Portare 308 test da Domestique | Alto |
| 29 | Aggiornare API_ENDPOINTS.md con tutti i route | Basso |
| 30 | Creare CHANGELOG.md | Basso |
| 31 | Creare CONTRIBUTING.md | Basso |
| 32 | Aggiungere docs/ con SCIENCE.md, SYSTEM.md | Medio |

---

## Riepilogo Finale

| App | Features totali | Features uniche | Gap vs CPSL |
|-----|----------------|-----------------|-------------|
| **Domestique** | ~120 | 23 | CPSL manca ~14 features |
| **PCC** | ~80 | 10 | CPSL manca ~10 features |
| **CPSL** | ~118 | 12 | Ha 64 features da entrambi |

**CPSL attualmente copre:**
- ~98% delle features Domestique
- ~98% delle features PCC
- ~85% delle features uniche di ciascuna

**Priorita assoluta:** Copiare workout ZWO e route GPX da Domestique, poi implementare le features critiche mancanti.
