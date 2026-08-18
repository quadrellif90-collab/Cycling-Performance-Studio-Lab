# Cycling Performance Studio Lab

Professional cycling analytics platform combining Domestique's architecture with PCC's advanced fitness analytics.

## Features

- **Profile Management**: Multi-profile with per-profile credentials and athlete data
- **Fitness Analytics**: FTP estimation, fitness signature (FTP/LTP/HIE/Pmax), CP/W' modeling
- **Power Curve**: Aggregate power curve analysis
- **Sync**: Intervals.icu integration with OAuth2 support
- **Injury Tracking**: Return-to-ride protocols with severity tracking
- **BIA Analysis**: Body composition via Vision API or local PDF parser
- **GPX Import**: Parse cycling route files with power/HR data
- **Performance Caching**: LRU cache with TTL for expensive computations

## Quick Start

### Development

```bash
# Install dependencies
pip install -r requirements-common.txt

# Run development server
python app.py

# Run desktop app (pywebview)
python app.py desktop
```

### Build Executables

```bash
# Windows
build_win.bat

# macOS
./build_mac.sh

# Linux
./build_linux.sh
```

## Architecture

```
Cycling Performance Studio Lab/
├── app.py                  # FastAPI entry point
├── config.py               # Global config + per-profile proxy
├── profile_manager.py      # Singleton profile management
├── error_codes.py          # 50 structured error codes
├── sync_targets.py         # Pluggable sync architecture
├── injury_manager.py       # Injury CRUD + persistence
├── bia_parser.py           # BIA PDF analysis
├── gpx_parser.py           # GPX file parsing
├── caching.py              # LRU cache with TTL
├── fitness_estimation.py   # FTP, fitness signature
├── power_curve.py          # Power curve analysis
├── training_live.py        # Live training metrics
├── user_home.py            # User home directory utils
├── frontend/
│   ├── templates/          # 6 HTML pages (Jinja2)
│   └── static/             # CSS + JS (Chart.js)
├── locales/                # en.json, it.json
├── tests/                  # pytest tests
└── build scripts           # Win/Mac/Linux
```

## API

See [API_ENDPOINTS.md](API_ENDPOINTS.md) for complete API reference.

Key endpoints:
- `POST /api/fitness/estimate-ftp` - Estimate FTP from best efforts
- `POST /api/fitness/signature` - Compute full fitness signature
- `POST /api/fitness/cp-wprime` - Monod-Scherrer CP/W' fit
- `GET/POST /api/injuries` - Injury management
- `POST /api/gpx/import` - GPX file upload and parsing

## Configuration

Per-profile `.env` files in `~/.cpsl/profiles/<id>/`:
```
ICU_ATHLETE_ID=your_id
ICU_API_KEY=your_key
ICU_ACCESS_TOKEN=your_token
BIA_VISION_API_KEY=your_key
```

## Testing

```bash
pytest tests/ -v
```

## License

Apache License 2.0
