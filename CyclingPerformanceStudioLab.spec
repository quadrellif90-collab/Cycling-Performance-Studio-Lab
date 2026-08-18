# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Cycling Performance Studio Lab."""

import os

block_cipher = None
SRC = os.path.abspath('.')

a = Analysis(
    ['app.py'],
    pathex=[SRC],
    binaries=[],
    datas=[
        ('frontend/templates', 'frontend/templates'),
        ('frontend/static', 'frontend/static'),
    ],
    hiddenimports=[
        # Uvicorn
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.off',
        # Standard lib
        'email.mime.text',
        'email.mime.multipart',
        'json',
        'xml.etree.ElementTree',
        # Core modules
        'profile_manager',
        'log_config',
        'error_codes',
        'config',
        'zones',
        'capacity_cap',
        'fitness_estimation',
        'power_curve',
        'ride_storage',
        'user_home',
        # PCC Enhanced modules
        'bia_parser',
        'gpx_parser',
        'session_manager',
        'caching',
        'injury_manager',
        'data_export',
        # Domestique modules
        'readiness',
        'readiness_composite',
        'sleep',
        'execution_score',
        'fit_activity',
        'workout_facts',
        'strain_score',
        'tau_fitting',
        'continuous_policy',
        'hr_targets',
        'oos_validation',
        'structure_fidelity',
        'geodesy',
        'route_archetypes',
        'sleep_inhibit',
        'training',
        'training_planner',
        'sync_targets',
        # Jinja2
        'jinja2',
        'jinja2.ext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'pandas',
        'scipy', 'PIL', 'cv2', 'torch', 'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CyclingPerformanceStudioLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
