# CPSL v1.4.4 — HRV Pipeline + WKO5 Radar + Graphics Fixes

## ❤️ HRV Pipeline (flusso corretto)

**Prima:** Huawei → export ZIP manuale → import in CPSL (rotto, confuso)
**Ora:** Huawei/Garmin/Whoop → Intervals.icu (sync automatico) → **CPSL legge da ICU** → calcola RMSSD/SDNN/pNN50/CV/baseline → **scrive su ICU** (solo se mancanti)

- `_process_hrv_from_sync()` aggiunta al post-sync: dopo ogni sync ICU elabora HRV automaticamente
- Card "Huawei Health / HRV" rimossa dalla Home (confondeva gli utenti)
- Branding Huawei rimosso dal tab HRV
- Write-back via `push_daily_hrv_to_icu()`: scrive solo valori mancanti, non sovrascrive Garmin/Whoop

## 📊 WKO5 Radar

- **Power Profile Radar**: 5 assi (Sprint NM, Anaerobica, VO2max, Soglia, Endurance) con benchmark élite
- **Power-Duration Curve**: scatter con modello CP+W' overlay
- Entrambi nel tab Analysis, stile Chart.js radar

## 🔧 Altri fix
- OAuth nascosto quando client_secret non configurato; API key promossa
- Token scaduto → fallback automatico API key senza intervento utente
- Schede Home che apparivano su tutti i tab → risolto (nesting sec-home)
- Build hygiene: pulizia cache prima di PyInstaller
