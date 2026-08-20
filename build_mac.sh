#!/bin/bash
# Cycling Performance Studio Lab - macOS Build Script
# Produces dist/Cycling-Performance-Studio-Lab.app and packages it as a tar.gz
# (creates a .dmg only if `create-dmg` ruby gem is available; otherwise falls back to tar.gz).
set -e

echo "============================================"
echo "Cycling Performance Studio Lab - macOS Build"
echo "============================================"

python3 --version || { echo "Errore: Python3 non trovato"; exit 1; }

echo "Installing dependencies..."
pip3 install -r requirements-common.txt
pip3 install pyinstaller
pip3 install -r requirements-mac.txt 2>/dev/null || echo "Warning: alcuni moduli macOS potrebbero non essere disponibili"

echo "Building executable (.app)..."
python3 -m PyInstaller --noconfirm --windowed \
    --name "Cycling-Performance-Studio-Lab" \
    --icon assets/icon.icns \
    app.py

APP="dist/Cycling-Performance-Studio-Lab.app"
[ -d "$APP" ] || { echo "FATAL: $APP non prodotto"; exit 1; }

# Try to build a .dmg if create-dmg is available (ruby gem), else tar.gz
if command -v create-dmg &> /dev/null; then
    echo "Creating .dmg package..."
    create-dmg --volname "Cycling Performance Studio Lab" \
        --icon "Cycling-Performance-Studio-Lab.app" 200 200 \
        --app-drop-link 400 200 \
        "dist/Cycling-Performance-Studio-Lab.dmg" "$APP" || true
fi

if [ -f "dist/Cycling-Performance-Studio-Lab.dmg" ]; then
    echo "Build completato: dist/Cycling-Performance-Studio-Lab.dmg"
else
    echo "Creating .tar.gz fallback (no create-dmg)..."
    tar -czf "dist/Cycling-Performance-Studio-Lab-macOS.tar.gz" -C dist "Cycling-Performance-Studio-Lab.app"
    echo "Build completato: dist/Cycling-Performance-Studio-Lab-macOS.tar.gz"
fi
exit 0
