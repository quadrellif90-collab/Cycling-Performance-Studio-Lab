# Cycling Performance Studio Lab v1.2.1

**Every user brings their own LLM key — no shared secrets, and they're never bundled.**

## Added
### 🔑 Per-user API keys
The AI Coach configuration (Settings → AI Coach) now makes explicit that **each end user must enter their own provider API key** — the app never uses a bundled/shared key. To make onboarding frictionless:
- The API Key field is labeled **"API Key (la tua, personale)"** with a clear hint.
- A contextual **"🔗 Crea API Key su [Provider]"** link appears under the field and updates live when you change the provider dropdown, pointing straight at that provider's key-signup page:
  - Google AI Studio, OpenAI, Anthropic, Groq, DeepSeek, Mistral, OpenRouter, xAI, Ollama.

### 🛡️ Build hardening
`ai_config.json` and `*.env` are now explicitly excluded from the PyInstaller build, so **no local secrets ship inside** the distributed `CyclingPerformanceStudioLab.exe` / `.dmg` / `.tar.gz`. Combined with the existing `.gitignore`, the AI/ICU keys stay strictly on the user's machine.

## Notes
- Carries over everything from v1.2.0 (LLM fallback, config export/import, CI smoke-test, granular ICU errors, rate-limit retries).

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.2.1-linux-x86_64.tar.gz` |
