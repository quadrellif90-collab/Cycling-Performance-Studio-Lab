# Cycling Performance Studio Lab v1.3.0

**CPSL si apre al mondo: estensione browser production-ready, server MCP, import multi-sorgente, metriche da GoldenCheetah e pagina atleta condivisibile.**

## Added

### 🧩 Estensione Intervals.icu production-ready
`extensions/icu-cpsl/` v1.0.0 — riscritta con architettura MV3 completa:
- **Background service worker**: auth centralizzata (API key **o** OAuth bearer token), cache 5 minuti, router messaggi.
- **Popup di stato**: verifica auth e bridge CPSL con un click, accesso rapido ad app e opzioni.
- **Pannello in-page arricchito**: indicatori (CTL/ATL/TSB/HRV/peso) + **ultime 3 attività** (kJ, Training Load) + **prossimi eventi** dal calendario ICU.
- **Sicurezza**: escape HTML su tutti i dati provenienti dalle API; la API key resta solo nel browser.

### 🔌 Server MCP (Model Context Protocol)
`icu_mcp_server.py` — collega il tuo CPSL a Claude Desktop o qualsiasi client MCP:
```
python icu_mcp_server.py
```
5 tool: `wellness_recent`, `rider_context`, `coach_memory_search`, `activities_recent`, `plan_preview`.
Bridge HTTP incluso: `GET /api/mcp/status` · `POST /api/mcp/call`.

### 📥 Import multi-sorgente
- **Garmin Connect** (`POST /api/import/garmin`): HRV, sonno, peso → record wellness. Login device una volta sola, poi token cache (~/.cpsl/garmin_tokens) — le credenziali non vengono mai salvate.
- **File .FIT** (`POST /api/import/fit`): riepilogo attività (durata, distanza, potenza max, HR).
- **File .GPX** (`POST /api/import/gpx`): distanza, dislivello, durata.

### 📊 Metriche avanzate (ispirate a GoldenCheetah)
- **Critical Power + W'** con fit lineare P = CP + W'/t e R² di qualità
- **W' Balance** (modello Skiba): deplezione % durante la gara/allenamento
- **DFA α1**: proxy soglia aerobica da intervalli RR
- **Distribuzione intensità**: classificazione polarizzata / piramidale / soglia
- Endpoint: `POST /api/metrics/power-analysis` (upload FIT), `POST /api/metrics/load-distribution`

### 🌐 Pagina atleta condivisibile
- `GET /export/athlete-page` → pagina HTML self-contained (card statistiche + tabella attività) pronta da condividere
- `GET /api/export/athlete-page` → payload JSON per integrazioni

## Verified live
- MCP: initialize + tools/list + tools/call ✔ · Estensione: 4 JS validati node --check ✔ · GPX upload end-to-end (33.3 km parse) ✔ · Athlete page HTML+JSON con dati reali (CTL 21.3) ✔ · Smoke test 21 aree: 0 bug ✔

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.3.0-linux-x86_64.tar.gz` |
