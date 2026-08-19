# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Cycling Performance Studio Lab.

Build:
  Windows: pyinstaller CyclingPerformanceStudioLab.spec

Output: dist/CyclingPerformanceStudioLab.exe
"""

import sys
import os
from pathlib import Path

block_cipher = None
app_name = "CyclingPerformanceStudioLab"

try:
    _spec_dir = Path(SPEC).resolve().parent
except NameError:
    _spec_dir = Path(os.path.abspath(os.getcwd()))
VERSION = (_spec_dir / "VERSION").read_text(encoding="utf-8-sig").strip()

datas = [
    ("frontend/templates", "frontend/templates"),
    ("frontend/static", "frontend/static"),
    ("workouts", "workouts"),
    ("courses", "courses"),
    ("VERSION", "."),
]

# v2.1.0 WIN-TLS-FIX: bundle certifi's CA bundle so urllib can verify certs
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files("certifi")

# ICU OAuth credentials (if present)
if os.path.exists(".oauth.env"):
    datas.append((".oauth.env", "."))

binaries: list = []

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "certifi",
        "uvicorn.logging",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "fastapi",
        "starlette.routing",
        "starlette.responses",
        "starlette.staticfiles",
        "starlette.templating",
        "jinja2",
        "httpx",
        "pydantic",
        "pystray",
        "PIL",
        "webview",
        # Windows webview backends (pythonnet)
        *(["clr", "clr_loader", "webview.platforms.edgechromium",
           "webview.platforms.winforms", "proxy_tools"]
          if sys.platform == "win32" else []),
        # fit_tool (FIT workout export + ride parser)
        "fit_tool",
        "fit_tool.fit_file",
        "fit_tool.fit_file_builder",
        "fit_tool.profile.profile_type",
        "fit_tool.profile.messages.file_id_message",
        "fit_tool.profile.messages.workout_message",
        "fit_tool.profile.messages.workout_step_message",
        # scipy for tau_fitting
        "scipy",
        "scipy.optimize",
        "scipy.linalg",
        # Core modules
        "profile_manager",
        "log_config",
        "error_codes",
        "config",
        "zones",
        "capacity_cap",
        "fitness_estimation",
        "power_curve",
        "ride_storage",
        "user_home",
        # PCC modules (imported from Performance Cycling Calculator)
        "bia_parser",
        "bia_vision",
        "gpx_parser",
        "session_manager",
        "caching",
        "injury_manager",
        "data_export",
        "activity_insights",
        "calendar_ics",
        "cp_models",
        "cpep_import",
        "custom_charts",
        "diet",
        "field_test_protocols",
        "hrv_engine",
        "huawei_api",
        "huawei_discovery",
        "huawei_hrv",
        "metabolic_decoder",
        "my_progress",
        "notifications",
        "nutrition",
        "ocr_pdf",
        "pedal_asymmetry",
        "plan_export",
        "plan_options",
        "run_web",
        "strength_mobility",
        # Domestique modules
        "readiness",
        "readiness_composite",
        "sleep",
        "execution_score",
        "fit_activity",
        "workout_facts",
        "strain_score",
        "tau_fitting",
        "continuous_policy",
        "hr_targets",
        "oos_validation",
        "structure_fidelity",
        "geodesy",
        "route_archetypes",
        "sleep_inhibit",
        "training",
        "training_planner",
        "sync_targets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pandas", "PyQt5"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # console for now (dev mode)
    icon="assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
