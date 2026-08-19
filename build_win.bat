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

pause
