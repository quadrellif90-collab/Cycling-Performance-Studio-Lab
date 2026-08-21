# Cycling Performance Studio Lab (CPSL)

<p align="center">
  <img src="frontend/static/icon.png" width="96" alt="CPSL" />
</p>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.4.0-green.svg)](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/releases/latest)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-009688.svg)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/tests-246%20passing-brightgreen.svg)]()

**Cycling Performance Studio Lab** è una piattaforma professionale di analisi e allenamento per ciclismo, self-hosted, che unisce il meglio di **Domestique** e **PCC** in un'unica applicazione desktop — senza cloud obbligatorio, senza abbonamenti, senza setup di server. I tuoi dati restano su `~/.cpsl`.

> Fork di [Domestique](https://github.com/platypus45/domestique) con la suite analitica completa di PCC integrata. Licenza **Apache 2.0**.

---

## ✨ In breve

| | |
|---|---|
| 🤖 **AI Coach integrato nel pianificatore** | Parere LLM groundato sui tuoi dati reali (RAG + memoria) con azioni applicabili al piano in un click — 14 provider LLM |
| 📋 **"Il tuo giorno"** | Digest giornaliero: readiness, workout del giorno, trend HRV, instabilità HRV (CV), monotonia, weekly review, countdown gara + protocollo heat |
| 🧠 **Pianificatore adattivo scientifico** | Auto-aggiornamento giornaliero da ride/HRV/sonno/TSB; calibrazione metodo per livello atleta (Rivera-Köfler 2025); cronologia versioni con restore |
| 🔬 **Analytics di livello WorldTour** | CP/W' Morton 3P, W'bal Skiba, phenotype radar, durability, DFA α1, breakthrough detection |
| ⚡ **Sync Intervals.icu bidirezionale** | OAuth2, push calendario 14 giorni con esito visibile, sync attività/wellness |
| 🍎 **Nutrizione evidence-based** | Fueling planner "fueling revolution" (fino a 120 g/h), gut training progressivo, recupero 3:1 |

---

## 🚀 Novità v1.4.0

| Funzione | Descrizione |
|----------|-------------|
| **Fueling Planner** (`fueling.py`) | Piano CHO/h per sessione basato sulla "fueling revolution" 2024-2026 (tabella per durata, miscele multi-trasportatore), tracker gut-training progressivo (+10-15 g/h ogni 2 sett), recupero 3:1. Endpoint `/api/fueling/session` |
| **4 Workout Durability** | Sessioni firma evidence-based: negative split, late hill reps @FTP, pre-fatigued intervals, muscular endurance (Muriel 2022, Spragg 2023) |
| **Alert instabilità HRV (CV)** | Coefficiente di variazione 7g vs 28g come allarme precoce più sensibile della baseline; deviazioni bidirezionali (paradosso parasimpatico, Plews) |
| **Calibrazione livello atleta** | Adaptive planner accetta `athlete_level`: il vantaggio polarizzato è élite-only (Rivera-Köfler 2025 JSCR) → amatori default pyramidal equipollente |
| **Protocollo heat training** | Suggerimento acclimatazione 10 giorni nel countdown gara per eventi in clima caldo (VO2max +5-8%, TT +6-8%) |
| **Cronologia piano + Restore** | Le ultime 7 versioni del piano (.bak rotation) consultabili e ripristinabili in sicurezza dal tab Plan |
| **Export piano PDF** | Con fallback writer integrato dove PyMuPDF non carica |
| **GPX → Golden Cheetah** | Conversione .gpx → .crs via endpoint |
| **Documentazione scientifica** | `docs/SCIENCE_UPDATES_2025.md` — sintesi citata delle evidenze implementate |

[CHANGELOG completo →](CHANGELOG.md)

---

## ✨ Funzionalità complete

### Analisi della performance
FTP estimation (Coggan) · Fitness Signature (FTP/LTP/HIE/Pmax) · CP/W' Monod-Scherrer · Modelli Morton 3P/2P/Marinescu · Power-duration curve · W' balance (Skiba) · Aerobic decoupling · Phenotype radar (6 tipi, 5 assi) · Durability score · Breakthrough detection · DFA α1 · Readiness composita bayesiana · Strain/XSS · Tau fitting · Pedal asymmetry · Metabolic profile · Field test protocols

### Allenamento & pianificazione
Training planner (5 metodologie: polarized/pyramidal/threshold/HIIT/sweet spot) · Adattamento giornaliero automatico (ride→reconcile→adapt→reforecast→push) · AI Coach nel Plan tab con azioni applicabili · Cronologia versioni piano con restore · Block model · Strength & mobility per fase · Inject multidisciplina · Calendar ICS · Export HTML/PDF · Workout player ZWO/FIT con controllo trainer BLE · 4.300+ workout in libreria classificati

### Nutrizione & composizione corporea
Macro giornalieri per tipo sessione · Fueling planner con gut training · Diet settimanali · Supplementi · BIA parser PDF (OCR/Vision) · Diet parser

### Recupero & benessere
HRV engine (baseline, trend, CV alert) · Huawei Health import · Sonno · Readiness composita · Daily digest notifiche · Injury manager

### Integrazioni
Intervals.icu OAuth2 bidirezionale (attività, wellness, push calendario con esito) · Garmin import · Terra wearables · MCP server per Claude Desktop · Export bundle ZIP/metrics

### Architettura
108 moduli Python · 293 route API · Multi-profilo con credenziali separate · Cache LRU TTL · Error registry strutturato · Audit log · 6 temi UI (light/dark/sepia/high-contrast/ocean/forest)

---

## 📦 Installazione — Utente finale

**Nessun requisito**: scarica l'eseguibile dalla pagina [Releases](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/releases).

| Piattaforma | Asset |
|-------------|-------|
| Windows | `CyclingPerformanceStudioLab-v*.zip` → estrai ed esegui `CyclingPerformanceStudioLab.exe` |

Al primo avvio: server locale su `http://127.0.0.1:22400` + finestra desktop nativa (pywebview). I dati vivono in `~/.cpsl` e sopravvivono agli aggiornamenti.

### Configurazione consigliata
1. **Settings → Connections**: collega Intervals.icu (OAuth o API key)
2. **Settings → AI Coach**: scegli provider LLM + la TUA api key (Google/OpenAI/Anthropic/Groq/DeepSeek/Mistral/OpenRouter/xAI/Ollama)
3. **Plan → Generate Plan**: il piano si auto-aggiorna dopo ogni sync

---

## 🛠️ Sviluppatori

```bash
git clone https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab.git
cd Cycling-Performance-Studio-Lab
pip install -r requirements-common.txt

python app.py          # web server su :22400
python launcher.py     # app desktop (pywebview)

build_win.bat          # build Windows (PyInstaller)
```

### Testing
```bash
pytest tests/ -v                      # 246 test, 10 file
pytest tests/test_advanced_analytics.py -v
```

---

## 📖 Documentazione

| Doc | Contenuto |
|-----|-----------|
| [docs/SCIENCE_UPDATES_2025.md](docs/SCIENCE_UPDATES_2025.md) | Evidenze 2024-2026 implementate (fueling, durability, HRV-CV, TID, heat) — citate |
| [docs/SCIENCE.md](docs/SCIENCE.md) | La scienza dietro le formule del progetto |
| [docs/SCIENCE_REVIEW.md](docs/SCIENCE_REVIEW.md) | Rassegna delle evidenze scientifiche |
| [docs/SYSTEM.md](docs/SYSTEM.md) | Documentazione di sistema |
| [docs/DEBUGGING.md](docs/DEBUGGING.md) | Playbook osservabilità/debug backend |
| [docs/HUAWEI_HRV.md](docs/HUAWEI_HRV.md) | Motore HRV Huawei |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Riferimento API (293 route) |
| [CHANGELOG.md](CHANGELOG.md) | Storia completa delle versioni |

---

## 🏗️ Architettura (sintesi)

```
┌────────────────────────────────────────────────────┐
│ Frontend SPA (vanilla JS, 14 tab, 6 temi)          │
│   dashboard.html ── Chart.js ── pywebview bridge   │
└──────────────────┬─────────────────────────────────┘
                   │ HTTP :22400
┌──────────────────┴─────────────────────────────────┐
│ FastAPI (293 routes)                               │
│  ├─ Planner engine (adaptive, daily-adapt, drift)  │
│  ├─ AI Coach (multi-provider LLM + RAG + memoria)  │
│  ├─ Analytics (CP/W', phenotype, durability, DFA)  │
│  ├─ ICU sync/push · Garmin · Terra · MCP server    │
│  └─ Nutrition/fueling · BIA · HRV · notifications  │
├────────────────────────────────────────────────────┤
│ Persistenza: ~/.cpsl (JSON per profilo, plan .bak) │
└────────────────────────────────────────────────────┘
```

---

## ❓ FAQ

**I miei dati lasciano il mio computer?**
No. Tutto vive in `~/.cpsl`. Le uniche chiamate esterne sono verso intervals.icu (sync), il provider LLM che scegli tu (solo per le query AI Coach) e GitHub (controllo aggiornamenti).

**Serve un abbonamento?**
No. Apache 2.0, forever. Il costo opzionale è solo la tua API key LLM se usi l'AI Coach.

**Il piano si modifica da solo?**
Sì: dopo ogni ride sync e a ogni apertura del tab Plan viene riconciliato con gli actuals e riadattato (readiness, HRV, TSB). Ogni versione precedente resta recuperabile da 🕘 Cronologia.

**L'AI può rompere il mio piano?**
No: i suggerimenti AI passano dagli stessi endpoint sicuri del planner e ogni modifica produce una nuova snapshot .bak ripristinabile.

---

## 📜 Licenza

Distribuito sotto **Apache License 2.0** — vedi [LICENSE](LICENSE).

### Attribuzioni
- **Domestique** — [platypus45/domestique](https://github.com/platypus45/domestique) — Apache 2.0
- **PCC** — moduli matematici condivisi — Apache 2.0
- **Chart.js** — MIT · **PyWebview** — BSD · **FastAPI** — MIT · **PyMuPDF** — AGPL (server-side use)

---

**Costruito con ❤️ per la community del ciclismo.**
