"""
Cycling Performance Studio Lab - Main Application Entry Point

A professional cycling analytics platform combining the best of Domestique and PCC.
"""

import asyncio
import contextlib
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# PCC Math modules integration
from fitness_estimation import (
    estimate_ftp, compute_fitness_signature, compute_cp_wprime
)
from power_curve import aggregate_power_curve

# Load .env from multiple candidate locations (dev, packaged, legacy)
def _load_env_files():
    candidates = [
        Path(__file__).parent / ".env",                          # dev mode
        Path.home() / ".cpsl" / ".env",                          # packaged mode
        Path.home() / "Documents" / "health_tracker" / ".env",   # legacy
    ]
    for p in candidates:
        if p.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(p, override=False)
                logging.info(f"Loaded .env from {p}")
            except Exception as e:
                logging.warning(f"Failed to load .env from {p}: {e}")

_load_env_files()

# Local imports
from config import config
from error_codes import Codes, _log_error, REGISTRY
from log_config import setup_logging
from profile_manager import ProfileManager
from sync_targets import get_target, connected_targets

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Diagnostic ring buffer for error observability
_DIAG_RING: deque[dict] = deque(maxlen=256)

def _log_error(code: str, exc: Exception | None = None, **context) -> None:
    """Single funnel for structured error logging with E_<domain>_<failure> codes."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "code": code,
        "message": str(exc) if exc else "",
        "context": context,
    }
    _DIAG_RING.append(entry)
    
    # Also log via standard logging
    meta = REGISTRY.get(code)
    if meta:
        level = getattr(logging, meta["severity"], logging.ERROR)
        logger.log(level, f"[{code}] {meta['description']} | {entry}")

# Global state
_profile_manager: Optional[ProfileManager] = None
_sync_lock = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _profile_manager
    logger.info("Starting Cycling Performance Studio Lab")
    
    # Initialize profile manager
    _profile_manager = ProfileManager.get()
    await _profile_manager.initialize()
    
    # Start background tasks
    yield
    
    # Cleanup
    logger.info("Shutting down Cycling Performance Studio Lab")
    if _profile_manager:
        _profile_manager.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Cycling Performance Studio Lab",
    description="Professional cycling analytics platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Static files and templates
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")

# Helper to get profile manager
def get_pm() -> ProfileManager:
    if _profile_manager is None:
        raise RuntimeError("Profile manager not initialized")
    return _profile_manager

# =============================================================================
# API Routes - Core
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard."""
    pm = get_pm()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "profiles": pm.list_profiles(),
        "active_profile": pm.active_id,
        "config": config,
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Profile management page."""
    pm = get_pm()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profiles": pm.list_profiles(),
        "active_profile": pm.active_id,
        "athlete": pm.active_athlete if pm.active_id else {},
    })

@app.get("/workouts", response_class=HTMLResponse)
async def workouts_page(request: Request):
    """Workout library page."""
    return templates.TemplateResponse("workouts.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page."""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    pm = get_pm()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "sync_targets": list_targets(),
        "connected": connected_targets(),
    })

# =============================================================================
# API Routes - Profiles
# =============================================================================

@app.get("/api/profiles")
async def api_list_profiles():
    """List all profiles."""
    pm = get_pm()
    return {"profiles": pm.list_profiles(), "active": pm.active_id}

@app.post("/api/profiles")
async def api_create_profile(request: Request):
    """Create a new profile."""
    pm = get_pm()
    data = await request.json()
    name = data.get("name", "").strip()
    color = data.get("color")
    
    if not name:
        return JSONResponse({"error": "Name required"}, status_code=400)
    
    try:
        profile_id = pm.create_profile(name, color)
        return {"profile_id": profile_id}
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.post("/api/profiles/{profile_id}/switch")
async def api_switch_profile(profile_id: str):
    """Switch active profile."""
    pm = get_pm()
    try:
        pm.switch(profile_id)
        return {"success": True, "active": pm.active_id}
    except Exception as e:
        _log_error(Codes.PROFILE_LOAD, e, profile_id=profile_id)
        return JSONResponse({"error": str(e)}, status_code=400)

@app.delete("/api/profiles/{profile_id}")
async def api_delete_profile(profile_id: str):
    """Delete a profile."""
    pm = get_pm()
    try:
        pm.delete_profile(profile_id)
        return {"success": True}
    except Exception as e:
        _log_error(Codes.PROFILE_LOAD, e, profile_id=profile_id)
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/api/profiles/{profile_id}/athlete")
async def api_get_athlete(profile_id: str):
    """Get athlete data for profile."""
    pm = get_pm()
    if profile_id != pm.active_id:
        return JSONResponse({"error": "Profile not active"}, status_code=400)
    return pm.active_athlete

@app.post("/api/profiles/{profile_id}/athlete")
async def api_save_athlete(profile_id: str, request: Request):
    """Save athlete data for profile."""
    pm = get_pm()
    if profile_id != pm.active_id:
        return JSONResponse({"error": "Profile not active"}, status_code=400)
    
    data = await request.json()
    try:
        pm.save_athlete(data)
        return {"success": True}
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.post("/api/profiles/{profile_id}/env")
async def api_save_env(profile_id: str, request: Request):
    """Save .env credentials for profile."""
    pm = get_pm()
    if profile_id != pm.active_id:
        return JSONResponse({"error": "Profile not active"}, status_code=400)
    
    data = await request.json()
    icu_athlete_id = data.get("icu_athlete_id", "").strip()
    icu_api_key = data.get("icu_api_key", "").strip()
    icu_access_token = data.get("icu_access_token", "").strip()
    bia_vision_api_key = data.get("bia_vision_api_key", "").strip()
    
    try:
        pm.save_env(icu_athlete_id, icu_api_key, icu_access_token, bia_vision_api_key)
        return {"success": True}
    except Exception as e:
        _log_error(Codes.PROFILE_LOAD, e, profile_id=profile_id)
        return JSONResponse({"error": str(e)}, status_code=400)

# =============================================================================
# API Routes - Sync
# =============================================================================

@app.get("/api/sync/targets")
async def api_sync_targets():
    """List available sync targets."""
    return {"targets": list_targets(), "connected": connected_targets()}

@app.post("/api/sync/icu/push")
async def api_sync_icu_push(request: Request):
    """Push data to Intervals.icu."""
    pm = get_pm()
    if not pm.active_id:
        return JSONResponse({"error": "No active profile"}, status_code=400)
    
    data = await request.json()
    target = get_target("intervals_icu")
    if not target or not target.is_configured():
        return JSONResponse({"error": "ICU not configured"}, status_code=400)
    
    # This would be implemented with actual push logic
    return {"success": True, "message": "Push initiated"}

# =============================================================================
# API Routes - Math & Analytics
# =============================================================================

class FitnessEstimation(BaseModel):
    efforts: Dict[int, int]  # {duration_s: best_avg_watts}
    ftp: Optional[int] = None

class CpWprimeRequest(BaseModel):
    efforts: Dict[int, int]

@app.post("/api/fitness/estimate ftp")
async def api_estimate_ftp(request: Request):
    """Estimate FTP from best effort data."""
    data = await request.json()
    efforts = data.get("efforts", {})
    ftp = estimate_ftp(efforts) if efforts else None
    return {"ftp": ftp, "success": ftp is not None}

@app.post("/api/fitness/signature")
async def api_fitness_signature(request: Request):
    """Compute fitness signature (FTP, LTP, HIE, Pmax)."""
    data = await request.json()
    efforts = data.get("efforts", {})
    ftp = data.get("ftp")
    signature = compute_fitness_signature(efforts, ftp) if efforts and ftp else None
    if signature is None:
        return JSONResponse({"error": "Insufficient data"}, status_code=400)
    return {
        "ftp": signature.ftp,
        "ltp": signature.ltp,
        "hie": signature.hie,
        "peak_power": signature.peak_power,
        "success": True
    }

@app.post("/api/fitness/cp-wprime")
async def api_cp_wprime(request: Request):
    """Compute Monod-Scherrer CP/W' values."""
    data = await request.json()
    efforts = data.get("efforts", {})
    cp, wprime = compute_cp_wprime(efforts)
    if cp is None or wprime is None:
        return JSONResponse({"error": "Insufficient data for CP/W' fit"}, status_code=400)
    return {
        "cp": cp,
        "w_prime": wprime,
        "success": True
    }

# =============================================================================
# API Routes - Diagnostics
# =============================================================================

@app.get("/api/diag/recent-errors")
async def api_recent_errors():
    """Get recent errors from diagnostic ring."""
    return {"errors": list(_DIAG_RING)}

@app.get("/api/diag/health")
async def api_health():
    """Health check endpoint."""
    pm = get_pm()
    return {
        "status": "ok",
        "active_profile": pm.active_id,
        "profiles_count": len(pm.list_profiles()),
        "sync_targets": list_targets(),
    }

# =============================================================================
# Main entry point for desktop app
# =============================================================================

def run_web():
    """Run the web server (for development)."""
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=config.DOMESTIQUE_PORT,
        reload=True,
        log_level="info",
    )

def run_desktop():
    """Run as desktop application with pywebview."""
    import webview
    
    # Start FastAPI in background thread
    def start_server():
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=config.DOMESTIQUE_PORT,
            log_level="warning",
        )
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Create webview window
    window = webview.create_window(
        "Cycling Performance Studio Lab",
        f"http://127.0.0.1:{config.DOMESTIQUE_PORT}",
        width=1400,
        height=900,
        min_size=(1000, 700),
    )
    
    webview.start(debug=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "desktop":
        run_desktop()
    else:
        run_web()