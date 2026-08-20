#!/bin/bash
# Cycling Performance Studio Lab - Linux Build Script
# Produces a standalone executable and packages it as a tar.gz.
# (AppImage is attempted only if appimagetool is present; otherwise tar.gz fallback.)
set -e
cd "$(dirname "$0")"

VERSION="$(tr -d '[:space:]' < VERSION 2>/dev/null || echo 1.0.0)"
APP_NAME="CyclingPerformanceStudioLab"
DIST="dist/${APP_NAME}"

echo "=== CPSL Linux Build (v${VERSION}) ==="

export APPIMAGE_EXTRACT_AND_RUN="${APPIMAGE_EXTRACT_AND_RUN:-1}"

echo "[1/4] Installing dependencies..."
pip3 install -r requirements-common.txt pyinstaller 2>&1 | tail -2
pip3 install -r requirements-linux.txt 2>&1 | tail -2 || echo "Warning: alcuni moduli Linux potrebbero non essere disponibili"

echo "[2/4] Building with PyInstaller..."
rm -rf dist/${APP_NAME} build/${APP_NAME}
pyinstaller CyclingPerformanceStudioLab.spec --clean --noconfirm 2>&1 | tail -3
[ -x "${DIST}/${APP_NAME}" ] || { echo "FATAL: ${DIST}/${APP_NAME} non prodotto"; exit 1; }

echo "[3/4] Packaging tar.gz..."
tar -czf "dist/${APP_NAME}-v${VERSION}-linux-x86_64.tar.gz" -C dist "${APP_NAME}"
echo "  -> dist/${APP_NAME}-v${VERSION}-linux-x86_64.tar.gz"

echo "[4/4] Attempting AppImage (optional)..."
if command -v appimagetool &> /dev/null; then
    APPDIR="build/${APP_NAME}.AppDir"
    rm -rf "$APDIR"
    mkdir -p "$APDIR/usr/bin"
    cp -a "${DIST}/." "$APDIR/usr/bin/"
    cat > "$APDIR/${APP_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Cycling Performance Studio Lab
Comment=Cycling training planner with power analysis
Exec=${APP_NAME}
Categories=Education;Sports;
Terminal=false
DESKTOP
    (cd "$APDIR" && ln -sf "usr/bin/${APP_NAME}" "${APP_NAME}" 2>/dev/null || true)
    appimagetool --no-appstream "$APDIR" "dist/${APP_NAME}-v${VERSION}-linux-x86_64.AppImage" 2>/dev/null \
        && echo "  -> AppImage creato" || echo "  AppImage skip (fallback tar.gz)"
else
    echo "  appimagetool non disponibile -> uso tar.gz"
fi

echo "=== Build complete ==="
ls -la dist/*.tar.gz dist/*.AppImage 2>/dev/null
