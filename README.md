# Cycling Performance Studio Lab (CPSL)

<p align="center">
  <img src="frontend/static/icon.png" width="96" alt="CPSL" />
</p>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.5.0-green.svg)](https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab/releases/latest)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-009688.svg)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/tests-304%20passing-brightgreen.svg)]()

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

## 🚀 Novità v1.5.0 — Port Montis (ESPE · W′bal · ISDM · ADE)

Quattro nuovi moduli analitici ad alto valore, portati dai concetti di [Montis.icu](https://www.montis.icu) (MIT) e ricalibrati sulle convenzioni CPSL — attribuzione completa nel file [`NOTICE`](NOTICE).

| Funzione | Descrizione |
|----------|-------------|
| **Progressione sistemi energetici (ESPE)** | Confronta la power curve a 84 giorni con i precedenti 84: delta per 1m/5m/20m/60m classificati per sistema (anaerobico, VO₂max, soglia, durabilità aerobica), bias glicolitico P1m/P20m (ideale ~1.8), detection plateau, profilo di curva su 6 fenotipi. Endpoint `/api/espe` + card nel tab Analysis |
| **Repeatabilità anaerobica W′bal** | Statistiche settimanali della depletazione W′bal per sessione: media/max %, sessioni moderate (>50%) e alte (>60%), divergenza dalla baseline endurance. Fonte sync Intervals.icu (`icu_w_prime`, `icu_max_wbal_depletion`), fallback stimato da kJ sopra FTP + W′ locale. Endpoint `/api/repeatability` |
| **Trend durabilità ISDM** | Classificazione settimanale del trend di resistenza dal decoupling aerobico firmato, con requisito di evidenza ripetuta (drifting / improving / stable). Endpoint `/api/durability-trend` |
| **Decisione del giorno (ADE)** | Governance giornaliera spiegabile: punteggio da 100 con penalità/supporti itemizzati (HRV, sonno, TSB, ramp rate, monotonia, taper, rischio) → directive chiara da *carico completo* a *riposo*, con confidenza proporzionale ai segnali disponibili. Il motore decide, l'AI spiega. Endpoint `/api/coach/decision` |

[CHANGELOG completo →](CHANGELOG.md)

---

## ✨ Funzionalità complete

### Analisi della performance
FTP estimation (Coggan) · Fitness Signature (FTP/LTP/HIE/Pmax) · CP/W' Monod-Scherrer · Modelli Morton 3P/2P/Marinescu · Power-duration curve · W' balance (Skiba) · Aerobic decoupling · Phenotype radar (6 tipi, 5 assi) · Durability score + trend ISDM · Breakthrough detection · ESPE progressione sistemi energetici · Repeatabilità anaerobica W′bal · DFA α1 · Readiness composita bayesiana · Strain/XSS · Tau fitting · Pedal asymmetry · Metabolic profile · Field test protocols

### Allenamento & pianificazione
Training planner (5 metodologie: polarized/pyramidal/threshold/HIIT/sweet spot) · Adattamento giornaliero automatico (ride→reconcile→adapt→reforecast→push) · AI Coach nel Plan tab con azioni applicabili · Cronologia versioni piano con restore · Block model · Strength & mobility per fase · Inject multidisciplina · Calendar ICS · Export HTML/PDF · Workout player ZWO/FIT con controllo trainer BLE · 4.300+ workout in libreria classificati

### Nutrizione & composizione corporea
Macro giornalieri per tipo sessione · Fueling planner con gut training · Diet settimanali · Supplementi · BIA parser PDF (OCR/Vision) · Diet parser

### Recupero & benessere
HRV engine (baseline, trend, CV alert) · Huawei Health import · Sonno · Readiness composita · Daily digest notifiche · Injury manager

### Integrazioni
Intervals.icu OAuth2 bidirezionale (attività, wellness, push calendario con esito) · Garmin import · Terra wearables · MCP server per Claude Desktop · Export bundle ZIP/metrics

### Architettura
110 moduli Python · 297 route API · Multi-profilo con credenziali separate · Cache LRU TTL · Error registry strutturato · Audit log · 6 temi UI (light/dark/sepia/high-contrast/ocean/forest)

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

Distribuito sotto **Apache License 2.0** — vedi [LICENSE](LICENSE), [NOTICE](NOTICE) e [TRADEMARKS.md](TRADEMARKS.md).

## 🙏 Acknowledgments

CPSL è costruito sulle spalle di giganti — il riconoscimento completo (contributori, calcolatori→fonti scientifiche, software, dati, ricerche) è in **[ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)**.

### Progetti d'origine
| Progetto | Contributo | Contributori |
|----------|-----------|--------------|
| **[Domestique](https://github.com/platypus45/domestique)** — Apache 2.0 | Codebase originale, build system, motore training science, 4.232 workout | [platypus45](https://github.com/platypus45) (649 commit), claude |
| **PCC** — Programming Cycling Coach | Moduli BIA/nutrizione/diet/HRV-Huawei/metabolic + route API | quadrellif90-collab |

### Fonti scientifiche principali
Coggan & Allen · Banister · Skiba (W'bal) · Seiler · Helgerud · Rønnestad · Mujika · Gabbett (ACWR) · Foster (monotony) · Treff (PI) · Rogers (DFA α1) · Jeukendrup (fueling) · Costa (gut training) · Muriel & Spragg (durability) · Rivera-Köfler 2025 (TID élite-only) · Llanos-Lagos 2025 (forza concorrente) · Warneke 2025 (mobilità) · Périard/Springer (heat)

→ Mappatura completa calcolatore→formula→fonte in [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md).

---

**Costruito con ❤️ per la community del ciclismo.**
