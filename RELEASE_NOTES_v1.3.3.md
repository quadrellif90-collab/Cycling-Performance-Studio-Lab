# CPSL v1.3.3 — Deepscan A→Z

**Tipo:** stability · **Copertura:** 108 moduli Python, 23.228 righe frontend, 273 endpoint API, 6 template, 4.306 workout

## Corretto in questa release
- **Card qualità HRV nel tab sempre "—"**: ID duplicato con la card Home faceva aggiornare quella sbagliata
- **5 variabili CSS mai definite** (`--text1 --bg2 --accent-bg --amber --dev-red`): colori imprevedibili ora deterministic
- **4 dipendenze non dichiarate**: certifi, bleak (trainer BLE), fitparse (FIT), garminconnect
- **Rimosso dead code JS** (25 KB): `app.js`/`analytics.js` non caricati da nessuna pagina

## Esito scansione completa
| Area | Esito |
|------|-------|
| Sintassi Python | 108/108 OK |
| API sweep | 159 GET + 114 POST — zero 5xx |
| Frontend | 0 duplicati reali, 0 tab orfani, asset completi |
| Sicurezza | Nessun segreto nel repo, .env non tracciati |
| Push Intervals.icu | Confermato funzionante (6 eventi pushati nei log reali) |
| Parità PCC/Domestique | Completa + 21 moduli esclusivi CPSL |

## Miglioramenti proposti (roadmap)
1. **Endpoint stato push ICU** (`GET /api/icu/push/status`) + card "ultimo push: 6 eventi, 14g fa"
2. **Cronologia versioni piano** con restore UI dalle snapshot .bak esistenti
3. **Digest giornaliero notifiche** (il motore notifications.py è completo ma non cablato in app.py)
4. **Export piano PDF** (PyMuPDF già presente; plan_export fa HTML)
5. **Vista mobile/PWA** (PCC aveva una SPA mobile; CPSL no)
