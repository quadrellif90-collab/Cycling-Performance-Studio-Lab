# Cycling Performance Studio Lab v1.1.5

**Reliability + security fixes.** Resolves two runtime bugs found during full live endpoint testing, and removes secrets from git history (GitHub push-protection compliant).

## Fixed
### 🤖 AI Coach no longer fails on Gemini hiccups
`gemini-3-flash-preview` is a rate-limited preview model that intermittently returns `503 Service Unavailable`, which made `POST /api/ai/coach-query` fail. Added a 3-attempt retry with exponential backoff in `ai_coach/llm_client._chat_google()` — coach queries now ride through transient 503/429s.

### 🔄 Intervals.icu sync no longer throws a silent ImportError
`/api/icu/sync` called `training.fetch_athlete_numbers`, which doesn't exist → `athlete_numbers: {"skipped":"nums_err:ImportError"}`. Removed the dead call (athlete numbers are already served by `/api/icu/athlete-numbers`). Sync now returns clean data.

### 🔒 Security — secrets purged from history
Live API keys (Intervals.icu + Gemini) were present in `test_smoke.py` and got caught by GitHub push protection. Removed them, made the test read credentials from env vars, and purged the file from git history. No secrets remain in the repo.

## Test coverage
Full live smoke-test against all functional endpoints (profiles, ICU connect/sync/push, AI Coach status/settings/coach-query/memory/rider-context, plan generate/preview/reforecast/availability, settings, BIA/injury/nutrition/DFA, tab configurator, 8 themes). **0 critical (5xx) bugs** after the two fixes above.

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.1.5-linux-x86_64.tar.gz` |
