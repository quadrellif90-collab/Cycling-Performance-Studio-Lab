# Cycling Performance Studio Lab v1.1.3

**AI Coach goes live.** The chat, weekly-analysis and plan-generation endpoints now actually talk to an LLM. A new settings endpoint lets you plug in any provider (OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, OpenRouter, local Ollama/LM Studio) without editing code or restarting.

## What's new
- **`/api/ai/settings`** — set provider + API key + model and enable the coach from the UI/API. The key is stored **only** in `ai_config.json` (gitignored — never committed to the repo).
- **Gemini client fix** — the Google path now forwards the system instruction, so the coach's Friel-style prompt is actually applied (previously dropped).

## Verified live with real athlete data
- ✅ AI Coach query **grounded in YOUR data**: FTP 200W, weight 70 kg, HRV avg 57 ms, RHR 48 bpm → coach replied with a Friel-style analysis (e.g. *"2.85 W/kg, in base-building phase; HRV 57ms + RHR 48 = autonomic balance, no overreach"*).
- ✅ Persistent memory across sessions (8 entries saved).
- ✅ intervals.icu connect / HRV sync / plan → calendar push (from v1.1.1–1.1.2).

## How to enable the coach
1. Settings → AI Coach → pick provider (e.g. **Google Gemini**, model `gemini-3-flash-preview`) and paste your API key.
2. The coach is immediately available in the AI Coach tab. For best results, connect intervals.icu first so the RAG context is populated.

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.1.3-linux-x86_64.tar.gz` |
