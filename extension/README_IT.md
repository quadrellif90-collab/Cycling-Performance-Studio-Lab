# Montis IT · CPSL Edition v2.0

Estensione browser (Manifest V3) **completamente autonoma** che trasforma
**app.montis.icu** in un'esperienza italiana con i calcolatori CPSL integrati.
**Nessuna app locale, nessun server, nessun processo in background.**

## Cosa fa

1. **Traduzione italiana completa** — ~350 stringhe applicate in tempo reale su
   tutte le pagine (anche `aria-label`, `title`, `placeholder`).
2. **Calcolatori CPSL integrati (JS)** — pannelli **CPSL+** calcolati nel browser:
   - **Prontitudine Composita 0-10**: porting JS di `readiness_composite.py`
     (z-score individuali su baseline personale, ln(RMSSD) media mobile 7 giorni,
     TSB, FC a riposo invertita, sonno — pesi rinormalizzati quando un componente
     manca, confidenza = somma pesi disponibili)
   - **Segnali autonomici**: deviazione ln(RMSSD), stabilità HRV 14g
     (1 − std/mean), stato autonomico 42g
   - Gestione automatica del ritardo dei dati (usa l'ultimo giorno con HRV)

## Da dove prende i dati

Dalla **cache locale di Montis stessa** (`montis_wellness_dashboard` in
localStorage): la serie giornaliera di 42 giorni con HRV, FC a riposo, sonno,
CTL/ATL che l'app ha già scaricato da Intervals.icu. L'estensione legge solo
la pagina su cui gira — nessun dato lascia il browser, nessuna credenziale
viene toccata.

> Se la serie non è ancora in cache, apri una volta la pagina Panoramica o
> Benessere di Montis: l'estensione calcola subito dopo.

## Installazione

1. Apri `chrome://extensions` (o `thorium://extensions`)
2. Attiva **Modalità sviluppatore**
3. **Carica estensione non pacchettizzata** → seleziona questa cartella
4. Apri/ricarica `https://app.montis.icu`

## File

| File | Ruolo |
|------|-------|
| `manifest.json` | Manifest MV3 — nessun permesso host, nessun background |
| `content/translate.js` | Dizionario EN→IT + osservatore mutazioni |
| `content/engine.js` | Motore CPSL in JS (readiness composita, ln-RMSSD, stabilità) |
| `content/cpsl.js` | Iniezione pannelli CPSL+ con auto-reinject su navigazione SPA |
| `content/style.css` | Stile pannelli coerente col design system di Montis |

## Note

- I nomi degli allenamenti della libreria personale NON vengono tradotti (dati).
- Se un giorno Montis cambia la struttura della cache wellness, il pannello
  mostra un messaggio chiaro invece di rompersi.
- Il motore CPSL completo (fit dei modelli CP, parsing ride, durability su
  stream di potenza) resta nel progetto
  [Cycling-Performance-Studio-Lab](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab)
  per chi vuole l'analisi completa.
