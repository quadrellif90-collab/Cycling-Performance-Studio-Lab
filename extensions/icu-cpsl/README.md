# CPSL for Intervals.icu — Estensione Browser (Proof of Concept)

Estensione Chrome/Edge (Manifest V3) che porta **Cycling Performance Studio Lab**
dentro la pagina dell'atleta su [intervals.icu](https://intervals.icu).

## Cosa fa
- Si aggancia alla pagina atleta di intervals.icu (`content.js`).
- Legge l'`athleteId` dall'URL.
- **Se CPSL è in esecuzione in locale** (default `http://127.0.0.1:22400`): chiama
  `GET /api/icu/extension/context?athlete_id=...` e mostra i valori calcolati
  *ufficiali* di CPSL (Forma/CTL, Fatica/ATL, Equilibrio/TSB, HRV, HRV 14gg, Peso).
- **Se CPSL non è attivo**: calcola gli stessi indicatori lato client leggendo le API
  REST di intervals.icu (con la tua API key personale, salvata nelle Options).
- Pulsante **"Apri in CPSL"** → apre l'app locale passando l'atleta.

## Installazione (load unpacked — dev)
1. Apri `chrome://extensions` (o `edge://extensions`).
2. Attiva **Modalità sviluppatore** (in alto a destra).
3. **Carica estensione non pacchettizzata** → seleziona la cartella
   `extensions/icu-cpsl/`.
4. Clicca sull'icona dell'estensione → **Opzioni** → incolla la tua
   **Intervals.icu API Key** (la stessa usata in CPSL → Settings → Connections).
5. Vai su `https://intervals.icu/athlete/<tuo_id>/...` → in cima alla pagina
   compare il pannello **CPSL**.

## Bridge lato CPSL (richiesto per i valori ufficiali)
L'endpoint è già presente in `app.py`:

```
GET /api/icu/extension/context?athlete_id=i130499
→ { "ok": true, "athlete_id": "i130499",
    "indicators": { "ctl": 21.3, "atl": 2.9, "tsb": 18.4,
                    "hrv": 49.3, "hrvAvg14": 65.2, "weight": null, "samples": 90 },
    "source": "CPSL local" }
```

L'estensione lo chiama solo se CPSL risponde entro 1.5s; altrimenti ricade sul
calcolo client-side via API ICU.

## File
| File | Ruolo |
|------|-------|
| `manifest.json` | Manifest MV3 (content script su `intervals.icu/*`) |
| `content.js` | Logica: parse URL, fetch dati, render pannello, bridge CPSL |
| `options.html` / `options.js` | Inserimento API key ICU (salvata in `chrome.storage.local`) |
| `styles.css` | Stile pannello iniettato |
| `make_icons.py` | Genera le icone PNG |

## Note / limiti del POC
- È una **content-script injection**, non l'iframe ufficiale del framework
  "Community Extensions" di intervals.icu (che richiederebbe un sito pubblico
  hostato da noi che ICU carica). Questo approccio funziona subito con load unpacked
  e non richiede hosting.
- La API key ICU è salvata solo nel browser dell'utente (`chrome.storage.local`),
  mai inviata a server terzi.
- Nessun dato CPSL viene esfiltrato: il bridge gira solo su `127.0.0.1`.

## Prossimi passi (se si decide di proseguire)
- [ ] Portare su **iframe ufficiale Community Extensions** di ICU (necessita hosting).
- [ ] Aggiungere fenotipo, durabilità e DFA α1 calcolati da CPSL nel bridge.
- [ ] Packaging `.crx` / pubblicazione su Chrome Web Store ed Edge Add-ons.
- [ ] Widget desktop Windows always-on (pywebview) come complemento.
