# API Endpoints

Riferimento completo di tutti gli endpoint HTTP di Cycling Performance Studio Lab.

**Base URL:** `http://127.0.0.1:22400`

---

## Autenticazione

Tutti gli endpoint API sono accessibili senza autenticazione in modalita sviluppo.
Per la produzione, implementare middleware di autenticazione personalizzato.

---

## Pagine HTML

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/` | Dashboard principale |
| GET | `/profile` | Gestione profilo |
| GET | `/workouts` | Libreria workout |
| GET | `/analytics` | Dashboard analytics |
| GET | `/settings` | Impostazioni |

---

## Profili API

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/profiles` | Lista tutti i profili |
| POST | `/api/profiles` | Crea nuovo profilo |
| POST | `/api/profiles/{id}/switch` | Cambia profilo attivo |
| DELETE | `/api/profiles/{id}` | Elimina profilo |
| GET | `/api/profiles/{id}/athlete` | Ottieni dati atleta |
| POST | `/api/profiles/{id}/athlete` | Salva dati atleta |
| POST | `/api/profiles/{id}/env` | Salva credenziali .env |

### POST `/api/profiles`

Crea un nuovo profilo atleta.

```json
Request:
{
  "name": "Marco",
  "color": "blue"
}

Response:
{
  "profile_id": "marco"
}
```

### POST `/api/profiles/{id}/athlete`

Salva dati atleta con validazione.

```json
Request:
{
  "ftp": 250,
  "weight_kg": 75,
  "lthr": 175,
  "max_hr": 195,
  "lbm_kg": 60,
  "age": 32,
  "sex": "M"
}

Response:
{
  "success": true
}
```

**Validazione:**
- FTP: 50-600 W
- Peso: 30-200 kg
- LTHR: 100-250 bpm
- Max HR: 100-250 bpm
- LBM: 20-150 kg

### POST `/api/profiles/{id}/env`

Salva credenziali per profilo (ICU, BIA Vision).

```json
Request:
{
  "icu_athlete_id": "12345",
  "icu_api_key": "xxx",
  "icu_access_token": "xxx",
  "bia_vision_api_key": "xxx"
}

Response:
{
  "success": true
}
```

---

## Sync API

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/sync/targets` | Lista target sync disponibili |
| POST | `/api/sync/icu/push` | Push dati a Intervals.icu |

---

## Fitness & Analytics API

| Method | Path | Descrizione |
|--------|------|-------------|
| POST | `/api/fitness/estimate-ftp` | Stima FTP dai best efforts |
| POST | `/api/fitness/signature` | Calcola firma fitness completa |
| POST | `/api/fitness/cp-wprime` | Analisi CP/W' Monod-Scherrer |

### POST `/api/fitness/estimate-ftp`

Stima FTP usando scaling factors Coggan.

```json
Request:
{
  "efforts": {
    "300": 280,
    "600": 250,
    "1200": 230,
    "3600": 210
  }
}

Response:
{
  "ftp": 209,
  "success": true,
  "cached": false
}
```

### POST `/api/fitness/signature`

Calcola firma fitness completa (FTP, LTP, HIE, Pmax).

```json
Request:
{
  "efforts": {"300": 280, "600": 250},
  "ftp": 210
}

Response:
{
  "ftp": 210,
  "ltp": 157,
  "hie": 21300,
  "peak_power": 418,
  "success": true
}
```

### POST `/api/fitness/cp-wprime`

Modello Monod-Scherrer per Critical Power e W'.

```json
Request:
{
  "efforts": {
    "180": 350,
    "300": 280,
    "600": 250,
    "1200": 230
  }
}

Response:
{
  "cp": 205.0,
  "w_prime": 23143,
  "success": true
}
```

---

## Infortuni API

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/injuries` | Lista infortuni + sommario |
| POST | `/api/injuries` | Crea infortunio |
| PUT | `/api/injuries/{id}` | Aggiorna infortunio |
| POST | `/api/injuries/{id}/resolve` | Risolvi infortunio |
| DELETE | `/api/injuries/{id}` | Elimina infortunio |

### POST `/api/injuries`

```json
Request:
{
  "name": "Tendinite rotulea",
  "date_start": "2025-01-15",
  "severity": "medium",
  "notes": "Dolore dopo allenamento in salita"
}

Response:
{
  "success": true,
  "injury_id": "inj_20250115_abc123"
}
```

### GET `/api/injuries`

```json
Response:
{
  "active_injuries": [...],
  "summary": {
    "active_count": 2,
    "total_count": 5,
    "by_severity": {
      "minor": 1,
      "medium": 3,
      "severe": 1
    },
    "recent_injuries": [...]
  }
}
```

---

## GPX Import API

| Method | Path | Descrizione |
|--------|------|-------------|
| POST | `/api/gpx/import` | Upload file GPX |
| POST | `/api/gpx/parse-file` | Parsing GPX da path |

### POST `/api/gpx/import`

Upload multipart di file `.gpx`.

```json
Response:
{
  "success": true,
  "filename": "ride.gpx",
  "summary": {
    "total_tracks": 1,
    "total_distance_km": 45.2,
    "total_elevation_gain_m": 850,
    "total_duration_s": 5400
  },
  "routes": [
    {
      "track_name": "Morning Ride",
      "distance_meters": 45200,
      "elevation_gain_m": 850,
      "avg_power_w": 185,
      "max_power_w": 420,
      "avg_hr": 155,
      "max_hr": 182
    }
  ]
}
```

---

## Data Export API

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/export/backup` | Backup completo profilo |
| GET | `/api/export/metrics` | Export metriche profilo |
| GET | `/api/export/zip` | Backup ZIP compresso |

---

## Session API

| Method | Path | Descrizione |
|--------|------|-------------|
| POST | `/api/sessions` | Crea sessione |
| GET | `/api/sessions` | Lista sessioni attive |
| GET | `/api/sessions/{id}` | Ottieni dettagli sessione |
| DELETE | `/api/sessions/{id}` | Distruggi sessione |

---

## Diagnostica API

| Method | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/diag/recent-errors` | Errori recenti |
| GET | `/api/diag/health` | Health check |

### GET `/api/diag/health`

```json
Response:
{
  "status": "ok",
  "active_profile": "marco",
  "profiles_count": 3,
  "sync_targets": ["intervals_icu"]
}
```

---

## Codici di Errore

Tutti gli errori usano il formato `E_<domain>_<failure>`.

| Codice | Dominio | Descrizione |
|--------|---------|-------------|
| `E_PROFILE_LOAD` | profile | Caricamento profilo fallito |
| `E_PROFILE_SWITCH_FAILED` | profile | Timeout cambio profilo |
| `E_SYNC_TIMEOUT` | sync | Timeout sync gate |
| `E_SYNC_BLOCKING_SLOW` | sync | Sync bloccata/lenta |
| `E_BIA_VISION_FAILED` | bia | Errore Vision API |
| `E_EXPORT_FAILED` | export | Export fallito |

Per l'elenco completo vedere `error_codes.py` (50 codici).

---

## Rate Limiting

Nessun rate limiting implementato in modalita sviluppo.
Per la produzione, implementare rate limiting personalizzato.

---

## Formato Risposta

Tutti gli endpoint JSON restituiscono risposte nel formato:

```json
{
  "success": true,
  "data": { ... }
}
```

In caso di errore:

```json
{
  "error": "Descrizione errore",
  "detail": "Dettagli aggiuntivi"
}
```
