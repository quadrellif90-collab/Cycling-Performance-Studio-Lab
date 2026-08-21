# CHANGELOG - Cycling Performance Studio Lab

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/).

## [1.3.1] - 2026-08-21

### Fixed (release di stabilità — deep scan + test live su browser reale)

- **Chart.js mancante → tutti i grafici morti** (causa radice dei "tab non funzionanti"): `dashboard.html` caricava `/static/vendor/chart.umd.min.js` ma la cartella `frontend/static/vendor/` non esisteva mai nel repo. Ogni scheda con un grafico (Analysis, Plan, HRV, DFA, Home sparkline…) falliva silenziosamente. Chart.js 4.4.3 (MIT) ora è incluso in `frontend/static/vendor/`.
- **Icone statiche 404**: aggiunti `favicon.png`, `icon.png`, `apple-touch-icon.png` in `frontend/static/` (prima referenziati ma assenti).
- **`cpsl_ui.css` fantasma**: `hrv_monitor.html` e `workout_player.html` referenziavano un CSS mai creato (404 a ogni apertura pagina). Entrambe le pagine sono self-styled via `<style>` inline; aggiunto placeholder per eliminare il 404.
- **Deadlock Workout Player** (`workout_player.py`): il loop di playback teneva `self._lock` durante `time.sleep(1)` e scriveva al trainer BLE dentro il lock — ogni skip/pausa/report dell'utente si accodava al tick (freeze percepibile, hang nei test concorrenti). Ora il lock copre solo lo snapshot di stato; la scrittura BLE e l'attesa (interrompibile via `_stop_flag.wait()`) avvengono fuori dal lock.
- **Sintassi Python dentro JavaScript** (`app.js`): `sendAiCoachMessage` conteneva `try:`/`else:`/commenti `#` → SyntaxError che bloccava TUTTO il frontend. Riscritta in JS valido.
- **Banner onboarding duplicato** (`dashboard.html`): seconda copia con gli stessi `id` mai nascosta da JS (`getElementById` trova solo la prima) → striscia "Completa il setup" non dismissabile su ogni tab. Rimossa.
- **4 bottoni morti** (onclick verso funzioni inesistenti): implementati `busyButton()` (Push piano ICU, Inietto multidisciplina), `loadNutritionAuto()` (bottone "Auto" nutrizione → `/api/nutrition-auto`, endpoint finora orfano), `openHuaweiImport()` (naviga al tab HRV), `injectMultidiscipline()` (`/api/plan/inject-multidiscipline`).
- **Tab orfano "Workout Player"**: rimosso dalla barra (nessuna sezione interna; il player è una pagina separata `/player/<file>` aperta dalla libreria).

### Removed
- **Estensione browser `extensions/icu-cpsl/`** e relativo bridge `GET /api/icu/extension/context`: rimossa su decisione owner (non utilizzabile così com'era).

### Verified (test live con browser automation, app reale)
- 14/14 tab si aprono e diventano visibili: Home, Shuffle, Library, Routes & Climbs, **Plan**, Analysis, DFA α1, Settings, HRV, Nutrition, BIA, Profile, Novità, AI Coach.
- Pianificatore verificato end-to-end: fold configurazione apre/chiude, "Generate Plan" produce 12 settimane, calendario renderizza 25 righe (`#cal-rows`) con fasi/date/TSS, metriche CTL/FTP/W/kg presenti.
- 0 errori JavaScript di pagina; Chart.js globale attivo; connessione Intervals.icu OK.

## [1.3.0] - 2026-08-21

### Added
- **Estensione browser production-ready** (`extensions/icu-cpsl/` v1.0.0): background service worker con auth centralizzata (API key **o** OAuth bearer), cache 5 min, popup di stato (auth + bridge CPSL), pannello in-page arricchito con ultime attività e prossimi eventi, URL CPSL locale configurabile, escape HTML su tutti i dati API.
- **MCP server CPSL** (`icu_mcp_server.py`): espone 5 tool MCP (wellness_recent, rider_context, coach_memory_search, activities_recent, plan_preview) via stdio JSON-RPC — collegabile a Claude Desktop o qualsiasi client MCP. Bridge HTTP incluso: `GET /api/mcp/status`, `POST /api/mcp/call`.
- **Import multi-sorgente** (`importers.py`): Garmin Connect (HRV/sonno/peso → wellness records, token cache senza credenziali persistenti), file `.FIT` (riepilogo attività via fitparse), `.GPX` (via parser interno). Endpoint: `POST /api/import/garmin|fit|gpx`.
- **Metriche avanzate** (`advanced_metrics.py`): Critical Power + W' (modello lineare P = CP + W'/t con R²), W' balance (Skiba), DFA α1 (DFA su finestre RR), classificazione distribuzione intensità (polarizzata/piramidale/soglia). Endpoint: `POST /api/metrics/power-analysis` (upload FIT), `POST /api/metrics/load-distribution`.
- **Pagina atleta pubblica**: `GET /export/athlete-page` HTML self-contained condivisibile (card statistiche + tabella attività) e `GET /api/export/athlete-page` payload JSON.

### Dependencies
- `garminconnect`, `fitparse` (opzionali a runtime: gli endpoint degradano con messaggio chiaro se assenti).



### Added
- **POC: estensione CPSL per intervals.icu** (`extensions/icu-cpsl/`): estensione Chrome/Edge MV3 che inietta un pannello CPSL dentro la pagina atleta di ICU, mostrando Forma/CTL, Fatica/ATL, Equilibrio/TSB, HRV, HRV 14gg e Peso. Se CPSL è in esecuzione in locale usa i valori ufficiali via bridge; altrimenti calcola lato client dalle API REST di ICU. La API key ICU è salvata solo nel browser (`chrome.storage.local`).
- **Bridge lato CPSL** `GET /api/icu/extension/context?athlete_id=...`: restituisce gli indicatori calcolati da CPSL per un atleta (riusa il loader wellness del RAG AI Coach).

### Fixed
- **CI pytest hang**: `test_smoke.py` veniva raccolto da pytest come test (nome `test_*.py`) e si appendeva sui timeout di rete verso `127.0.0.1:22400`. Rinominato in `smoke_test.py` (non matcha il pattern) e aggiornato il job CI. La CI ora completa in tempi normali.



### Added
- **Per-user LLM API keys**: the AI Coach configuration panel now makes clear every end user must supply **their own** provider API key (no shared/bundled keys). Each provider shows a contextual **"Crea API Key su …"** link pointing to that provider's key-signup page, so users without a key can get one in one click.
- **Build hardening**: `ai_config.json` and `*.env` are now explicitly excluded from the PyInstaller build, guaranteeing no local secrets ship inside the distributed `.exe`/`.app`/`.tar.gz`.



### Added
- **AI Coach LLM settings UI** (Settings → AI Coach tab): choose provider (Google Gemini / OpenAI / Anthropic / Groq / DeepSeek / Mistral / OpenRouter / xAI / Ollama), model, API key, and an optional **fallback provider** for rate-limit resilience. Key is stored only in gitignored `ai_config.json`.
- **AI Coach config export/import** (`/api/ai/config/export`, `/api/ai/config/import`) — backup and restore the LLM configuration (provider/key/model/fallback) as a JSON file, so a profile wipe no longer loses the coach setup.
- **LLM provider fallback** in `ai_coach/llm_client`: if the primary provider errors, the client automatically retries on a configured fallback provider before failing.
- **CI live smoke-test job**: the workflow now starts the app and runs `test_smoke.py` against all functional endpoints (credentials injected via GitHub secrets — never hard-coded).

### Fixed
- **ICU sync silent failure**: `/api/icu/sync` now checks the connection state up front and returns a clear `not_connected` error instead of a silent 500; wellness errors include the exception message for faster diagnosis.
- **Rate-limit resilience**: retry-with-backoff on HTTP 429/503 extended to all OpenAI-compatible providers (was Gemini-only), so transient provider limits don't break coach queries or weekly analysis.



### Fixed
- **AI Coach not auto-enabling on boot**: persisted settings in `ai_config.json` were only applied inside the `lifespan()` hook, which didn't reliably re-enable the coach after a restart (status stayed `ai_coach_enabled: false`). Moved the load to **module-import time** so the coach is enabled immediately on startup, reading provider/key/model from `ai_config.json`. Verified: `GET /api/ai/status` now returns `enabled: true` right after launch.



### Fixed
- **AI Coach 503 on Gemini preview models**: `gemini-3-flash-preview` intermittently returns `503 Service Unavailable` (rate-limited preview model). Added a 3-attempt retry with backoff in `ai_coach/llm_client._chat_google()` so coach queries no longer fail transiently.
- **`/api/icu/sync` ImportError (silent)**: the endpoint called `training.fetch_athlete_numbers`, which doesn't exist → `athlete_numbers: {"skipped":"nums_err:ImportError"}`. Removed the bad call; athlete numbers are already served by `/api/icu/athlete-numbers`. Sync now returns clean data.
- **Security**: removed live API keys (Intervals.icu + Gemini) from `test_smoke.py` and purged the file from git history (GitHub push-protection compliant). Test credentials now come from env vars.



### Fixed
- **Tabs not opening on click**: the dynamic `renderTabs()` rebuilt the tab bar with `innerHTML = ''`, dropping the click listeners. Reverted to static tabs in the HTML + a lightweight `applyTabVisibility()` that only toggles `display`, so click handlers stay attached. Tabs now open correctly.
- **Intervals.icu "Connect" (login) failed**: the API-Key connect path posted `api_key`/`athlete_id` but the backend save endpoint expects `icu_api_key`/`icu_id`. Corrected the field names in `connectIcuApiKey()` so the Settings → Connections → API Key flow actually persists and connects (verified: `connected: true, method: apikey, write_ok: true`).

### Changed
- **New app icon** — racing-gradient disc with a cycling wheel, an analytics line chart and a lightning bolt (generated `assets/icon.ico` / `icon_512x512.png`).



### Added
- **AI Coach chat is now functional**: new `/api/ai/settings` endpoint persists LLM provider + key (stored in gitignored `ai_config.json`, never committed) and toggles the coach on/off at runtime. Verified live with Google Gemini (`gemini-3-flash-preview`) and Groq.
- **Gemini client fix**: `_chat_google` now forwards the `system` instruction (previously ignored), so the coach's Friel-style system prompt is honored.

### Fixed
- `get_client()` was called with invalid `provider=` kwarg — now passes `config_section` dict (matches `LLMClient.from_config`).
- RAG context now reads real HRV/weight/FTP from the intervals.icu sync store (verified live: FTP 200W, HRV avg 57ms, weight 70kg, RHR 48).

### Verified live (real athlete data)
- AI Coach query grounded in real rider data ✅
- Persistent memory (8 entries saved across sessions) ✅
- intervals.icu connect / sync / plan push ✅



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