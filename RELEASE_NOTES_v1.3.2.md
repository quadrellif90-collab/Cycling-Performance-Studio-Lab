## 🤖 AI Coach integrato nel Pianificatore

Nuovo pannello **"Chiedi all'AI Coach"** nel tab Plan: parere LLM groundato sui tuoi dati reali (FTP, HRV, fenotipo, stato piano + memoria sessioni) con **azione applicabile in un click**:

- `Adatta la sessione di oggi` → riduzione/scarico
- `Ricalcola il piano da oggi` (riprevisione)
- `Rigenera il piano da zero`

Il backend (`/api/ai/coach-query`) ora restituisce `suggested_action` e `plan_state`. Verificato live contro Google Gemini (retry automatico su 503 → 200).

## 🔧 6 API rotte corrette (sweep completo: 138 GET + 109 POST testati)

- `/api/export/backup|metrics|zip` — chiamavano funzioni inesistenti; ricollegate alle firme reali di data_export
- `/api/onboarding/status` — `_plan_dir` mai definita in pcc_routes_v2, aggiunta copia profile-aware
- `/api/terra/status` — funzione annidata per errore + config senza getattr
- `/api/workouts/classify` — modulo classify_library_content.py mancante dal repo, recuperato da PCC

## ✅ Scenari end-to-end verificati sull'app reale

- Generazione piano 8 settimane + daily-sync che riconcilia gli actuals (rest→z2 con TSS)
- HRV −12% + sonno 5h + TSB −25 → raccomandazione riduzione/riposo ✓
- HRV buona + TSB positivo → nessun blocco forzato ✓
- Monotonia 2.2 (> soglia rossa 2.0) → warning monotonia ✓
- Cambio goal → rigenerazione coerente ✓
- Catena auto-adjust + drift ✓

**Download:** zip Windows 64-bit windowed (nessun terminale). Dati utente in ~/.cpsl intatti.
