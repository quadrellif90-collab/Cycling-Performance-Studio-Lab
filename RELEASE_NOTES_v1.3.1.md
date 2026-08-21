# CPSL v1.3.1 — Release di Stabilità

**Data:** 21 agosto 2026 · **Tipo:** bugfix release · **Test:** 245 pytest + live UI automation 14/14 tab

## Perché questa release

La v1.3.0 aveva un difetto di packaging invisibile ma devastante: **Chart.js era referenziato ma mai incluso nel repository**. Tutte le schede che disegnano un grafico (Analysis, Plan, HRV, DFA, Home) fallivano silenziosamente — l'origine principale dei report "le schede non si aprono / il pianificatore non funziona".

## Correzioni principali

| Problema | Impatto | Stato |
|----------|---------|-------|
| Chart.js assente dal repo | Grafici morti in tutte le schede | ✅ Bundle Chart.js 4.4.3 |
| Deadlock Workout Player | Freeze su skip/pausa durante playback | ✅ Lock ridotto allo snapshot; BLE fuori lock |
| Sintassi Python in app.js | Frontend interamente bloccato | ✅ Riscritta |
| Banner onboarding duplicato | Striscia non dismissabile su ogni tab | ✅ Rimossa |
| 4 bottoni morti (Push ICU, Auto nutrizione, Import Huawei, Inietto multidisciplina) | Click senza effetto | ✅ Implementati |
| Tab orfano "Workout Player" | Click senza effetto | ✅ Rimosso |
| Asset statici 404 (favicon, icon, cpsl_ui.css) | Errori console, pagine degradate | ✅ Aggiunti |

## Rimozioni

- Estensione browser `extensions/icu-cpsl/` e bridge `/api/icu/extension/context` (decisione owner: non utilizzabile così com'era).

## Verifica (app reale, browser automation)

- **14/14 tab** si aprono e diventano visibili
- Pianificatore: configurazione apre/chiude, Generate Plan → 12 settimane, calendario 25 righe con fasi/TSS, metriche CTL/FTP/W/kg
- 0 errori JavaScript di pagina; connessione Intervals.icu OK
- Suite pytest completa verde (245 test)

## Download

- `CyclingPerformanceStudioLab-v1.3.1-win64.zip` — Windows 64-bit, windowed (nessun terminale). Estrai ed esegui `CyclingPerformanceStudioLab.exe`.

## Upgrade

Sostituisci la cartella dell'app precedente. I dati utente restano in `~/.cpsl` e non vengono toccati.
