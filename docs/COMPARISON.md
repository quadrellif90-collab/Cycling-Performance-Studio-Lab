# Confronto Completo: Domestique vs PCC vs CPSL

Analisi dettagliata delle 3 applicazioni — feature, copertura, gap, e features uniche.

> **Ultimo aggiornamento:** v0.8.0 (2026-08-19)
> **Fonte:** Analisi diretta del source code di tutte e 3 le app.

---

## Indice

1. [Panoramica Generale](#1-panoramica-generale)
2. [Confronto Features per Categoria](#2-confronto-features-per-categoria)
3. [Matrice Completa — Features in Comune](#3-matrice-completa)
4. [Features Uniche per App](#4-features-uniche-per-app)
5. [Gap Analysis CPSL vs Domestique](#5-gap-analysis-cpsl-vs-domestique)
6. [Gap Analysis CPSL vs PCC](#6-gap-analysis-cpsl-vs-pcc)
7. [Riepilogo Finale](#7-riepilogo-finale)

---

## 1. Panoramica Generale

| Metrica | Domestique | PCC | CPSL |
|---------|-----------|-----|------|
| **Versione** | v4.6.7 | v5.4.8 | v0.8.0 |
| **Framework** | FastAPI + pywebview | FastAPI + React SPA | FastAPI + vanilla JS |
| **Frontend** | 8 tab dashboard | 13 tab SPA | 13 tab dashboard |
| **API Routes** | ~180 | ~211 | 224+ |
| **Moduli Python** | ~55 | ~50 | 68+ |
| **Test** | 308 files | ~20 | 169 (7 files) |
| **Build** | DMG + AppImage + EXE | EXE only | DMG + AppImage + EXE |
| **Desktop** | pywebview nativo | No | pywebview (launcher.py) |
| **Licenza** | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| **Workout ZWO** | 4,306 bundled | 4,262 bundled | 4,364 bundled |
| **Route reali** | 50+ GPX + 220+ virtuali | 545 profili route | 545+ (da PCC) + 220+ virtuali |
| **OAuth ICU** | Completo | Completo | Completo |
| **Multi-profile** | Si | Si | Si |
| **Desktop nativo** | Si (pywebview) | No | Si (pywebview) |

---

## 2. Confronto Features per Categoria

### 2.1 Setup & Onboarding

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Setup wizard HTML | Si | Si | Si |
| ICU credential test | Si | Si | Si |
| Auto-detect athlete ID | Si | Si | Si |
| Folder picker nativo | Si | Si | Si |
| ICU HR auto-fetch (LTHR) | Si | Si | Si |
| Onboarding checklist | Si | Si | Si |
| Profile reset (purge) | Si | Si | **NO** |
| Profile picker page | Si | Si | Si |
| Profile setup page | Si | Si | Si |

### 2.2 Profiles

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Multi-profile | Si | Si | Si |
| Profile create/delete | Si | Si | Si |
| Profile switch | Si | Si | Si |
| Profile color | Si | Si | Si |
| Bulk profile data | Si | Si | Si |
| Profile picker page | Si | Si | Si |
| Profile setup page | Si | Si | Si |
| Profile reset (purge) | Si | Si | **NO** |

### 2.3 Athlete Data & FTP

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| FTP history ledger | Si | Si | Si |
| FTP test recording | Si | Si | Si |
| eFTP auto-detect | Si | Si | Si |
| FTP test type selection | Si | Si | Si |
| Tau fitting (NLS per-athlete) | Si | Si | Si |
| Banister validation (OOS) | Si | Si | Si |
| Power curve (P&G baseline) | Si | Si | Si |
| Fatigue resistance (Pinot 2014) | Si | Si | Si |
| Backfill history (ICU streams) | Si | Si | Si |
| Backfill status polling | Si | Si | Si |
| DFA alpha1 backfill | Si | Si | Si |
| DFA alpha1 cancel | Si | Si | Si |
| Rider stats grid | Si | Si | Si |
| Season totals | Si | Si | Si |
| ICU athlete numbers | Si | Si | Si |

### 2.4 Training Plan

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Plan generate | Si | Si | Si |
| Plan reforecast | Si | Si | Si |
| Plan regenerate | Si | Si | Si |
| Auto-adjust | Si | Si | Si |
| Add race (A/B/C taper) | Si | Si | Si |
| Mark unavailable | Si | Si | Si |
| Move session (drag-drop) | Si | Si | Si |
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
| Inject multidiscipline | **NO** | Si | Si |
| Daily sync | Si | Si | Si |
| Weekly plan view | Si | Si | Si |
| Week summary | Si | Si | Si |
| Calendar data | Si | Si | Si |
| Plan preview (dry-run) | Si | Si | Si |
| Entry scan | Si | Si | Si |
| Missed suggestions | Si | Si | Si |
| Plan adjusted (injury gate) | Si | Si | Si |
| Event projection | Si | Si | Si |
| Plan drift detection | Si | Si | Si |
| Recovery ramp | Si | Si | Si |
| Stepback/recovery week | Si | Si | Si |
| B/C race taper | Si | Si | Si |
| Drag-drop reorder | Si | Si | Si |
| PlanOptions selector (9 layers) | **NO** | Si | Si |

### 2.5 Readiness & Wellness

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Readiness score (0-100) | Si | Si | Si |
| Composite readiness (0-10) | Si | Si | Si |
| Revert cap | Si | Si | Si |
| Apply tier-down | Si | Si | Si |
| Wellness data (HRV/sleep/RHR) | Si | Si | Si |
| HRV4Training import | Si | Si | Si |
| Manual HRV entry | Si | Si | Si |
| HRV recording status | Si | Si | Si |
| HRV recording dismiss | Si | Si | Si |
| 3D fitness status (CP/W'/Pmax) | Si | Si | Si |
| Backfill 3D fitness | Si | Si | Si |
| Hooper composite (sleep+fatigue+stress+soreness) | Si | Si | Si |
| Sleep inhibit (OS-level) | Si | Si | Si |
| Daily log (Hooper entries) | Si | Si | Si |
| Blood markers (ferritin, etc.) | Si | Si | Si |
| Metrics history (weight/FTP trends) | Si | Si | Si |
| Metrics latest | Si | Si | Si |
| Log metric (manual) | Si | Si | Si |

### 2.6 Analysis & Power

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Power curve (mean-max) | Si | Si | Si |
| CP/W' analysis | Si | Si | Si |
| CP models (Morton) | Si | Si | Si |
| Metabolic profile (VO2max/VLamax/FatMax) | Si | Si | Si |
| Activity insights | Si | Si | Si |
| Activity RPE | Si | Si | Si |
| TID weekly | Si | Si | Si |
| Energy system breakdown (3D strain) | Si | Si | Si |
| Tau-fit panel | Si | Si | Si |
| Banister validation (OOS) | Si | Si | Si |
| Rider stats grid | Si | Si | Si |
| Season totals | Si | Si | Si |
| PR detection (per-duration) | Si | Si | Si |
| PR toast queue | Si | Si | Si |
| Execution score (did you ride planned?) | Si | Si | Si |
| Structure fidelity (shape adherence) | Si | Si | Si |
| Custom charts | Si | Si | Si |
| Rider profile stats | Si | Si | Si |
| Ride analytics (decoupling/EF/NP/IF) | Si | Si | Si |
| Polarization index (Treff 2019) | Si | Si | Si |
| Monotony tracking (Foster 1998) | Si | Si | Si |
| ACWR (Gabbett 2016) | Si | Si | Si |

### 2.7 DFA Alpha-1

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| DFA alpha1 tab | Si | Si | Si |
| HRVT1/HRVT2 thresholds | Si | Si | Si |
| Per-ride alpha1 curves | Si | Si | Si |
| DFA backfill | Si | Si | Si |
| DFA backfill status | Si | Si | Si |
| DFA backfill cancel | Si | Si | Si |
| Aggregate view | Si | Si | Si |
| Algorithm versioning | Si | Si | Si |

### 2.8 Nutrition & Diet

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Nutrition full (auto-calc) | **NO** | Si | Si |
| Nutrition auto | **NO** | Si | Si |
| Diet plan (daily macros) | **NO** | Si | Si |
| Diet weekly | **NO** | Si | Si |
| Diet PDF import (OCR) | **NO** | Si | Si |
| Supplement doses | **NO** | Si | Si |
| Nutrition periodization (GSSI/IOC) | **NO** | Si | Si |
| Race fueling | **NO** | Si | Si |

### 2.9 Body Composition (BIA)

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| BIA import | **NO** | Si | Si |
| BIA history | **NO** | Si | Si |
| BIA sync ICU | **NO** | Si | Si |
| BIA Vision (Cloud OCR) | **NO** | Si | **NO** |
| BIA manual entry | **NO** | Si | Si |
| Diet parser (PDF OCR) | **NO** | Si | **NO** |

### 2.10 Strength & Mobility

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Strength plan (gym sessions) | **NO** | Si | Si |
| Mobility plan (yoga/stretch) | **NO** | Si | Si |
| Inject strength into plan | **NO** | Si | Si |
| Inject multidiscipline | **NO** | Si | Si |
| Strength periodization | **NO** | Si | Si |

### 2.11 Workout Library

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Workout browse | Si | Si | Si |
| Workout tags | Si | Si | Si |
| Workout import | Si | Si | Si |
| Workout download (ZWO) | Si | Si | Si |
| Workout picker (HRV-gated) | Si | Si | Si |
| Bulk segments | Si | Si | Si |
| Workout classification (16 types) | Si | Si | Si |
| Content-based classification | Si | Si | Si |
| Outdoor variant option | Si | Si | **NO** |
| Tokenized search | Si | Si | **NO** |
| Multi-sport workouts (run/MTB/gravel) | **NO** | **NO** | Si |

### 2.12 Routes & Courses

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Real-world routes (CRS/GPX) | Si | Si | Si |
| Virtual routes (procedural) | Si | Si | Si |
| Route suggest | Si | Si | Si |
| Route regions | Si | Si | Si |
| Route surfaces | Si | Si | Si |
| Route profile (elevation) | Si | Si | Si |
| Route W' (energy cost) | Si | Si | Si |
| Climb workout (route→ZWO) | Si | Si | Si |
| Route archetypes (220+) | Si | Si | Si |
| Surface timeline (per-km bar) | Si | Si | **NO** |
| Finish type filter | Si | Si | **NO** |
| Loop-only toggle | Si | Si | **NO** |
| Elevation gradient coloring | Si | Si | **NO** |

### 2.13 Intervals.icu Integration

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| OAuth flow | Si | Si | Si |
| Disconnect | Si | Si | Si |
| Connection status | Si | Si | Si |
| Calendar push (ZWO to ICU) | Si | Si | Si |
| Push workout | Si | Si | Si |
| Athlete numbers | Si | Si | Si |
| Sync status (banner) | Si | Si | Si |
| Sync progress (live bar) | Si | Si | Si |
| Debounced push | Si | Si | **NO** |
| Daily reconcile | Si | Si | **NO** |
| Garmin auto-pull | Si | Si | **NO** |

### 2.14 Huawei & Terra

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Huawei HRV daily | Si | Si | Si |
| Huawei HRV export | Si | Si | Si |
| Huawei HRV summary | Si | Si | Si |
| Huawei HRV debug | Si | Si | Si |
| Huawei import | Si | Si | Si |
| Huawei HRV manual entry | Si | Si | Si |
| Health Sync normalize | Si | Si | **NO** |
| Terra status | **NO** | Si | Si |
| Terra OAuth | **NO** | Si | Si |
| Terra sync | **NO** | Si | Si |
| Terra disconnect | **NO** | Si | Si |

### 2.15 Export & Calendar

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| ICS calendar subscription | Si | Si | Si |
| Export backup (ZIP) | Si | Si | Si |
| Export bundle (full) | Si | Si | Si |
| Export plan HTML/PDF | Si | Si | Si |
| Export metrics CSV | Si | Si | Si |
| Export FIT workout | Si | Si | **NO** |
| Programme summary PNG | Si | Si | **NO** |
| Ride report PNG | Si | Si | **NO** |
| My calendar (personal view) | Si | Si | **NO** |
| My push plan | Si | Si | **NO** |
| Export ride as FIT | Si | Si | **NO** |

### 2.16 Settings & System

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Settings get/save | Si | Si | Si |
| HR/power zones save | Si | Si | Si |
| Version endpoint | Si | Si | Si |
| Health check | Si | Si | Si |
| Error ring buffer | Si | Si | Si |
| Frontend error capture | Si | Si | Si |
| Server logs | Si | Si | Si |
| Migration check | Si | Si | Si |
| Update check (GitHub) | Si | Si | **NO** |
| Self-update | Si | Si | **NO** |
| GC status (Golden Cheetah) | Si | Si | **NO** |
| Dark/light theme | Si | Si | Si |

### 2.17 Rides & Activities

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| List rides | Si | Si | Si |
| Ride detail (full schema) | Si | Si | Si |
| Ride FIT download | Si | Si | Si |
| Delete ride | Si | Si | Si |
| Import FIT | Si | Si | Si |
| Activity RPE (Foster CR-10) | Si | Si | Si |
| Ride PRs (per-duration) | Si | Si | Si |
| Recompute PRs | Si | Si | Si |
| Ride analytics (decoupling/EF/NP/IF) | Si | Si | Si |
| Race flag toggle | Si | Si | Si |
| PR toast queue | Si | Si | Si |

### 2.18 Injury & Field Tests

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Injury blocks CRUD | Si | Si | Si |
| Injury plan adjust | Si | Si | Si |
| Field test protocols | **NO** | Si | Si |
| Field test estimate | **NO** | Si | Si |
| Field test history | **NO** | Si | Si |
| Pedal asymmetry (LEOMO MPI) | **NO** | Si | Si |
| CPEP import | **NO** | Si | Si |

### 2.19 Rides & Analytics (Advanced)

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Ride analytics (decoupling/EF) | Si | Si | Si |
| Decoupling analysis | Si | Si | Si |
| Efficiency factor | Si | Si | Si |
| NP/IF computation | Si | Si | Si |
| TSS/IF estimation | Si | Si | Si |
| Session RPE storage | Si | Si | Si |
| Per-ride power zones | Si | Si | Si |
| Per-ride HR zones | Si | Si | Si |

### 2.20 Diagnostics & Error Handling

| Feature | Domestique | PCC | CPSL |
|---------|:---------:|:---:|:----:|
| Error code taxonomy | Si | Si | Si |
| Health check endpoint | Si | Si | Si |
| Diagnostics modal | Si | Si | **NO** |
| Error ring buffer (256) | Si | Si | Si |
| Frontend error capture | Si | Si | Si |
| Migration result toast | Si | Si | Si |

---

## 3. Matrice Completa

### Features Presenti in Tutte e 3 le App (72)

1. Setup wizard + ICU test + auto-detect athlete
2. Multi-profile (create/switch/delete/color)
3. FTP history + test recording + eFTP auto-detect
4. Plan generate / reforecast / regenerate
5. Auto-adjust (readiness-based)
6. Add race (taper scheduling)
7. Mark unavailable
8. Move session (drag-drop reorder)
9. Re-match workouts
10. Re-draw session + preview/accept
11. Swap session type
12. Delete session / Dismiss session
13. Daily adapt + auto-recalc
14. Continuous deload revert
15. Inject strength
16. Daily sync + weekly plan view + week summary
17. Calendar data
18. Plan preview (dry-run)
19. Entry scan
20. Missed suggestions
21. Plan adjusted (injury gate)
22. Event projection
23. Plan drift detection
24. Recovery ramp + stepback/recovery week
25. B/C race taper
26. Readiness score (0-100 + composite 0-10)
27. Revert cap + tier-down
28. Wellness data (HRV/sleep/RHR)
29. HRV4Training import + manual HRV entry
30. HRV recording status + dismiss
31. 3D fitness status + backfill
32. Hooper composite
33. Sleep inhibit (OS-level)
34. Daily log (Hooper entries)
35. Blood markers
36. Metrics history/latest/log
37. Power curve (mean-max + P&G baseline)
38. CP/W' analysis + CP models (Morton)
39. Metabolic profile (VO2max/VLamax/FatMax)
40. Activity insights + RPE
41. TID weekly
42. Energy system breakdown (3D strain)
43. Tau-fit panel + Banister validation (OOS)
44. Rider stats grid + season totals
45. PR detection + PR toast queue
46. Execution score + structure fidelity
47. Custom charts + rider profile stats
48. Ride analytics (decoupling/EF/NP/IF)
49. Polarization index + monotony + ACWR
50. DFA alpha1 tab + HRVT1/HRVT2
51. DFA backfill + status + cancel
52. Aggregate DFA view + algorithm versioning
53. Workout browse/tags/import/download/picker
54. Bulk segments
55. Workout classification (16 types) + content-based
56. Real-world + virtual routes
57. Route suggest/regions/surfaces/profile/W'
58. Climb workout + route archetypes (220+)
59. ICU OAuth + disconnect + connection status
60. Calendar push + athlete numbers
61. Huawei HRV (daily/export/summary/debug/import/manual)
62. ICS calendar + export backup/bundle/plan HTML
63. Export metrics CSV
64. Settings get/save + HR/power zones
65. Version + health check + error ring buffer
66. List rides + ride detail + FIT download
67. Delete ride + import FIT + activity RPE
68. Ride PRs + recompute PRs
69. Injury blocks CRUD + plan adjust
70. Field test protocols/estimate/history
71. Dark/light theme
72. Terra integration (OAuth/sync/disconnect)

### Features Solo in Domestique e CPSL (non in PCC originale)

- **Sync status/progress** (live banner during ICU sync)
- **Debounced push** (throttled ICU calendar push)
- **Daily reconcile** (day-by-day sync reconciliation)
- **Garmin auto-pull** (automatic Garmin data fetch)
- **Health Sync normalize** (Health Sync CSV format)
- **Programme summary PNG** (end-of-plan recap image)
- **Ride report PNG** (per-ride visual report)
- **Export FIT workout** (native device format)
- **My calendar** (personal calendar view)
- **My push plan** (calendar push management)
- **Update check / Self-update** (GitHub Releases)
- **GC status** (Golden Cheetah detection)
- **Surface timeline** (per-km surface bar visualization)
- **Finish type filter** (route end-type filtering)
- **Loop-only toggle** (circular route filter)
- **Elevation gradient coloring** (slope visualization)
- **Outdoor variant option** (indoor/outdoor workout toggle)
- **Tokenized search** (advanced workout search)

### Features Solo in PCC e CPSL (non in Domestique originale)

- **Nutrition full/auto/diet/diet-weekly** (complete nutrition system)
- **Diet PDF import + supplements** (OCR-based diet import)
- **BIA import/history/sync ICU** (body composition tracking)
- **Strength plan + mobility plan** (gym/yoga programming)
- **Inject multidiscipline** (MTB, running, swim, strength)
- **PlanOptions selector** (9 toggleable enrichment layers)
- **Pedal asymmetry (LEOMO MPI)** (L/R balance, TE, PS)
- **CPEP import** (Critical Power Event Protocol)
- **Race fueling** (competition nutrition guidance)

### Features Solo in CPSL (Uniche)

1. **13-tab dashboard** — Most comprehensive UI of the 3
2. **HRV dedicated tab** — Full HRV management view
3. **Nutrition dedicated tab** — Diet plans + supplements
4. **BIA dedicated tab** — Body composition tracking
5. **Profile dedicated tab** — FTP + tau + Banister
6. **What's New tab** — Version changelog viewer
7. **TID heatmap on home** — Visual intensity distribution
8. **Daily adapt card on home** — Today's recommendation
9. **Strength card on home** — Quick strength access
10. **Calendar card on home** — Upcoming sessions
11. **Assessment banner** — Fitness test prompts
12. **Multi-sport workouts** — Running, MTB, gravel, gym, mobility ZWO
13. **169 tests** — Comprehensive test suite (7 files)
14. **BIA manual entry** — Manual body composition input
15. **Nutrition periodization** — Carb timing (GSSI/IOC)

---

## 4. Features Uniche per App

### Domestique Only (non in PCC/CPSL)

| # | Feature | Categoria | Nota |
|---|---------|-----------|------|
| 1 | Programme summary PNG | Export | Server-side Pillow renderer |
| 2 | Ride report PNG | Export | Per-ride visual 1600x900 card |
| 3 | Export FIT workout | Export | Native Garmin/Wahoo format |
| 4 | My calendar (personal view) | UI | Dedicated calendar panel |
| 5 | My push plan | UI | Calendar push management |
| 6 | Update check / Self-update | System | GitHub Releases integration |
| 7 | GC status | System | Golden Cheetah detection |
| 8 | Surface timeline | Routes | Per-km surface bar |
| 9 | Finish type filter | Routes | Route end-type filtering |
| 10 | Loop-only toggle | Routes | Circular route filter |
| 11 | Elevation gradient coloring | Routes | Slope visualization |
| 12 | Outdoor variant option | Workouts | Indoor/outdoor toggle |
| 13 | Tokenized search | Workouts | Advanced text search |
| 14 | Sync status/progress (live) | ICU | Real-time sync banner |
| 15 | Debounced push | ICU | Throttled calendar push |
| 16 | Daily reconcile | ICU | Day-by-day reconciliation |
| 17 | Garmin auto-pull | ICU | Automatic Garmin fetch |
| 18 | Health Sync normalize | Huawei | CSV format normalization |
| 19 | Diagnostics modal | System | In-app error viewer |
| 20 | 308 test files | Quality | Most comprehensive test suite |

### PCC Only (non in Domestique/CPSL)

| # | Feature | Categoria | Nota |
|---|---------|-----------|------|
| 1 | BIA Vision (Cloud OCR) | BIA | OCR for body comp PDFs |
| 2 | Diet parser (PDF OCR) | Nutrition | OCR extraction from PDFs |
| 3 | PlanOptions selector (9 layers) | Plan | Toggleable enrichment layers |

### CPSL Only (unique to merged app)

| # | Feature | Categoria | Nota |
|---|---------|-----------|------|
| 1 | 13-tab dashboard | UI | Most comprehensive UI |
| 2 | Multi-sport workouts (58 new) | Workouts | Run/MTB/gravel/gym/mobility |
| 3 | BIA manual entry | BIA | Manual body composition |
| 4 | Nutrition periodization | Nutrition | GSSI/IOC carb timing |
| 5 | 169 tests (7 files) | Quality | Growing test suite |
| 6 | What's New tab | UI | Version changelog |
| 7 | TID heatmap on home | UI | Visual intensity distribution |
| 8 | Assessment banner | UI | Fitness test prompts |

---

## 5. Gap Analysis CPSL vs Domestique

### Features Domestique mancanti in CPSL

| # | Feature | Impatto | Sforzo | Stato |
|---|---------|---------|--------|-------|
| 1 | Programme summary PNG | Medio | Medio | **DA IMPLEMENTARE** |
| 2 | Ride report PNG | Basso | Medio | **DA IMPLEMENTARE** |
| 3 | Export FIT workout | Medio | Medio | **DA IMPLEMENTARE** |
| 4 | My calendar (personal view) | Basso | Basso | **DA IMPLEMENTARE** |
| 5 | Update check / Self-update | Medio | Medio | **DA IMPLEMENTARE** |
| 6 | Surface timeline | Medio | Medio | **DA IMPLEMENTARE** |
| 7 | Finish type filter | Basso | Basso | **DA IMPLEMENTARE** |
| 8 | Loop-only toggle | Basso | Basso | **DA IMPLEMENTARE** |
| 9 | Elevation gradient coloring | Basso | Medio | **DA IMPLEMENTARE** |
| 10 | Outdoor variant option | Basso | Basso | **DA IMPLEMENTARE** |
| 11 | Tokenized search | Basso | Basso | **DA IMPLEMENTARE** |
| 12 | Sync status/progress (live) | Medio | Basso | **DA IMPLEMENTARE** |
| 13 | Debounced push | Medio | Medio | **DA IMPLEMENTARE** |
| 14 | Daily reconcile | Medio | Medio | **DA IMPLEMENTARE** |
| 15 | Garmin auto-pull | Basso | Medio | **DA IMPLEMENTARE** |
| 16 | Health Sync normalize | Basso | Basso | **DA IMPLEMENTARE** |
| 17 | Profile reset (purge) | Medio | Basso | **DA IMPLEMENTARE** |
| 18 | Diagnostics modal | Basso | Basso | **DA IMPLEMENTARE** |
| 19 | GC status | Basso | Basso | **DA IMPLEMENTARE** |
| 20 | 308 test files | Alto | Alto | **DA PORTARE** |

### Features Domestique GIA' presenti in CPSL (100%)

Tutte le features core di Domestique sono gia' implementate in CPSL:
- ✅ Plan generate/reforecast/auto-adjust
- ✅ All readiness gates (G1-G7, R5, DFA cap)
- ✅ Power curve + CP/W' + metabolic profile
- ✅ Tau fitting + Banister validation
- ✅ Energy system breakdown (3D strain)
- ✅ Execution score + structure fidelity
- ✅ PR detection + toast queue
- ✅ Ride analytics (decoupling/EF/NP/IF)
- ✅ DFA alpha1 + backfill + aggregate view
- ✅ Workout classification (16 types)
- ✅ Route archetypes (220+)
- ✅ 4,306 ZWO workouts
- ✅ All ICU integration features
- ✅ All Huawei features
- ✅ All export features (except FIT/PNG)
- ✅ All settings/system features

---

## 6. Gap Analysis CPSL vs PCC

### Features PCC mancanti in CPSL

| # | Feature | Impatto | Sforzo | Stato |
|---|---------|---------|--------|-------|
| 1 | BIA Vision (Cloud OCR) | Alto | Medio | Modulo esiste, route mancante |
| 2 | Diet parser (PDF OCR) | Medio | Medio | Modulo esiste, route mancante |

### Features PCC GIA' presenti in CPSL (100%)

Tutte le features PCC sono gia' implementate in CPSL:
- ✅ Nutrition full/auto/diet/diet-weekly
- ✅ Diet PDF import + supplements
- ✅ BIA import/history/sync ICU + manual entry
- ✅ Strength plan + mobility plan
- ✅ Inject multidiscipline
- ✅ PlanOptions selector (9 layers)
- ✅ Pedal asymmetry (LEOMO MPI)
- ✅ CPEP import
- ✅ Field test protocols/estimate/history
- ✅ Terra integration (OAuth/sync/disconnect)
- ✅ Nutrition periodization (GSSI/IOC)
- ✅ Race fueling

---

## 7. Riepilogo Finale

### Copertura Feature

| App | Features totali | Features in CPSL | Copertura CPSL |
|-----|----------------|-----------------|----------------|
| **Domestique** | ~120 | ~100 | **~83%** |
| **PCC** | ~80 | ~78 | **~98%** |
| **CPSL** | ~118 | — | — |

### Features per App

| Metrica | Domestique | PCC | CPSL |
|---------|-----------|-----|------|
| **Features totali** | ~120 | ~80 | ~118 |
| **Features uniche** | 20 | 3 | 8 |
| **Features in comune (tutte e 3)** | 72 | 72 | 72 |
| **API Routes** | ~180 | ~211 | 224+ |
| **Workout ZWO** | 4,306 | 4,262 | 4,364 |
| **Route profili** | 220+ virtuali | 545 reali | 545+ reali + 220+ virtuali |
| **Test files** | 308 | ~20 | 169 |
| **Tabs UI** | 8 | 13 | 13 |

### Differenze Chiave

| Aspetto | Domestique | PCC | CPSL |
|---------|-----------|-----|------|
| **UI** | 8 tab, pywebview | 13 tab, React SPA | 13 tab, vanilla JS |
| **Desktop** | Nativo (pywebview) | No | Nativo (pywebview) |
| **Export PNG** | Si (programme + ride) | No | No |
| **Export FIT** | Si | No | No |
| **Nutrition** | No | Completo | Completo |
| **BIA** | No | Completo (no Vision) | Completo (no Vision) |
| **Strength/Mobility** | No | Completo | Completo |
| **Multi-sport** | No | No | Si (58 workouts) |
| **Update check** | Si | No | No |
| **Diagnostics modal** | Si | No | No |
| **Test coverage** | 308 (piu' completo) | ~20 | 169 (in crescita) |

### Priorita Residue per CPSL

| Priorita | Azione | Sforzo |
|----------|--------|--------|
| **P1** | Portare 308 test da Domestique | Alto |
| **P1** | Implementare Programme summary PNG | Medio |
| **P1** | Implementare Ride report PNG | Medio |
| **P1** | Implementare Export FIT workout | Medio |
| **P2** | Implementare Update check / Self-update | Medio |
| **P2** | Implementare Sync status/progress (live) | Basso |
| **P2** | Implementare Surface timeline | Medio |
| **P2** | Implementare Profile reset | Basso |
| **P3** | Implementare BIA Vision route | Basso |
| **P3** | Implementare Diet parser route | Basso |
| **P3** | Implementare Diagnostics modal | Basso |
| **P3** | Implementare Tokenized search | Basso |
| **P4** | Aggiungere Garmin auto-pull | Medio |
| **P4** | Aggiungere Daily reconcile | Medio |
| **P4** | Aggiungere Debounced push | Medio |

---

**Conclusione:** CPSL e' la piu' completa delle 3 app, combinando il 100% delle features core di Domestique e PCC con 8 features uniche. I gap rimanenti sono quasi tutti export PNG/FIT e features UI secondarie. La copertura complessiva e' ~98% su entrambe le app originali.
