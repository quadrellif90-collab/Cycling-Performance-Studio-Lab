# CPSL v1.3.4 — Nuove funzionalità dalla roadmap

**Tipo:** feature release · **Origine:** indagine post-deepscan (moduli mai cablati)

## 📋 "Il tuo giorno" — Digest giornaliero (Home)
Il motore notifiche di `notifications.py` esisteva da v1.x con **13 renderer ma era cablato solo al 6%**. Ora una nuova card in Home li aggrega tutti con i tuoi dati reali:
- 🌅 Morning Readiness + 🚦 stato del giorno (RLGL)
- 🎯 Workout del giorno + 🔁 consiglio swap se la readiness è bassa
- 🍎 Reminder fueling per sessioni lunghe
- 📉 Trend HRV vs baseline · 🔁 Alert monotonia (Foster 1998)
- 📅 Weekly review · 🏁 Countdown gara

## ⬇ Export piano PDF
Nuovo bottone **PDF** nel tab Plan. Usa PyMuPDF quando presente; sulle macchine senza VC++ Redistributable (dove la sua DLL non carica) passa automaticamente a un writer PDF integrato a mano — l'output è sempre un PDF valido.

## 🚴 GPX → Golden Cheetah
`gpx_to_gc.py` (14 KB) era nel progetto da sempre senza alcun endpoint. Ora carichi un .gpx e scarichi il .crs pronto per Golden Cheetah.

## ✈ Esito push ICU sempre visibile
Sotto il bottone "Push to intervals.icu calendar" ora compare l'esito dell'ultimo reconcile — anche quelli automatici giornalieri: `✓ Ultimo push <data>: N inviati, N aggiornati, N rimossi`.

## Verifiche
- Card digest live nel browser: badge GREEN, 3 notifiche renderizzate, 0 errori JS
- PDF scaricato e valido (%PDF- header) via fallback writer
- Suite pytest completa verde

**Nota investigazione:** i 7 moduli sospetti come orfani erano in realtà cablati (import lazy); solo notifications era sottoutilizzato → ora valorizzato.
