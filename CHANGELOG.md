# CHANGELOG - Cycling Performance Studio Lab

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/).

## [1.1.2] - 2026-08-20

### Fixed
- **`/api/icu/sync` 404**: the frontend "Sync" button called an endpoint that was never registered server-side. Added the route — now pulls wellness/HRV + athlete numbers from intervals.icu on demand.
- **AI Coach RAG read empty data**: `build_rider_context` now pulls the rider's REAL HRV, weight and FTP from the intervals.icu sync store (`ride_storage.load_recent_wellness`) instead of modules that returned nothing. The coach is now grounded in actual measured data (verified: FTP 200W, HRV avg 57ms, weight 70kg).

### Verified live (with real athlete data)
- intervals.icu connect (API Key) ✅
- Wellness/HRV sync (91 records) ✅
- Plan generation (deterministic, no LLM needed) ✅
- **Plan → intervals.icu calendar push** (2 workouts pushed) ✅
- AI Coach memory + rider-context panels ✅

### Notes
- AI Coach *chat* (coach-query / weekly-analysis / generate-plan AI) still requires an LLM API key (`AI_COACH_ENABLED`); set it in Settings → AI Coach. The RAG context and memory layers work independently.



### Added
- **AI Coach with persistent memory**: the coach now remembers every session across conversations (SQLite `ai_memory.db`, per-profile). New endpoints `/api/ai/memory` (GET/DELETE) and `/api/ai/rider-context`.
- **RAG on real rider data**: coach responses are grounded in the rider's actual FTP, HRV trend, phenotype, durability and plan gaps (not generic LLM knowledge).
- **AI Coach tab UX**: "Contesto Rider" panel (live grounded data) + "Memoria del Coach" panel (session history with clear button).
- Single source of truth for version: `APP_VERSION` now derives from the `VERSION` file (no more `4.0.0-alpha` phantom).

### Cleaned
- Removed residual Domestique branding/version references that confused the app's identity (update-check still pointed at the upstream `platypus45/domestique` repo — fixed in 1.0.2; remaining inline references normalized).

### Notes
- intervals.icu **push** (plan → ICU calendar) and **HRV-guided auto-plan adaptation** were already present in the core (`/api/icu/push`, `daily_adapt_plan`); they are now surfaced and verified as part of the live workflow.



### Fixed
- **False "Update available 3.10.1"**: update-check pointed to the upstream `platypus45/domestique` repo. Now targets `quadrellif90-collab/Cycling-Performance-Studio-Lab`; platform asset matching updated to CPSL asset names (`CyclingPerformanceStudioLab.exe`, `Cycling-Performance-Studio-Lab.dmg`/`-macOS.tar.gz`, `CyclingPerformanceStudioLab-v*-linux-x86_64.tar.gz`).

### Added
- **Tab configurator**: show/hide individual dashboard tabs via Settings → "Configura schede". Per-profile, persisted in localStorage. Core tabs (Home, Settings) are always visible. "Ripristina default" resets.
- **Setup wizard launcher**: Settings → "Apri il Wizard di setup" opens `/setup` in a new tab (wizard was already auto-triggered on first run / fresh profile).
- **New curated themes**: Ocean, Forest, Sunset, Nord (plus refined Dark & Sepia palettes) — selectable from the header theme dropdown.

- **AI Coach full integration**: new `/api/ai/coach-query` (contextual coaching query using current analytics) and `/api/ai/health` (module health check) routes. AI Coach now exposes 7 endpoints: status, weekly-analysis, generate-plan, friel-assessment, friel-prompts, coach-query, health.
- **Automatic bootstrapper**: `app.py` verifies and pip-installs critical dependencies (fastapi, uvicorn, starlette, pydantic, sqlalchemy, Pillow, numpy, jinja2, python-multipart) at startup if missing — zero manual install for the end user.
- **CI/CD multi-platform**: GitHub Actions workflow builds and publishes Windows `.exe`, macOS `.dmg` and Linux `.AppImage` automatically on tag push.

### Improved
- **API routes parity** with Domestique: 145/145 routes covered
- **8 proprietary analytical modules**: Power-Duration 3P, Phenotype radar, Breakthrough detection, Durability score, Training phase detector, Formula alerts, AI Coach, Workout player
- **Test suite**: 28 API route tests passing (incl. 4 new AI Coach tests), core modules verified
- **Standalone executable**: `CyclingPerformanceStudioLab.exe` (69.8 MB) with DB auto-migration and local server on port 22400

### Fixed
- Resolved `cpsl.config` import bug in all AI Coach routes (module is top-level `config`)
- Replaced undefined `JSONContent` helper with standard `JSONResponse` across all AI routes
- Corrected CI/CD workflow: requirements filenames (`requirements-linux/mac/win.txt`), artifact upload paths, and release step

### Deprecated
- None

### Removed
- Duplicate `v0.10.0` release (consolidated into v1.0.0)

## [0.9.1] - 2026-08-20

### Added
- **BIA Vision Analysis** (`/api/bia-vision-analyze`): Cloud Vision integration for body composition analysis from PDF images via `bia_vision.py`
- **Self-Update** (`/api/self-update`): Cross-platform automatic update system (Windows NSIS, macOS DMG, Linux AppImage) with upstream asset detection
- **8 proprietary analytical modules**: Power-Duration 3P model, Phenotype radar, Breakthrough detection, Durability score, Training phase detector, Formula alerts, AI Coach, Workout player

### Improved
- **API routes parity** with Domestique: 145/145 routes now covered
- **PCC feature integration**: BIA vision cloud and self-update mechanisms fully incorporated into CPSL
- **Test suite**: 201 core tests passing, 24/25 workout player tests passing
- **Build Windows**: Executable `CyclingPerformanceStudioLab.exe` (69.8 MB) con migrazione DB e server su porta 22400

### Fixed
- Removed duplicate `api_self_update` registration from `pcc_routes_v2.py` (avoided NameError)
- Fixed version bump from `3.10.0` to `0.9.1`
- Resolved import issues in test environment

### Deprecated
- None

### Removed
- None

## [0.9.0] - 2026-08-19

### Added
- Advanced Analytics Suite: workout player, HRV integration, nutrition planning
- Power-Duration 3P model and Phenotype radar
- Breakthrough detection and Durability scoring
- Training phase detection and Formula-based alerts
- AI Coach module and full workout player functionality
- Migration script `migrate_profiles.py` for Domestique → CPSL upgrade

### Improved
- Full API route analysis: 198+ routes mapped across CPSL, Domestique, PCC
- Comparative report: `ANALISI_COMPARATIVA_3_APP.md` generated
- Test infrastructure: 239/239 CPSL tests passing

## [Unreleased]

### Planned
- Dashboard widget enhancements
- External integrations (Strava / TrainingPeaks)
- Mobile companion app

### Notes
- Version targeted for next release cycle