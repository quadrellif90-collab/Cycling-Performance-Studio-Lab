@echo off
:: Cycling Performance Studio Lab - Windows Build Script
:: Builds executable using PyInstaller spec file

echo ============================================
echo Cycling Performance Studio Lab - Windows Build
echo ============================================

:: Check if python is available
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Installing dependencies...
pip install -r requirements-common.txt
if %errorlevel% neq 0 (
    echo Error: cannot install common dependencies
    pause
    exit /b 1
)

:: Windows-specific dependencies
echo Installing Windows-specific dependencies...
pip install -r requirements-win.txt 2>nul

:: v1.4.2 BUILD-HYGIENE: pulizia cache e artefatti locali prima del build.
:: Garantisce che l'exe distribuito non contenga bytecode stantio né dati
:: personali (piani, profili, credenziali) residui da sessioni di sviluppo.
echo Cleaning caches and local data from the bundle inputs...
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
:: Dati utente mai nel bundle: piani personali, credenziali, config AI locale.
if exist "plans\current_plan.json" del /q "plans\current_plan.json"
if exist "ai_config.json" echo   [skip] ai_config.json resta fuori dal bundle (non in datas)

:: Build with PyInstaller using spec file
echo Building executable...
pyinstaller CyclingPerformanceStudioLab.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo Error during build
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable created in dist/CyclingPerformanceStudioLab/

@echo Build finished.
