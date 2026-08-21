# Acknowledgments & Riferimenti

Cycling Performance Studio Lab nasce come fusione di due progetti esistenti e si
basa su ricerca scientifica pubblicata, software open source e dati aperti.
Questo documento riconosce **tutti** i contributi.

---

## 👥 Progetti d'origine e contributori

### Domestique — il progetto fondatore
CPSL è un fork di [Domestique](https://github.com/platypus45/domestique) (v3.5.2,
Apache-2.0), "adaptive cycling training planner: 7 science-grounded
injury-prevention guardrails, 4.232 ZWO workouts, 622 routes, hardware-agnostic".

| Contributore | Commit | Profilo |
|--------------|--------|---------|
| **platypus45** | 649 | [github.com/platypus45](https://github.com/platypus45) |
| **claude** (bot) | 18 | [github.com/claude](https://github.com/claude) |

*Built with PubMed research, 4,232 workouts, and a deep love for cycling* —
Domestique contributors, Copyright 2026 (formerly ChickenCycling).

Tutto il merito per la codebase originale, il build system e gran parte del motore
di training science va agli autori Domestique; riusato sotto Apache License 2.0.

### PCC / PPC — Programming Cycling Coach
Secondo lignaggio fuso in CPSL: fork di Domestique sviluppato da
[quadrellif90-collab](https://github.com/quadrellif90-collab) (2024-2026), autore
dei moduli BIA/nutrizione/diet/HRV-Huawei/metabolic decoder/pedal asymmetry e delle
relative route API. Copyright 2024-2026 PCC contributors.

### CPSL — aggiunte proprie
AI Coach multi-provider con RAG e memoria · fueling planner (evidenze 2024-2026) ·
durability score · phenotype radar · power-duration model 3P · training phase
detector · workout player con controllo trainer BLE · MCP server · daily digest ·
cronologia versioni piano · export PDF/GPX→CRS · deepscan/QA automation.

---

## 🧪 Calcolatori, formule e fonti scientifiche

Ogni calcolatore dell'app mappa su letteratura peer-reviewed. L'implementazione è
indipendente; le citazioni sono per attribuzione e non implicano approvazione degli
autori citati.

| Calcolatore / Funzione | Modello | Fonte primaria |
|------------------------|---------|----------------|
| FTP estimation | Scaling factors Coggan da best efforts | Coggan & Allen (2019). *Training and Racing with a Power Meter*, 4th ed. |
| Critical Power | Monod–Scherrer 2P; Morton 3P; Marinescu | Poole et al. (2016). CP: fatigue threshold. MSSE 48(11); Jones et al. (2019). |
| W' balance (W'bal) | Skiba exponential reconstitution | Skiba et al. (2015). J Appl Physiol 118(12):1379-88; Skiba & Clarke (2021). IJSPP 16(11). |
| Power-Duration 3P (Pmax, tau) | Modello iperbolico esteso stile WKO5/INSCYD | Letteratura CP 3-parametri (Morton 1996). |
| DFA α1 (soglia aerobica) | DFA su RR series, finestre Rogers | Peng et al. (1995). Chaos 5:82 (metodo DFA); Rogers et al. (2021). PMID 33519504. |
| CTL / ATL / TSB | Fitness-fatigue impulse model | Banister (1991). Modeling elite athletic performance. |
| TSS | Training Stress Score | Coggan & Allen (2019). |
| ACWR (spike → rischio infortuni) | Acute:Chronic Workload Ratio | Gabbett (2016). Br J Sports Med. |
| Monotony & Strain | Foster monotony/strain | Foster (1998). Med Sci Sports Exerc 30(7). |
| Polarization Index | Treff PI (multiplicativo) | Treff et al. (2019). J Sports Sci. |
| Taper | Step taper, decay | Mujika & Padilla (2003). Sports Med 33(13). |
| Cardiovascular drift | HR drift per endurance assessment | Coyle & Gonzalez-Alonso (2001). PMID 11337829. |
| VO2max intervals (4×4) | Norwegian protocol | Helgerud et al. (2007). MSSE 39(4). PMID 17414804. |
| 30/15 intervals | Intermittent HIIT | Rønnestad & Hansen (2013). JSCR 28(9):2594-603. |
| Distribuzione intensità | Polarized/pyramidal/threshold bands | Seiler & Kjerland (2006); Seiler (2010). |
| **Calibrazione livello atleta** ⭐ | Polarized advantage = élite-only | Rivera-Köfler et al. (2025). JSCR 39(3) scoping review; Rosenblat et al. (2019). JSCR 33(12) meta-analysis. |
| **Durability** ⭐ | Delta CP fresh→fatigued; sessioni firma | Muriel et al. (2022). EJSS 22(12); Spragg, Leo & Swart (2023). MSSE. |
| Readiness composita | Bayesian HRV+sleep+load | Sintesi interna su modelli Whoop/Oura/Garmin readiness. |
| HRV baseline/trend | Rolling mean ± SD, CV | Buchheit (2014); review HRV wearables 2025; Plews et al. (parasympathetic saturation). |
| **Alert instabilità HRV (CV)** ⭐ | Coefficient of variation 7d vs 28d bidirezionale | Review Physiological Reports 2025; Scientific Reports 2025 (cyclists, HRV-guided). |
| Fueling CHO/h per durata | Tabella 0-120 g/h multi-trasportatore | Jeukendrup (2014). Sports Med; *From Metabolism to Medals*, J Nutrition (2026). |
| **Gut training** ⭐ | Progressione +10-15 g/h / 2 sett | Costa et al. (2017). APNM; linee guida CHO 2026. |
| **Recupero 3:1** ⭐ | CHO:PROT entro 45 min | Consenso sports nutrition (ISSN 2018 update). |
| Carb periodization | Train-low / sleep-low | GSSI SSE 231; meta-analisi PMC8127206 (effetto performance nullo, adattamenti parziali). |
| Race-day fueling + caffeina | Linee guida gara | Jeukendrup & UCI Sports Nutrition Project (2026). |
| **Heat acclimation** ⭐ | Protocollo 10 giorni | Périard et al. (2015). SJMSS; meta-analisi Springer s40279-021-01445-6; BMC SSMSR (2024) passive heat. |
| Forza concorrente | 2×/sett 4×6 @85% 1RM; separazione ≥6h | Llanos-Lagos et al. (2025). EJAP; Vikmoen et al. (2021); Wilson 2012 / Sabag 2018 meta. |
| Mobilità quotidiana | ROM training e rischio infortuni | Warneke et al. (2025). |
| Integratori (tier A/B/C) | Caffeina, beta-alanina, nitrati, bicarbonato, creatina, glicerolo | Consenso ISSN/sports-nutrition. |
| HR ergometer control | Controllo HR per ergometro | Hunt & Fankhauser (2019). PMID 31471785. |

⭐ = implementato/aggiornato in v1.4.0 sulla base di `docs/SCIENCE_UPDATES_2025.md`.

---

## 🛠️ Software di terze parti

### Backend Python
| Pacchetto | Licenza | Uso |
|-----------|---------|-----|
| [FastAPI](https://github.com/tiangolo/fastapi) / Starlette | BSD-3 | Web framework + routing |
| [uvicorn](https://www.uvicorn.org) | BSD-3 | ASGI server |
| [httpx](https://www.python-httpx.org) | BSD-3 | Client HTTP (ICU, LLM providers) |
| [Jinja2](https://palletsprojects.com/p/jinja) | BSD-3 | Templating dashboard |
| [pydantic](https://docs.pydantic.dev) | MIT | Validazione modelli |
| [websockets](https://websockets.readthedocs.io) | BSD-3 | WebSocket runtime |
| [scipy](https://scipy.org) | BSD-3 | Fitting CP/W', ottimizzazione |
| [numpy](https://numpy.org) | BSD-3 | Calcolo numerico |
| [fit-tool](https://pypi.org/project/fit-tool/) | MIT | Emissione file .FIT |
| [fitparse](https://github.com/polyvertex/fitparse) | MIT | Parsing .FIT attività |
| [bleak](https://github.com/hbldh/bleak) | MIT | BLE trainer control |
| [pycycling](https://github.com/zacharyedwardbull/pycycling) | MIT | FTMS trainer protocol |
| [openant](https://github.com/Tigge/openant) | MIT | ANT+ trainer |
| [garminconnect](https://github.com/cyberjunky/python-garminconnect) | MIT | Import Garmin wellness |
| [certifi](https://github.com/certifi/python-certifi) | MPL-2.0 | CA bundle TLS |
| [PyMuPDF](https://pymupdf.readthedocs.io) | AGPL-3.0 | PDF export/BIA OCR (uso server-side) |
| [pytesseract](https://github.com/madmaze/pytesseract) | Apache-2.0 | OCR BIA/diet |
| [lxml](https://lxml.de) | BSD-3 | Parsing XML/GPX |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | BSD-3 | Config env |
| [Pillow](https://python-pillow.org) | HPND/MIT-CMU | Immagini icone |
| [python-dateutil](https://dateutil.readthedocs.io) | Apache-2.0 | Date parsing |
| [packaging](https://github.com/pypa/packaging) | Apache-2.0/BSD | Versioni |
| [pystray](https://github.com/moses-palmer/pystray) | LGPL-3.0 | Tray icon (bytecode COLLECT = requisito user-replaceability soddisfatto) |
| [pythonnet](https://github.com/pythonnet/pythonnet) | MIT | Bridge .NET per WebView2 Win |
| [cefpython3](https://github.com/cztomczak/cefpython) | BSD-3 | Backend webview alternativo |
| [playwright](https://playwright.dev) (solo dev/test) | Apache-2.0 | UI automation testing |
| [pytest](https://pytest.org) + pytest-timeout (solo dev) | MIT | Test suite |

### Frontend / desktop
| Pacchetto | Licenza | Uso |
|-----------|---------|-----|
| [Chart.js](https://www.chartjs.org) | MIT | Tutti i grafici (`static/vendor/chart.umd.min.js`) |
| [html2canvas](https://html2canvas.hertzen.com) — Niklas von Hertzen | MIT | Screenshot ride report |
| [pywebview](https://pywebview.flowrl.com) | BSD-3 | Finestra desktop nativa |
| [PyInstaller](https://pyinstaller.org) | GPL-2.0 + bootloader exception | Packaging eseguibili (l'eccezione consente distribuzione con licenza propria) |

---

## 🗃️ Attribuzione dati

| Dato | Fonte | Licenza |
|------|-------|---------|
| Nutrition database (284 prodotti) | [Open Food Facts](https://world.openfoodfacts.org/) | ODbL 1.0 — derivate devono condividere sotto ODbL |
| Brand nutrition (Maurten, SiS, GU…) | Marchi dei rispettivi proprietari | uso nominativo |
| Route virtuali | Generazione procedurale (Perlin-style noise, seed deterministico) | Apache-2.0 |
| Route reali (Alpi, Pirenei, Dolomiti…) | Nomi geografici pubblici; profili da DEM reali; dove applicabile OpenStreetMap contributors | ODbL 1.0 |
| Workout library (4.306 .zwo) | Strutture interval da fisiologia pubblica (Helgerud 2007, Rønnestad 30/15, Billat 30/30, zone Seiler, profili Coggan); nomi/descrizioni originali generate | Apache-2.0 |
| Durability workouts (v1.4.0) | Protocolli da Muriel 2022 / Spragg 2023, implementazione originale | Apache-2.0 |

---

## 🏷️ Marchi

Tacx, Wahoo, Garmin, Polar, MyWhoosh, Zwift, Golden Cheetah, Rouvy, TrainerRoad,
Intervals.icu, Google Vision, Huawei Health e Terra sono marchi dei rispettivi
proprietari, usati per sola identificazione (vedi anche `TRADEMARKS.md`).

---

## 🔬 Ricerche di riferimento nel progetto

Sintesi complete in `docs/`:

- `SCIENCE_UPDATES_2025.md` — evidenze 2024-2026 implementate (fueling revolution,
  durability, HRV-CV, TID élite-only, heat training) con bibliografia essenziale
- `SCIENCE.md` — logica e formule del progetto con citazioni
- `SCIENCE_REVIEW.md` — rassegna delle evidenze scientifiche
- `RESEARCH_TRAINING_PLANNER.md` — sintesi di ricerca del pianificatore
- `workout_analysis.md` (in PCC upstream) — ranking evidence-based della libreria

---

## 🙏 Grazie

Un ringraziamento speciale alla community di Domestique, ai contributor di OpenStreetMap
e Open Food Facts, e ai ricercatori le cui pubblicazioni rendono possibili strumenti
come questo. *This project stands on the shoulders of giants.*

---

*Ultimo aggiornamento: v1.4.0 (21 agosto 2026). Questo file deve essere mantenuto in
tutte le ridistribuzioni del progetto.*
