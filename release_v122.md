# Cycling Performance Studio Lab v1.2.2

**Proof-of-concept: CPSL lives inside Intervals.icu. Plus a CI fix.**

## Added
### 🧩 Estensione CPSL per Intervals.icu (POC)
New `extensions/icu-cpsl/` — a Chrome/Edge (Manifest V3) extension that injects a **CPSL panel** directly into the intervals.icu athlete page:
- **Forma (CTL)**, **Fatica (ATL)**, **Equilibrio (TSB)**, **HRV**, **HRV 14gg**, **Peso** — computed from the athlete's intervals.icu data.
- **If CPSL is running locally** (`127.0.0.1:22400`): shows CPSL's *authoritative* values via the new bridge endpoint.
- **If CPSL is closed**: computes the same indicators client-side from intervals.icu REST APIs, using the user's own API key (stored only in the browser via `chrome.storage.local`).
- **"Apri in CPSL"** button → opens the local app with the athlete pre-selected.

Install: `chrome://extensions` → Developer mode → Load unpacked → select `extensions/icu-cpsl/`. Then Options → paste your intervals.icu API key. Full guide in `extensions/icu-cpsl/README.md`.

### 🔌 Bridge endpoint
`GET /api/icu/extension/context?athlete_id=...` returns CPSL-computed indicators (reuses the AI Coach RAG wellness loader). Verified live with real data: CTL 21.3, ATL 2.9, TSB +18.4, HRV 49.3 ms, HRV 14gg 65.2 ms.

## Fixed
- **CI pytest hang**: `test_smoke.py` was collected by pytest as a test (matched `test_*.py`) and hung on network timeouts to `127.0.0.1:22400`. Renamed to `smoke_test.py` (no pattern match) and updated the CI job. CI now finishes in normal time.

## Notes
Carries over v1.2.0 + v1.2.1 (LLM fallback, per-user keys + signup links, config export/import, ICU granular errors, rate-limit retries, CI live smoke-test).

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.2.2-linux-x86_64.tar.gz` |
