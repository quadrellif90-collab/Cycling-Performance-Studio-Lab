# CPSL v1.4.2 — Build Hygiene + Privacy

**Tipo:** fix · **Focus:** privacy dati utente, pulizia build, verifica wizard/sync/tab-leak

## 🔒 Privacy
- **Piani personali rimossi dal repo**: `plans/current_plan.json` + esportazioni datate erano tracciati in git — chi clonava il repo vedeva i piani dell'owner. Ora gitignored (file locali intatti).

## 🧹 Build hygiene
- `build_win.bat` ora pulisce `__pycache__`, `.pytest_cache`, `build/`, `dist/` e i piani personali residui **prima** di PyInstaller, così l'exe distribuito non contiene mai stato locale di sviluppo.

## ✅ Verifiche (4 segnalazioni utente)

| Segnalazione | Esito indagine | Azione |
|--------------|---------------|--------|
| Sync ICU "token failed" | OAuth token scade → 401 → auth_disabled → banner rosso "Reconnect" con link a Settings. Comportamento by-design. | Nessuna modifica necessaria: clicca Reconnect nel banner |
| Wizard iniziale mancante | Verificato in ambiente fresco (HOME temporanea): `/` → 307 → `/setup` 200 con 10 input, 14 bottoni, 0 errori JS. Se `~/.cpsl` ha già setup completato non riappare (by design). Riapribile da Settings → "Apri il Wizard di setup" | Nessuna modifica necessaria |
| Profilo personale nel download | `plans/` era in git → **rimosso e gitignored**. `.oauth.env` nell'exe è il client secret installed-app OAuth (non dati utente, documentato in config.py). `profiles/` in git sono profili route (elevazione), non utenti | Fix applicato |
| Card dashboard visibili su altri tab | Test Playwright su tutti i 14 tab: zero leak (1 sezione visibile + 1 tab attivo per switch, nessun overlay fixed). Non riproducibile; possibile rendering WebView2-specific | Da monitorare |

## Download
Zip Windows 64-bit windowed. Dati utente in `~/.cpsl` intatti.
