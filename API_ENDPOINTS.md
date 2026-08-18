# API Endpoints

Complete reference of all HTTP endpoints in Cycling Performance Studio Lab.

Base URL: `http://127.0.0.1:22400`

## Pages (HTML)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main dashboard |
| GET | `/profile` | Profile management |
| GET | `/workouts` | Workout library |
| GET | `/analytics` | Analytics charts |
| GET | `/settings` | Settings & sync |

## Profiles API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create profile |
| POST | `/api/profiles/{id}/switch` | Switch active profile |
| DELETE | `/api/profiles/{id}` | Delete profile |
| GET | `/api/profiles/{id}/athlete` | Get athlete data |
| POST | `/api/profiles/{id}/athlete` | Save athlete data |
| POST | `/api/profiles/{id}/env` | Save .env credentials |

### POST `/api/profiles`
Create a new athlete profile.
```json
Request: {"name": "Marco", "color": "blue"}
Response: {"profile_id": "marco"}
```

### POST `/api/profiles/{id}/switch`
Switch active profile (with sync gate).
```json
Response: {"success": true, "active": "marco"}
```

### POST `/api/profiles/{id}/athlete`
Save athlete metrics with validation.
```json
Request: {
  "ftp": 250,
  "weight_kg": 75,
  "lthr": 175,
  "max_hr": 195,
  "lbm_kg": 60,
  "age": 32,
  "sex": "M"
}
Response: {"success": true}
```

### POST `/api/profiles/{id}/env`
Save per-profile credentials (ICU, BIA Vision).
```json
Request: {
  "icu_athlete_id": "12345",
  "icu_api_key": "xxx",
  "icu_access_token": "xxx",
  "bia_vision_api_key": "xxx"
}
Response: {"success": true}
```

## Sync API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sync/targets` | List sync targets |
| POST | `/api/sync/icu/push` | Push to Intervals.icu |

## Fitness & Analytics API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/fitness/estimate-ftp` | Estimate FTP from efforts |
| POST | `/api/fitness/signature` | Compute fitness signature |
| POST | `/api/fitness/cp-wprime` | Compute CP/W' values |

### POST `/api/fitness/estimate-ftp`
```json
Request: {"efforts": {"300": 280, "600": 250, "1200": 230, "3600": 210}}
Response: {"ftp": 209, "success": true}
```

### POST `/api/fitness/signature`
```json
Request: {"efforts": {"300": 280, "600": 250}, "ftp": 210}
Response: {
  "ftp": 210, "ltp": 157, "hie": 21300, "peak_power": 418, "success": true
}
```

### POST `/api/fitness/cp-wprime`
```json
Request: {"efforts": {"180": 350, "300": 280, "600": 250, "1200": 230}}
Response: {"cp": 205.0, "w_prime": 23143, "success": true}
```

## Injuries API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/injuries` | List injuries + summary |
| POST | `/api/injuries` | Create injury |
| PUT | `/api/injuries/{id}` | Update injury |
| POST | `/api/injuries/{id}/resolve` | Resolve injury |
| DELETE | `/api/injuries/{id}` | Delete injury |

### POST `/api/injuries`
```json
Request: {
  "name": "Tendinite rotulea",
  "date_start": "2025-01-15",
  "severity": "medium",
  "notes": "Dolore dopo allenamento in salita"
}
Response: {"success": true, "injury_id": "inj_20250115_abc123"}
```

### GET `/api/injuries`
```json
Response: {
  "active_injuries": [...],
  "summary": {
    "active_count": 2,
    "total_count": 5,
    "by_severity": {"minor": 1, "medium": 3, "severe": 1},
    "recent_injuries": [...]
  }
}
```

## GPX Import API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/gpx/import` | Upload GPX file |
| POST | `/api/gpx/parse-file` | Parse GPX from path |

### POST `/api/gpx/import`
Multipart form upload of `.gpx` file.
```json
Response: {
  "success": true,
  "filename": "ride.gpx",
  "summary": {
    "total_tracks": 1,
    "total_distance_km": 45.2,
    "total_elevation_gain_m": 850
  },
  "routes": [...]
}
```

## Diagnostics API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/diag/recent-errors` | Recent error log |
| GET | `/api/diag/health` | Health check |

### GET `/api/diag/health`
```json
Response: {
  "status": "ok",
  "active_profile": "marco",
  "profiles_count": 3,
  "sync_targets": ["intervals_icu"]
}
```

## Error Codes

All errors use `E_<domain>_<failure>` format. Examples:

| Code | Domain | Description |
|------|--------|-------------|
| `E_PROFILE_LOAD` | profile | Failed to load profile |
| `E_PROFILE_SWITCH_FAILED` | profile | Profile switch timeout |
| `E_SYNC_TIMEOUT` | sync | Sync gate timeout |
| `E_BIA_VISION_FAILED` | bia | Vision API error |

Full list: see `error_codes.py` (50 codes).
