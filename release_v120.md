# Cycling Performance Studio Lab v1.2.0

**AI Coach is now fully configurable from the UI, resilient to rate-limits, and CI-verified.**

## Added
### 🎛️ LLM provider settings UI
Settings → **AI Coach** tab now has a complete configuration panel:
- Provider picker (Google Gemini, OpenAI, Anthropic, Groq, DeepSeek, Mistral, OpenRouter, xAI, Ollama)
- Model field (e.g. `gemini-3-flash-preview`, `gpt-4o`, `llama-3.1-70b-versatile`)
- API key (saved only to gitignored `ai_config.json`)
- **Optional fallback provider** — if the primary errors (e.g. Gemini 503/rate-limit), the coach automatically retries on the fallback before giving up.

### 💾 Config export / import
- `Esporta` downloads `cpsl-ai-config.json` (provider/key/model/fallback)
- `Importa` restores it — so wiping a profile no longer loses the AI Coach setup

### 🔁 Provider fallback (engine)
`ai_coach/llm_client` retries failed calls on the configured fallback provider, and retry-with-backoff on HTTP 429/503 now covers **all** OpenAI-compatible providers (previously Gemini-only).

### 🤖 CI live smoke-test
The GitHub workflow now boots the app and runs `test_smoke.py` against every functional endpoint. Credentials come from **GitHub secrets** (`CPSL_ICU_KEY`, `CPSL_ICU_ID`, `CPSL_LLM_KEY`) — never committed to the repo.

## Fixed
- **ICU sync silent failure**: `/api/icu/sync` now checks the connection first and returns a clear `not_connected` error instead of a silent 500; wellness errors include the exception message.
- **Rate-limit resilience** extended to all providers.

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.2.0-linux-x86_64.tar.gz` |
