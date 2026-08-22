# CPSL v1.4.5 — Personalizzazione layout: bottoni accessibili + drag robusto

**Tipo:** feature + hardening · **Modulo:** `frontend/static/js/dashboard_layout.js`

## Cosa c'è di nuovo

### 🔘 Bottoni di controllo su ogni card (edit mode)
In modalità "Personalizza layout" ogni card della Home mostra ora una barra di
controllo in alto a destra con 4 bottoni:

| Bottone | Azione |
|---------|--------|
| ◀ | Sposta la card a sinistra |
| ▶ | Sposta la card a destra |
| + | Allarga (span +1 colonna) |
| − | Restringi (span −1 colonna) |

Ogni click salva subito il layout (`homeLayout:<profilo>`), quindi l'ordinamento
e le dimensioni sopravvivono al reload. I bottoni sono cliccabili anche dove il
drag è scomodo (touch, precisione ridotta) e rendono la feature accessibile.

### 🧪 API programmatiche (test + accessibilità)
- `window._layoutMoveCard(fromIdx, toIdx)` — sposta una card per indice
- `window._layoutResizeCard(id, span)` — imposta lo span di una card
- `window._layoutResetLayout()` — ripristina default

## Fix di robustezza

1. **`setPointerCapture` protetto con try/catch**: con pointer sintetici o già
   rilasciati l'eccezione interrompeva l'inizializzazione del drag/resize.
   Ora il trascinamento parte comunque (il capture è un'ottimizzazione, non un
   requisito).
2. **CSS `pointer-events` corretto in edit mode**: la regola che disabilita
   l'interattività del contenuto card esclude ora esplicitamente
   `.dl-card-controls`, senza i quali i bottoni non erano cliccabili.
3. **Listener pointermove/up/cancel su `document`**: gli eventi retargetizzati
   dal pointer capture raggiungono sempre gli handler anche fuori dalla griglia.

## Verifica (Playwright, Chromium headless — 8/8 ✅)

| Test | Esito |
|------|-------|
| Toolbar edit mode | ✅ |
| Barre controllo presenti su tutte e 5 le card | ✅ |
| ▶ sposta destra → scambio ordine | ✅ |
| ◀ sposta sinistra → ritorno all'origine | ✅ |
| + / − resize → span 4→5→4 | ✅ |
| Persistenza span dopo reload | ✅ |
| Reset ai default | ✅ |
| Drag reale (PointerEvent dispatchati) riordina + persiste | ✅ |

> Nota: la sintesi input mouse di Playwright headless non completa le sequenze
> pointer-capture; la logica di drag è verificata con PointerEvent reali
> dispatchati attraverso i medesimi handler.

## File toccati
- `frontend/static/js/dashboard_layout.js` — bottoni, API, try/catch, CSS
- `tests/test_dashboard_layout_ui.py` — nuova suite UI (8 test)
- `VERSION` → 1.4.5
