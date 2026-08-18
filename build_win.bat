@echo off
:: Cycling Performance Studio Lab - Windows Build Script
:: Builds executable using PyInstaller with pythonnet support

echo ============================================
echo Cycling Performance Studio Lab - Windows Build
echo ============================================

:: Check if python is available
python --version
if %errorlevel% neq 0 (
    echo Errore: Python non trovato nel PATH
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Installing dependencies...
pip install -r requirements-common.txt
if %errorlevel% neq 0 (
    echo Errore: impossibile installare le dipendenze comuni
    pause
    exit /b 1
)

:: Windows-specific dependencies
echo Installing Windows-specific dependencies...
pip install -r requirements-win.txt
if %errorlevel% neq 0 (
    echo Warning: alcuni moduli Windows potrebbero non essere disponibili
)

:: Build with PyInstaller
echo Building executable...
pyinstaller --noconfirm --onefile --windowed ^
    --name Cycling-Performance-Studio-Lab ^
    --add-binary "pythonnet.dll;." ^
    --add-data "requirements-common.txt;." ^
    app.py

if %errorlevel% neq 0 (
    echo Errore durante la build
    pause
    exit /b 1
)

echo Build completato con successo!
echo File eseguibile creato nella cartella dist/

pause