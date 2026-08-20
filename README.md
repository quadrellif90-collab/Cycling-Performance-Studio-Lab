# Cycling Performance Studio Lab (CPSL)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-009688.svg)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/actions)
[![Tests](https://img.shields.io/badge/tests-245%20passing-brightgreen.svg)]()

**Cycling Performance Studio Lab** is a professional, self-hosted cycling analytics and training platform that unifies the best of **Domestique** and **PCC (Performance Cycling Calculator)** into a single, standalone desktop application — no cloud account, no subscription, no server setup required.

> **Fork of [Domestique](https://github.com/platypus45/domestique)** with the full advanced analytics suite of PCC integrated. Released under the **Apache 2.0** license.

---

## 🚀 What's New in v1.0.0

| Feature | Description |
|---------|-------------|
| **AI Coach — Full Integration** | 7 endpoints: `status`, `weekly-analysis`, `generate-plan`, `friel-assessment`, `friel-prompts`, `coach-query` (contextual), `health` (module check) |
| **BIA Vision Analysis** | Body-composition extraction from PDF images via Cloud Vision (`/api/bia-vision-analyze`) |
| **Self-Update Engine** | Cross-platform automatic update (Windows NSIS, macOS DMG, Linux AppImage) with upstream asset detection (`/api/self-update`) |
| **Automatic Bootstrapper** | On startup the app verifies and pip-installs critical dependencies if missing — **zero manual install for the end user** |
| **8 Proprietary Analytical Modules** | Power-Duration 3P, Phenotype radar, Breakthrough detection, Durability score, Training-phase detector, Formula alerts, AI Coach, Workout player |
| **145+ API Routes Parity** | Full coverage of Domestique + PCC endpoints (230 routes total) |
| **CI/CD Multi-Platform** | GitHub Actions builds & publishes Windows `.exe`, macOS `.dmg`/`.app`, Linux `.tar.gz`/`.AppImage` on every version tag |

---

## ✨ Features

### Performance Analysis
| Capability | Description |
|-----------|-------------|
| **FTP Estimation** | FTP from best efforts using Coggan scaling factors |
| **Fitness Signature** | Full signature: FTP, LTP, HIE, Pmax |
| **CP/W' Analysis** | Monod–Scherrer Critical Power and W′ |
| **CP Models** | Morton 3P / 2P / Marinescu models |
| **Power Curve** | Power–duration curve with Intervals.icu data |
| **Aerobic Decoupling** | Decoupling analysis for endurance assessment |
| **Readiness Score** | Composite HRV + sleep + training-load score |
| **Strain Score** | Session strain and weakness (XSS) |
| **Tau Fitting** | Athlete weakness-parameter fitting |
| **Continuous Policy** | Continuous goal engine with deload triggers |
| **Phenotype Radar** | Multi-axis rider phenotype visualization |
| **Breakthrough Detection** | Automatic performance breakthrou式 detection |
| **Durability Score** | Durability metric across sessions |

### Training & Planning
| Capability | Description |
|-----------|-------------|
| **Training Planner** | Weekly plan generation with TSS targets |
| **Daily Recalculate** | Daily recalculation with auto-adjustment |
| **Block Model** | Training-block recommendations |
| **Strength & Mobility** | Phase-aware strength & mobility plans |
| **Mobility Plan** | Daily stretching/mobility routines |
| **Calendar ICS** | Export plans to iCalendar |
| **Plan Export** | Export plans to HTML |
| **Workout Player** | In-app structured-workout player (ZWO/FIT) |

### Nutrition & Body Composition
| Capability | Description |
|-----------|-------------|
| **Nutrition** | Daily macros per training type |
| **Diet** | Weekly meal plans with hydration & fueling |
| **Supplements** | Supplement recommendations |
| **BIA Parser** | Body-composition from PDF (OCR or Vision API) |
| **BIA Vision** | BIA extraction from images via Google Vision API |
| **Diet Parser** | Parse meal plans from PDF |

### Advanced Analysis
| Capability | Description |
|-----------|-------------|
| **HRV Engine** | HRV analysis with baseline & trends |
| **Huawei HRV** | Import HRV from Huawei Watch |
| **Pedal Asymmetry** | L/R balance, TE, PS analysis |
| **Activity Insights** | Protocol classification & session insights |
| **Metabolic Profile** | Metabolic profile decoder |
| **Custom Charts** | Free-metric custom charts |
| **Field Test Protocols** | CP test, ramp test, etc. |

### Integration & Sync
| Capability | Description |
|-----------|-------------|
| **Intervals.icu** | Bidirectional OAuth2 sync |
| **Terra** | Terra API wearable integration |
| **Huawei** | Huawei device data import |
| **Upstream Check** | Check for available updates |
| **Data Export** | Full-profile ZIP bundle |
| **Activity RPE** | Session RPE logging |

### Architecture
| Capability | Description |
|-----------|-------------|
| **Modular Codebase** | 68+ Python modules, fully testable |
| **230 API Routes** | Complete REST API with OpenAPI docs |
| **Multi-Profile** | Multiple profiles with separate credentials |
| **Pluggable Sync** | Modular multi-target sync architecture |
| **LRU Cache** | TTL cache for expensive computations |
| **Session Manager** | Session management with audit log |
| **Error Registry** | Structured error codes |
| **Injury Manager** | Injury CRUD with JSON persistence |

### Frontend (13 Tabs)
Home · Activity Picker · Library · Courses · Plan · Analysis · DFA · HRV · Nutrition · BIA · Profile · What's New · Settings

---

## 📦 Installation — End User (Standalone)

**No Python or dependencies required.** Download the pre-built executable for your platform from the [Releases](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/releases) page:

| Platform | Asset | Notes |
|----------|-------|-------|
| **Windows** | `CyclingPerformanceStudioLab.exe` | Double-click to run; auto-installs missing deps |
| **macOS** | `Cycling-Performance-Studio-Lab.dmg` (or `.tar.gz`) | Drag `.app` to Applications |
| **Linux** | `CyclingPerformanceStudioLab-vX.Y.Z-linux-x86_64.tar.gz` | Extract & run the bundled binary |

On first launch the app starts a local web server and opens `http://127.0.0.1:22400` in your browser.

---

## 🛠️ Developer / Source Build

### Requirements
- Python 3.11+
- pip

### Run from source
```bash
git clone https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab.git
cd Cycling-Performance-Studio-Lab

pip install -r requirements-common.txt

# Run as web server
python app.py

# Or as a desktop window (pywebview)
python launcher.py
```

The app is available at `http://127.0.0.1:22400`.

### Build distributable executables
```bash
# Windows
build_win.bat

# macOS (.app + optional .dmg)
bash build_mac.sh

# Linux (tar.gz; optional AppImage if appimagetool present)
bash build_linux.sh
```

### CI/CD
Pushing a tag `v*.*.*` triggers the GitHub Actions pipeline, which:
1. Runs the test suite on Windows / macOS / Linux
2. Builds the standalone executable for each platform
3. Publishes all three assets to a GitHub Release

---

## 🧪 Testing
```bash
# All tests (245 test definitions across 10 files)
pytest tests/ -v

# Specific suites
pytest tests/test_api_routes.py -v
pytest tests/test_core_modules.py -v
pytest tests/test_workout_player.py -v
```

---

## 🤖 AI Coach API
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/status` | GET | LLM client status |
| `/api/ai/weekly-analysis` | POST | Weekly coaching analysis |
| `/api/ai/generate-plan` | POST | Generate training plan |
| `/api/ai/friel-assessment` | POST | Friel-based assessment |
| `/api/ai/friel-prompts` | GET | System & template prompts |
| `/api/ai/coach-query` | POST | Contextual coaching query |
| `/api/ai/health` | GET | Module health check |

---

## 📁 Project Structure
```
Cycling Performance Studio Lab/
├── app.py                          # FastAPI entry point (230 routes)
├── launcher.py                     # Desktop entry point (pywebview)
├── pcc_routes_v2.py                # PCC API routes (modular)
├── ai_coach/                       # AI Coach module (LLM client)
├── config.py                       # Global configuration
├── profile_manager.py             # Profile singleton
├── training_planner.py            # Plan generation + block model
├── phenotype.py / breakthrough_detector.py / durability_score.py
├── workout_player.py              # Structured-workout player
├── bia_parser.py / bia_vision.py  # Body-composition analysis
├── frontend/                      # SPA dashboard (13 tabs)
│   ├── templates/dashboard.html
│   └── static/
├── tests/                         # 245 tests (10 files)
├── CyclingPerformanceStudioLab.spec  # PyInstaller spec
├── build_win.bat / build_mac.sh / build_linux.sh
├── requirements-common.txt / requirements-{win,mac,linux}.txt
├── VERSION                        # 1.0.0
├── CHANGELOG.md
├── API_ENDPOINTS.md
└── LICENSE                        # Apache 2.0
```

---

## 📜 Changelog
See [CHANGELOG.md](CHANGELOG.md) for the full history (Keep a Changelog format).

---

## 📝 License
Distributed under the **Apache License 2.0**. See [LICENSE](LICENSE).

### Attributions
- **Domestique** — [github.com/platypus45/domestique](https://github.com/platypus45/domestique) — Apache 2.0
- **PCC** — Shared mathematical modules — Apache 2.0
- **FastAPI** — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) — MIT
- **Chart.js** — [chartjs.org](https://www.chartjs.org/) — MIT
- **PyWebview** — [pywebview.flowrl.com](https://pywebview.flowrl.com/) — BSD

---

**Built for the cycling community.**
