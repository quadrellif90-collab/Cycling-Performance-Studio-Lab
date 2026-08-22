# CPSL v1.4.3 — Fix: schede che restavano attive su altri tab

**Tipo:** bugfix critico · **Causa radice:** tag `</div>` di chiusura di `#sec-home` nella posizione sbagliata

## Il problema

7 card della Home erano **fuori da qualsiasi sezione** a causa di un errore di nesting HTML:

- Distribuzione intensità settimanale
- Nutrizione
- Integrazione
- Adattamento giornaliero
- Forza & Mobilità
- Il mio calendario
- Huawei Health / HRV

Poiché non era contenuta in nessun `<div class="section">`, queste card apparivano **su ogni tab** indipendentemente da quale fosse attivo.

## Il fix

Spostato il tag di chiusura `</div>` di `#sec-home` dalla riga 1824 alla riga 2031 (dopo l'ultima card). Ora tutte e 7 le card sono correttamente dentro la sezione Home e appaiono solo quando il tab Home è attivo.

## Verifica (Playwright su browser reale)

| Card | Su Home | Su Analysis |
|------|---------|-------------|
| Distribuzione intensità | ✅ visibile | ✅ nascosta |
| Nutrizione | ✅ visibile | ✅ nascosta |
| Integrazione | ✅ visibile | ✅ nascosta |
| Adattamento giornaliero | ✅ visibile | ✅ nascosta |
| Forza & Mobilità | ✅ visibile | ✅ nascosta |
| Il mio calendario | ✅ visibile | ✅ nascosta |
| Huawei Health/HRV | ✅ visibile | ✅ nascosta |

**Risultato: 0 card orfane visibili su tab non-Home** ✓

## Altri fix in questa release
- Build hygiene: pulizia cache prima di PyInstaller (nessun dato locale nell'exe)
- Privacy: rimossi piani personali da git (`plans/` gitignored)
