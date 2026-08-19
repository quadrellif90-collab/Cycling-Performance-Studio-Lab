# Cycling Performance Studio Lab

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/tests-150%20passing-brightgreen.svg)]()

Professional cycling analytics platform combining the best of **Domestique** and **PCC** into a single, unified application.

> **Fork di [Domestique](https://github.com/platypus45/domestique)** con tutte le funzionalita avanzate di PCC integrate. Licenza Apache 2.0.

---

## Features (v0.5.0)

### Analisi della Performance

| Funzionalita | Descrizione |
|-------------|-------------|
| **FTP Estimation** | Stima FTP dai best efforts usando scaling factors Coggan |
| **Fitness Signature** | Calcolo completo: FTP, LTP, HIE, Pmax |
| **CP/W' Analysis** | Modello Monod-Scherrer per Critical Power e W' |
| **CP Models** | Modelli Morton 3P, 2P, Marinescu per performance |
| **Power Curve** | Curva potenza-duration con dati da Intervals.icu |
| **Aerobic Decoupling** | Analisi decoupling aerobico per valutare resistenza |
| **Readiness Score** | Score composito HRV + sonno + carico training |
| **Strain Score** | Calcolo strain e debolezza (XSS) per sessioni |
| **Tau Fitting** | Fitting parametri debolezza per atleta |
| **Continuous Policy** | Goal engine continuo con deload trigger |

### Training & Pianificazione

| Funzionalita | Descrizione |
|-------------|-------------|
| **Training Planner** | Generazione piani settimanali con TSS target |
| **Daily Recalculate** | Ricalcolo giornaliero con adjustment automatico |
| **Block Model** | Raccomandazioni per blocchi di allenamento |
| **Strength & Mobility** | Piani forza e mobilita per fase di allenamento |
| **Mobility Plan** | Routine giornaliere stretching/mobilita |
| **Calendar ICS** | Esporta piani in formato iCalendar |
| **Plan Export** | Esporta piani in HTML |

### Nutrizione & Composizione Corporea

| Funzionalita | Descrizione |
|-------------|-------------|
| **Nutrition** | Calcolo macro giornalieri per tipo di allenamento |
| **Diet** | Piani alimentari settimanali con hydratation e fueling |
| **Supplements** | Raccomandazioni integratori per peso/categoria |
| **BIA Parser** | Analisi composizione corporea da PDF (OCR o Vision API) |
| **BIA Vision** | Estrazione BIA da immagini via Google Vision API |
| **Diet Parser** | Parsing piani alimentari da PDF |

### Analisi Avanzata

| Funzionalita | Descrizione |
|-------------|-------------|
| **HRV Engine** | Analisi HRV con baseline e trend |
| **Huawei HRV** | Import dati HRV da Huawei Watch |
| **Pedal Asymmetry** | Analisi asimmetria pedale (L/R balance, TE, PS) |
| **Activity Insights** | Classificazione protocollo e insights sessione |
| **Metabolic Profile** | Profilo metabolico con decodificatore |
| **Custom Charts** | Grafici personalizzati con metriche libere |
| **Field Test Protocols** | Protocolli test campo (CP test, ramp test, etc.) |

### Integrazione & Sync

| Funzionalita | Descrizione |
|-------------|-------------|
| **Intervals.icu** | Sync bidirezionale con OAuth2 |
| **Terra** | Integrazione con Terra API per wearables |
| **Huawei** | Import dati da dispositivi Huawei |
| **Upstream Check** | Verifica aggiornamenti disponibili |
| **Data Export** | Bundle ZIP con tutti i dati profilo |
| **Activity RPE** | Log RPE per sessioni |

### Architettura

| Funzionalita | Descrizione |
|-------------|-------------|
| **68 Moduli** | Codice modulare e testabile |
| **224 API Routes** | API REST complete con OpenAPI docs |
| **Multi-Profile** | Profili multipli con credenziali separate |
| **Pluggable Sync** | Architettura modulare per sync multi-target |
| **LRU Cache** | Cache con TTL per computazioni costose |
| **Session Manager** | Gestione sessioni con audit log |
| **Error Registry** | Codici di errore strutturati |
| **Injury Manager** | CRUD infortuni con persistenza JSON |

### Frontend (13 Tab)

| Tab | Descrizione |
|-----|-------------|
| **Home** | Overview con TID heatmap, daily adapt, strength, calendar |
| **Activity Picker** | Selezione attivita per analisi |
| **Library** | Libreria workout con filtri |
| **Courses** | Gestione percorsi |
| **Plan** | Piani di allenamento |
| **Analysis** | Analisi dettagliata sessione |
| **DFA** | Analisi DFA alpha per intensita |
| **HRV** | Dashboard HRV completa |
| **Nutrition** | Piani nutrizionali |
| **BIA** | Composizione corporea |
| **Profile** | Dati atleta e configurazione |
| **What's New** | Changelog e novita |
| **Settings** | Configurazione sync, credenziali |

---

## Quick Start

### Requisiti

- Python 3.11 o superiore
- pip

### Installazione

```bash
# Clona il repository
git clone https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab.git
cd Cycling-Performance-Studio-Lab

# Installa dipendenze
pip install -r requirements-common.txt

# Avvia server di sviluppo
python app.py

# Oppure avvia come app desktop (pywebview)
python app.py desktop
```

L'app sara disponibile su `http://127.0.0.1:22400`

### Build Eseguibili

```bash
# Windows
build_win.bat

# macOS
./build_dmg.sh

# Linux (in docker ubuntu:22.04)
docker run --rm -v "$PWD":/src -w /src ubuntu:22.04 bash build_linux.sh
```

---

## Struttura del Progetto

```
Cycling Performance Studio Lab/
├── app.py                      # Entry point FastAPI (224 routes)
├── launcher.py                 # Desktop entry point (pywebview)
├── pcc_routes_v2.py            # PCC API routes modulare
├── config.py                   # Configurazione globale
├── profile_manager.py          # Singleton gestione profili
├── training_planner.py         # Generazione piani + block model
├── zones.py                    # Calcolo zone HR e potenza
├── fitness_estimation.py       # Stima FTP, firma fitness
├── power_curve.py              # Analisi curva potenza
├── cp_models.py                # Modelli CP (Morton 3P/2P)
├── hrv_engine.py               # Analisi HRV
├── nutrition.py                # Macro e integrazione
├── diet.py                     # Piani alimentari
├── bia_parser.py               # Analisi BIA da PDF
├── pedal_asymmetry.py          # Asimmetria pedale
├── activity_insights.py        # Insights sessione
├── custom_charts.py            # Grafici personalizzati
├── injury_manager.py           # CRUD infortuni
├── session_manager.py          # Gestione sessioni
├── data_export.py              # Backup e export
├── user_home.py                # Directory utente (~/.cpsl)
├── assets/                     # Icone app (.ico/.icns/.png)
│   ├── icon.ico
│   ├── icon.icns
│   └── linux/                  # Icone Linux (hicolor)
├── frontend/
│   ├── templates/
│   │   └── dashboard.html      # SPA dashboard (13 tab)
│   └── static/
├── tests/                      # 150 test (6 file)
│   ├── conftest.py             # Fixtures hermetic
│   ├── test_core_modules.py    # 27 test moduli core
│   ├── test_training_analysis.py # 29 test training/analysis
│   ├── test_nutrition_bia.py   # 17 test nutrizione/BIA
│   ├── test_utilities.py       # 31 test utilita
│   ├── test_api_routes.py      # 22 test API routes
│   └── test_pcc_modules.py     # 24 test moduli PCC
├── CyclingPerformanceStudioLab.spec  # PyInstaller spec
├── build_dmg.sh                # macOS DMG builder
├── build_linux.sh              # Linux AppImage builder
├── requirements-common.txt     # Dipendenze comuni
├── pytest.ini                  # Configurazione pytest
├── API_ENDPOINTS.md            # Documentazione API
├── VERSION                     # 3.10.0
└── LICENSE                     # Apache License 2.0
```

---

## Testing

```bash
# Esegui tutti i test (150 test, 6 file)
pytest tests/ -v

# Solo test moduli core
pytest tests/test_core_modules.py -v

# Solo test API
pytest tests/test_api_routes.py -v

# Con copertura
pytest tests/ --cov=. --cov-report=html
```

---

## API

Vedi [API_ENDPOINTS.md](API_ENDPOINTS.md) per la documentazione completa (224 endpoints).

### Esempio

```bash
# Stima FTP
curl -X POST http://127.0.0.1:22400/api/fitness/estimate-ftp \
  -H "Content-Type: application/json" \
  -d '{"efforts": {"300": 280, "600": 250, "1200": 220}}'

# Nutrition macros
curl http://127.0.0.1:22400/api/nutrition-full

# HRV summary
curl http://127.0.0.1:22400/api/hrv/summary
```

---

## Licenza

Questo progetto e distribuito sotto licenza **Apache License 2.0**.

Vedi il file [LICENSE](LICENSE) per i dettagli completi.

### Attribuzioni

- **Domestique** - [github.com/platypus45/domestique](https://github.com/platypus45/domestique) - Apache 2.0
- **PCC** - Moduli matematici condivisi - Apache 2.0
- **FastAPI** - [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) - MIT
- **Chart.js** - [chartjs.org](https://www.chartjs.org/) - MIT
- **PyWebview** - [pywebview.flowrl.com](https://pywebview.flowrl.com/) - BSD

---

**Fatto con per la community del ciclismo**
