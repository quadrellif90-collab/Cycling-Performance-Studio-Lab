## Cycling Performance Studio Lab v0.1.0

Professional cycling analytics platform - fork of Domestique with PCC advanced features.

### Features
- 9 API endpoints (FTP, Fitness Signature, CP/W', Injuries, Sessions, Sync, Export)
- 5 HTML pages (Dashboard, Profile, Workouts, Analytics, Settings)
- Multi-profile management with per-profile credentials
- Intervals.icu sync with OAuth2
- Injury tracking with JSON persistence
- BIA analysis (Vision API + local PDF parser)
- GPX import with power/HR data
- LRU cache with TTL
- Session manager for multi-user
- Data export (backup, ZIP, metrics)
- Chart.js analytics (Power Curve, Fitness Signature, CP/W')
- Localization (EN/IT)
- CORS + global exception handler

### Tech Stack
Python 3.11+ / FastAPI / uvicorn / pywebview / Jinja2 / Chart.js / Vanilla JS

### License
Apache License 2.0

### Install
```
git clone https://github.com/quadrellif90-collab/Cycling-Performance-Studio-Lab.git
cd Cycling-Performance-Studio-Lab
pip install -r requirements-common.txt
python app.py
```

Open http://127.0.0.1:22400
