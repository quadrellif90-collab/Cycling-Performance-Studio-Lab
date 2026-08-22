# CPSL v1.4.6 — Fix totali: pulizia errori console e diagnostica

**Tipo:** bugfix · **Scope:** `app.py`, `frontend/templates/dashboard.html`

Ri-analisi A→Z autonoma (sweep 14 tab + 38 endpoint + console/reti) che ha
portato a **zero 404, zero errori JS, zero warning console**.

## Fix

### 1. Doppio 404 su `/api/rides/icu_*` al load (console)
`maybeShowFtpTestModal()` scandisce le prime ride al load per cercare il
suggestion FTP-test; per le attività sincronizzate da Intervals.icu (id `icu_*`,
senza FIT locale) la fetch del dettaglio rispondeva 404 — gestita ma rumorosa.
Ora lo scan salta le voci `source:"icu"`: lo stamp FTP nasce solo dal parser
FIT locale o dalle sessioni JSON legacy.

### 2. Warning DOM "Password field is not contained in a form"
La input API-key ICU era libera nel DOM. Ora è dentro un `<form>` con submit
gestito: warning eliminato e **il tasto Enter invia** la chiave.

### 3. Health check `rides_dir` sul path legacy
`/api/diag/health` controllava ancora `~/.cpsl/rides` (path globale pre-v3.0,
mai più scritto → `exists:false`). Ora usa `_fit_rides_dir()` per-profilo e
riporta il percorso reale verificato.

### 4. Card "Configurazione LLM" completamente morta (ReferenceError)
I 5 handler richiamati (`saveAiSettings`, `disableAiSettings`, `exportAiConfig`,
`importAiConfig`, `renderAiProviderLinks`) **non esistevano da nessuna parte**:
ogni click/cambio lanciava ReferenceError e i campi non salvavano nulla.
Sostituita con una card onesta che documenta le variabili d'ambiente reali
usate da `ai_coach/llm_client.py` (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, …)
con esempio `setx`.

## Verifica

| Check | Prima | Dopo |
|-------|-------|------|
| Risposte ≥400 su sweep completo 14 tab | 2× 404 icu rides | **0** |
| Errori console "Failed to load resource" | 2 | **0** |
| Warning console (password/form) | 1 | **0** |
| Suite QA completa (`tests/qa_full_az.py`) | — | **25/25 ✅** |
| `/api/diag/health` rides_dir | exists:false | **exists:true (per-profile)** |

## File toccati
- `app.py` — health check per-profilo
- `frontend/templates/dashboard.html` — fix 1, 2, 4
- `VERSION` → 1.4.6
