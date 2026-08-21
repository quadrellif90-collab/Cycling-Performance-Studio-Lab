# Cycling Performance Studio Lab v1.1.6

**AI Coach now survives restarts.** A boot-load ordering bug meant the coach stayed disabled after a server restart even though settings were saved.

## Fixed
### 🤖 AI Coach auto-enables on boot
Persisted settings in `ai_config.json` (provider / key / model / enabled) were only applied inside the FastAPI `lifespan()` hook, which didn't reliably re-enable the coach — `GET /api/ai/status` reported `ai_coach_enabled: false` after every restart. Moved the load to **module-import time** so the coach is enabled the moment the app starts. Verified live: status returns `enabled: true, provider: google, model: gemini-3-flash-preview` immediately after launch, and `POST /api/ai/coach-query` answers using your real RAG data (FTP 237W, HRV 57ms).

## Notes
- No secret leakage: `ai_config.json` is gitignored; `test_smoke.py` reads credentials from env vars only.
- Combined with v1.1.5 (Gemini 503 retry + sync ImportError fix + history secret purge), the AI Coach pipeline is now stable end-to-end.

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.1.6-linux-x86_64.tar.gz` |
