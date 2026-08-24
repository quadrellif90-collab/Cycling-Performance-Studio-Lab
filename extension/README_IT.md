# Montis IT · CPSL Edition

Estensione browser (Manifest V3) che trasforma **app.montis.icu** in un'esperienza
completamente in italiano e aggiunge i pannelli calcolatori avanzati del motore
locale **CPSL** (Cycling Performance Studio Lab).

## Cosa fa

1. **Traduzione italiana completa** — dizionario di ~350 stringhe applicato in tempo
   reale via MutationObserver su tutte le pagine (Panoramica, Micro, Meso, Macro,
   Calendario, Preparazione, Sandbox, Profilo Atleta, Benessere, Chat, Cronologia, Help).
   Traduce anche `aria-label`, `title` e `placeholder`.
2. **Pannelli CPSL+** — nelle sezioni "Prontitudine e Operazioni", "Durabilità (ISDM)"
   e "Andamento temporale (W′ BAL)" inserisce schede extra alimentate dal motore locale:
   - Prontitudine Composita multi-fattore (`/api/readiness/composite`)
   - Durability con ancoraggio sul lavoro cumulativo kJ (`/api/durability-trend`)
   - Stato del motore fisiologico aggiornato (W′bal Skiba 2015 a τ variabile,
     DFA α1 doppia scala, baseline HRV ln(RMSSD))

## Requisiti

- Browser Chromium/Thorium/Chrome/Edge/Brave
- **CyclingPerformanceStudioLab** in esecuzione sulla porta 22400 (l'app exe avvia
  il server automaticamente). Senza il motore locale l'estensione traduce comunque
  tutto; i pannelli mostrano un avviso finché il motore non è raggiungibile.

## Installazione permanente (consigliata)

1. Apri `chrome://extensions` (o `thorium://extensions`)
2. Attiva **Modalità sviluppatore** (interruttore in alto a destra)
3. Clicca **Carica estensione non pacchettizzata**
4. Seleziona questa cartella (`montis-extension`)
5. Apri/ricarica `https://app.montis.icu`

## Avvio rapido con estensione già caricata (alternativa)

```
thorium.exe --load-extension="C:\Users\Siviglino\Desktop\PPC\montis-extension"
```

## File

| File | Ruolo |
|------|-------|
| `manifest.json` | Manifest MV3, permessi solo su `127.0.0.1:22400` |
| `background.js` | Service worker: proxy fetch verso il motore locale (evita CORS/mixed-content) |
| `content/translate.js` | Dizionario EN→IT + osservatore mutazioni |
| `content/cpsl.js` | Iniezione pannelli CPSL+ con auto-reinject su navigazione SPA |
| `content/style.css` | Stile pannelli coerente col design system shadcn di Montis |

## Note tecniche

- La traduzione usa match esatto case-insensitive + normalizzazione spazi, con
  fallback a sostituzioni parziali per stringhe dinamiche ("REPORT STATUS:",
  "Ultimo aggiornamento:", …).
- I pannelli si reiniettano automaticamente dopo i re-render React dell'app.
- I nomi degli allenamenti della libreria personale NON vengono tradotti (sono dati).
- Nessun dato lascia il PC: la comunicazione è solo verso `http://127.0.0.1:22400`.
