## 🎉 Cycling Performance Studio Lab v3.11.0

### Nuove Funzionalità: AI Coach

**Multi-Provider LLM Client** (14 provider supportati):
- OpenAI, Anthropic, Google, Mistral, DeepSeek, Groq, OpenRouter
- Ollama, LM Studio, Perplexity, Replicate, Cohere, xAI, Azure
- Zero nuove dipendenze (usa solo httpx)

**5 API Endpoint FastAPI** (`/api/ai/*`):
- `GET /api/ai/status` - Stato AI Coach e provider configurato
- `POST /api/ai/weekly-analysis` - Analisi settimanale completa con LLM + dati CPSL nativi
- `POST /api/ai/generate-plan` - Genera piano settimanale personalizzato
- `POST /api/ai/friel-assessment` - Assessment stile Friel (CTL/ATL/TSB, polarizzazione, durabilità)
- `GET /api/ai/friel-prompts` - Template prompt coaching Friel

**Integrazione Frontend:**
- Nuovo tab "AI Coach" in dashboard
- Chat interface per domande naturali
- Generazione piani personalizzati
- Assessment Friel integrato

**Feature Flags** (tutti disabilitati di default):
- `AI_COACH_ENABLED` - Attiva/disattiva AI Coach
- `AI_LLM_PROVIDER` - Scegli provider (14 opzioni)
- `AI_LLM_MODEL` - Modello specifico per provider
- `AI_LLM_API_KEY` - Chiave API provider
- `AI_LLM_TEMPERATURE` / `AI_LLM_MAX_TOKENS` - Parametri modello
- `ENABLE_TP_MCP` - TrainingPeaks MCP (opzionale)

### Architettura Additiva:
- Zero regressioni sui 214 test esistenti
- Feature flaggato: attivabile solo se l'utente lo vuole
- Sfrutta moduli CPSL nativi: CP/W', phenotype, durabilità, phase detection
- Integrazione Friel prompts da rbrands/intervals-icu-sync

### Test Results
- ✅ 214 test passati (0 errori)
- ✅ Zero regressioni su moduli core
- ✅ Import moduli AI Coach puliti

### Moduli Core CPSL Sfruttati:
- `power_duration_model.py` - CP/W' fitting Morton 3P
- `phenotype.py` - Classificazione atleta (6 tipi, 5 assi)
- `durability_score.py` - Xert-style durability
- `training_phase_detector.py` - 6 fasi training auto-detect
- `adaptive_planner.py` - 5 metodologie training
- `analytics.py` - Polarizzazione Treff PI dual