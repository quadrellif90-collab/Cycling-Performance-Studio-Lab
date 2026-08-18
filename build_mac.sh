#!/bin/bash
# Cycling Performance Studio Lab - macOS Build Script
# Builds macOS .dmg package using pyinstaller and create-dmg

set -e

echo "============================================"
echo "Cycling Performance Studio Lab - macOS Build"
echo "============================================"

:: Check if python is available
python3 --version
if [ $? -ne 0 ]; then
    echo "Errore: Python3 non trovato"
    exit 1
fi

:: Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements-common.txt
if [ $? -ne 0 ]; then
    echo "Errore: impossibile installare le dipendenze comuni"
    exit 1
fi

:: macOS-specific dependencies
echo "Installing macOS-specific dependencies..."
pip3 install pywebview[cocoa] create-dmg
if [ $? -ne 0 ]; then
    echo "Warning: alcuni moduli macOS potrebbero non essere disponibili"
fi

:: Build executable
echo "Building executable..."
python3 -m PyInstaller --noconfirm --windowed --name "Cycling-Performance-Studio-Lab" app.py

if [ $? -ne 0 ]; then
    echo "Errore durante la build dell'eseguibile"
    exit 1
fi

:: Create .dmg
echo "Creating .dmg package..."
mkdir -p dist
create-dmg --volumename "Cycling Performance Studio Lab" --window-pos 200 200 --icon icns/Cycling-Performance-Studio-Lab.icns --app-drop-link 150 400 dist/Cycling-Performance-Studio-Lab.app dist/

echo "Build completato con successo!"
echo "File .dmg creato nella cartella dist/"
exit 0