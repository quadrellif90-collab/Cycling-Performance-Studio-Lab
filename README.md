# Cycling Performance Studio Lab

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

Professional cycling analytics platform combining the best of **Domestique** and **PCC** into a single, unified application.

> **Fork di [Domestique](https://github.com/platypus45/domestique)** con tutte le funzionalita avanzate di PCC integrate. Licenza Apache 2.0.

---

## Cos'e

Cycling Performance Studio Lab (CPSL) e un'applicazione desktop/web per ciclisti professionisti e amatoriali che offre:

- **Analisi della performance** con modelli matematici avanzati (FTP, CP/W', HIE, Pmax)
- **Sincronizzazione** con Intervals.icu e altri servizi
- **Gestione profili** multipli con credenziali separate
- **Tracking infortuni** con protocolli return-to-ride
- **Analisi composizione corporea** (BIA) da PDF
- **Import/Export** dati in formati standard (GPX, FIT, ICS)

### Origine del Progetto

Questo progetto nasce come **fork di [Domestique](https://github.com/platypus45/domestique)** (v3.10.0), un'applicazione open source per il monitoraggio dell'allenamento ciclistico. A Domestique sono state integrate tutte le funzionalita avanzate di **PCC** (Personal Cycling Coach), un'altra applicazione open source che condivide gli stessi moduli matematici di base.

**Moduli matematici condivisi** tra Domestique e PCC:
- `fitness_estimation.py` - Stima FTP e firma di fitness
- `power_curve.py` - Curva di potenza e analisi potenza-duration
- `training_live.py` - Metriche di training in tempo reale
- `error_codes.py` - Codici di errore strutturati (50 codici)

---

## Features

### Analisi della Performance

| Funzionalita | Descrizione |
|-------------|-------------|
| **FTP Estimation** | Stima FTP dai best efforts usando scaling factors Coggan |
| **Fitness Signature** | Calcolo completo: FTP, LTP, HIE, Pmax |
| **CP/W' Analysis** | Modello Monod-Scherrer per Critical Power e W' |
| **Power Curve** | Curva potenza-duration con dati da Intervals.icu |
| **Aerobic Decoupling** | Analisi decoupling aerobico per valutare resistenza |
| **Ramp Test FTP** | Advisory e capping per test a rampa |
| **Readiness Score** | Score composito HRV + sonno + carico training |

### Gestione Dati

| Funzionalita | Descrizione |
|-------------|-------------|
| **Multi-Profile** | Profili multipli con credenziali separate (.env) |
| **Sync Intervals.icu** | Push/pull attivita e wellness con OAuth2 |
| **GPX Import** | Parsing file GPX con dati potenza/FC/FCR |
| **FIT Import** | Import file FIT da dispositivi Garmin/Wahoo |
| **ICS Export** | Esporta piani di allenamento in formato iCalendar |
| **Data Export** | Backup completo profilo (ZIP, JSON) |

### Strumenti

| Funzionalita | Descrizione |
|-------------|-------------|
| **Injury Manager** | CRUD infortuni con persistenza JSON e severity tracking |
| **BIA Analysis** | Analisi composizione corporea da PDF (Vision API o parser locale) |
| **Sleep/HRV** | Analisi qualita sonno e basi HRV |
| **Capacity Cap** | Capping FTP e advisory per atleti |
| **Zones** | Calcolo zone HR e potenza (modello Coggan) |

### Architettura

| Funzionalita | Descrizione |
|-------------|-------------|
| **Pluggable Sync** | Architettura modulare per sincronizzazione multi-target |
| **Per-Profile Config** | Configurazione separata per ogni profilo |
| **LRU Cache** | Cache con TTL per computazioni costose |
| **Session Manager** | Gestione sessioni multi-utente con audit log |
| **Error Registry** | 50 codici di errore strutturati E_<domain>_<failure> |
| **CORS + Middleware** | Exception handler globale, CORS abilitato |

### Frontend

| Pagina | Descrizione |
|--------|-------------|
| **Dashboard** | Overview profilo attivo e metriche principali |
| **Profilo** | Gestione dati atleta e credenziali |
| **Workout Library** | Libreria workout con filtri e statistiche |
| **Analytics** | Grafici Chart.js: Power Curve, Fitness Signature, CP/W' |
| **Impostazioni** | Configurazione sync, credenziali, formati |

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
./build_mac.sh

# Linux
./build_linux.sh
```

---

## Struttura del Progetto

```
Cycling Performance Studio Lab/
├── app.py                  # Entry point FastAPI + pywebview
├── config.py               # Configurazione globale + proxy per profilo
├── profile_manager.py      # Singleton gestione profili
├── error_codes.py          # 50 codici di errore strutturati
├── sync_targets.py         # Architettura sync modulare
├── injury_manager.py       # CRUD infortuni + persistenza JSON
├── bia_parser.py           # Analisi BIA da PDF
├── gpx_parser.py           # Parsing file GPX
├── caching.py              # Cache LRU con TTL
├── fitness_estimation.py   # Stima FTP, firma fitness
├── power_curve.py          # Analisi curva potenza
├── training_live.py        # Metriche training tempo reale
├── user_home.py            # Utilita directory utente
├── zones.py                # Calcolo zone HR e potenza
├── db.py                   # Sync gate e write atomici
├── ride_storage.py         # Storage dati ride ICU
├── capacity_cap.py         # Capping FTP e advisory
├── data_export.py          # Backup e export dati
├── session_manager.py      # Gestione sessioni multi-utente
├── frontend/
│   ├── templates/          # 6 pagine HTML (Jinja2)
│   │   ├── base.html       # Template base con Chart.js
│   │   ├── index.html      # Dashboard
│   │   ├── profile.html    # Gestione profilo
│   │   ├── workouts.html   # Libreria workout
│   │   ├── analytics.html  # Grafici analytics
│   │   └── settings.html   # Impostazioni
│   └── static/
│       ├── css/main.css    # Stili responsive
│       └── js/
│           ├── app.js      # SPA router + gestione profili
│           └── analytics.js # Integrazione Chart.js
├── locales/
│   ├── en.json             # Traduzioni inglesi
│   └── it.json             # Traduzioni italiane
├── tests/
│   ├── test_basic.py       # Test core functionality
│   ├── test_injury.py      # Test injury manager
│   └── __init__.py
├── requirements-common.txt # Dipendenze comuni
├── requirements-win.txt    # Dipendenze Windows
├── requirements-mac.txt    # Dipendenze macOS
├── requirements-linux.txt  # Dipendenze Linux
├── pyproject.toml          # Configurazione ruff/black
├── pytest.ini              # Configurazione pytest
├── API_ENDPOINTS.md        # Documentazione API completa
├── README.md               # Questo file
└── LICENSE                 # Apache License 2.0
```

---

## API

Vedi [API_ENDPOINTS.md](API_ENDPOINTS.md) per la documentazione completa.

### Endpoints Principali

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/api/fitness/estimate-ftp` | Stima FTP dai best efforts |
| POST | `/api/fitness/signature` | Calcola firma fitness completa |
| POST | `/api/fitness/cp-wprime` | Analisi CP/W' Monod-Scherrer |
| GET | `/api/injuries` | Lista infortuni + sommario |
| POST | `/api/injuries` | Crea infortunio |
| POST | `/api/gpx/import` | Upload e parsing file GPX |
| GET | `/api/export/backup` | Backup completo profilo |
| GET | `/api/diag/health` | Health check |

### EsempioRichiesta

```json
POST /api/fitness/estimate-ftp
{
  "efforts": {
    "300": 280,
    "600": 250,
    "1200": 220,
    "3600": 210
  }
}

Response:
{
  "ftp": 209,
  "success": true
}
```

---

## Configurazione

### Profili

Ogni profilo ha la sua configurazione in `~/.cpsl/profiles/<id>/`:

```
~/.cpsl/profiles/
├── marco/
│   ├── athlete.json        # Dati atleta (FTP, peso, LTHR, etc.)
│   ├── user_prefs.json     # Preferenze utente
│   ├── .env                # Credenziali ICU, BIA Vision
│   ├── injuries.json       # Dati infortuni
│   ├── rides/              # Cache ride ICU
│   └── plans/              # Piani allenamento
└── laura/
    └── ...
```

### Credenziali (.env)

```env
ICU_ATHLETE_ID=your_athlete_id
ICU_API_KEY=your_api_key
ICU_ACCESS_TOKEN=your_access_token
BIA_VISION_API_KEY=your_bia_key
```

---

## Testing

```bash
# Esegui tutti i test
pytest tests/ -v

# Test moduli matematici
python test_math_modules.py
```

---

## Licenza

Questo progetto e distribuito sotto licenza **Apache License 2.0**.

Vedi il file [LICENSE](LICENSE) per i dettagli completi.

### Attribuzioni

- **Domestique** - [github.com/platypus45/domestique](https://github.com/platypus45/domestique) - Licenza: Apache 2.0
- **PCC** - Moduli matematici condivisi (fitness_estimation, power_curve, training_live)
- **FastAPI** - [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) - Licenza: MIT
- **Chart.js** - [chartjs.org](https://www.chartjs.org/) - Licenza: MIT
- **PyWebview** - [pywebview.flowrl.com](https://pywebview.flowrl.com/) - Licenza: BSD

---

## Contribuire

Contributi benvenuti! Per favore:

1. Fork il progetto
2. Crea una branch per la tua feature (`git checkout -b feature/nuova-feature`)
3. Commit le tue modifiche (`git commit -m 'Aggiungi nuova feature'`)
4. Push sulla branch (`git push origin feature/nuova-feature`)
5. Apri un Pull Request

---

## Supporto

- **Issue**: [GitHub Issues](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/issues)
- **Docs**: [API_ENDPOINTS.md](API_ENDPOINTS.md)

---

**Fatto con ❤️ per la community del ciclismo**
