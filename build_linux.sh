#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# CPSL Linux AppImage Builder
# ═══════════════════════════════════════════════════════════════
# Usage:  ./build_linux.sh
# Output: dist/CyclingPerformanceStudioLab-v<VERSION>-x86_64.AppImage
#
# Build in docker for oldest supported host:
#   docker run --rm -v "$PWD":/src -w /src ubuntu:22.04 bash build_linux.sh
# ═══════════════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

if [ "$(uname -s)" != "Linux" ]; then
    echo "build_linux.sh must run on Linux."
    echo "  docker run --rm -v \"\$PWD\":/src -w /src ubuntu:22.04 bash build_linux.sh"
    exit 1
fi

VERSION="$(tr -d '[:space:]' < VERSION)"
APP_NAME="CyclingPerformanceStudioLab"
DIST="dist/${APP_NAME}"
APPDIR="build/${APP_NAME}.AppDir"
ARTIFACT="dist/${APP_NAME}-v${VERSION}-x86_64.AppImage"

GLIBC_FLOOR="${GLIBC_FLOOR:-2.35}"
GLIBCXX_FLOOR="${GLIBCXX_FLOOR:-3.4.30}"
CXXABI_FLOOR="${CXXABI_FLOOR:-1.3.13}"

echo "=== CPSL Linux AppImage Build (v${VERSION}) ==="

export APPIMAGE_EXTRACT_AND_RUN="${APPIMAGE_EXTRACT_AND_RUN:-1}"

for tool in objdump ldd appimagetool; do
    if ! command -v "$tool" &> /dev/null; then
        echo "Required tool missing: $tool"
        exit 1
    fi
done

# 1. Dependencies
echo "[1/8] Installing dependencies..."
pip3 install -r requirements.txt pyinstaller

# 2. Freeze
rm -rf dist build/$APP_NAME
echo "[2/8] Building with PyInstaller..."
set -o pipefail
pyinstaller CyclingPerformanceStudioLab.spec --clean --noconfirm 2>&1 | tail -3
set +o pipefail
[ -x "${DIST}/${APP_NAME}" ] || { echo "FATAL: ${DIST}/${APP_NAME} not produced"; exit 1; }

# 3. Version smoke-test
BUNDLED_VER_FILE="$(find "$DIST" -name VERSION -type f 2>/dev/null | head -1)"
BUNDLED_VER="$(tr -d '[:space:]' < "$BUNDLED_VER_FILE" 2>/dev/null)"
if [ -z "$BUNDLED_VER_FILE" ] || [ "$BUNDLED_VER" != "$VERSION" ]; then
    echo "FATAL: bundled VERSION ('$BUNDLED_VER') != repo VERSION ('$VERSION')" >&2
    exit 1
fi
echo "[3/8] Version smoke-test OK — bundle reports $BUNDLED_VER"

# 4. Strip host graphics/runtime libs
echo "[4/8] Stripping bundled graphics/runtime libraries..."
for lib in 'libstdc++.so.6*' 'libgcc_s.so.1*' 'libgbm.so.1*' 'libxshmfence.so.1*'; do
    find "$DIST" -type f -name "$lib" -print -delete
done

# 5. Symbol-version gate
echo "[5/8] Symbol-version gate..."
SYMS="$(mktemp)"
trap 'rm -f "$SYMS"' EXIT
find "$DIST" -type f \( -name '*.so*' -o -perm -u+x \) -exec objdump -T {} + \
    > "$SYMS" 2>/dev/null || true

if [ ! -s "$SYMS" ]; then
    echo "FATAL: symbol sweep produced no output" >&2
    exit 1
fi

gate_family() {
    local prefix="$1" floor="$2" max highest
    max="$(grep -oE "${prefix}[0-9]+(\.[0-9]+)+" "$SYMS" | sed "s/^${prefix}//" \
           | sort -V | tail -1)"
    if [ -z "$max" ]; then
        echo "  ${prefix%_}: none referenced"
        return 0
    fi
    highest="$(printf '%s\n%s\n' "$max" "$floor" | sort -V | tail -1)"
    if [ "$highest" != "$floor" ]; then
        echo "  ${prefix%_}: needs $max, floor is $floor" >&2
        return 1
    fi
    echo "  ${prefix%_}: needs $max, floor is $floor"
}

GATE_FAIL=0
gate_family "GLIBC_"   "$GLIBC_FLOOR"   || GATE_FAIL=1
gate_family "GLIBCXX_" "$GLIBCXX_FLOOR" || GATE_FAIL=1
gate_family "CXXABI_"  "$CXXABI_FLOOR"  || GATE_FAIL=1
if [ "$GATE_FAIL" -ne 0 ]; then
    echo "FATAL: binary requires newer runtime symbols than oldest supported host" >&2
    exit 1
fi

# 6. Assemble AppDir
echo "[6/8] Assembling AppDir..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons"
cp -a "$DIST/." "$APPDIR/usr/bin/"
cp -a assets/linux/hicolor "$APPDIR/usr/share/icons/"
cp assets/linux/cpsl.png "$APPDIR/cpsl.png"

cat > "$APPDIR/cpsl.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Cycling Performance Studio Lab
Comment=Cycling training planner with power analysis and performance tracking
Exec=CyclingPerformanceStudioLab
Icon=cpsl
Categories=Education;Sports;
Terminal=false
StartupWMClass=CyclingPerformanceStudioLab
DESKTOP
cp "$APPDIR/cpsl.desktop" "$APPDIR/usr/share/applications/"

# QtWebEngineProcess check
QTWEP="$(find "$APPDIR/usr/bin" -type f -name QtWebEngineProcess 2>/dev/null | head -1)"
if [ -z "$QTWEP" ]; then
    echo "Warning: QtWebEngineProcess not found — web views may not render"
    QTWEP_PATH=""
else
    QTWEP_REL="${QTWEP#"$APPDIR"/}"
    echo "  QtWebEngineProcess: $QTWEP_REL"
    QTWEP_PATH="$QTWEP_REL"
fi

cat > "$APPDIR/AppRun" <<APPRUN
#!/bin/sh
APPDIR="\$(dirname "\$(readlink -f "\$0")")"
export QTWEBENGINE_DISABLE_SANDBOX="\${QTWEBENGINE_DISABLE_SANDBOX:-1}"
export QTWEBENGINEPROCESS_PATH="\${QTWEBENGINEPROCESS_PATH:-\$APPDIR/${QTWEP_PATH}}"
export QT_SCALE_FACTOR="\${QT_SCALE_FACTOR:-1.25}"
exec "\$APPDIR/usr/bin/${APP_NAME}" "\$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# 7. Assert no bundled graphics libs
echo "[7/8] Asserting no bundled graphics/runtime libraries..."
LEAKED="$(find "$APPDIR" -type f \( -name 'libGL.so.*' -o -name 'libGLX.so.*' \
    -o -name 'libEGL.so.*' -o -name 'libdrm.so.*' -o -name 'libgbm.so.*' \
    -o -name 'libstdc++.so.*' -o -name 'libgcc_s.so.*' \) 2>/dev/null || true)"
if [ -n "$LEAKED" ]; then
    echo "FATAL: bundled libraries that must come from the host:" >&2
    echo "$LEAKED" >&2
    exit 1
fi
echo "  none present"

# 8. Build AppImage
echo "[8/8] Building AppImage..."
rm -f "$ARTIFACT"
ARCH=x86_64 appimagetool --no-appstream "$APPDIR" "$ARTIFACT"
[ -f "$ARTIFACT" ] || { echo "FATAL: appimagetool produced no artifact"; exit 1; }
chmod +x "$ARTIFACT"

SIZE=$(du -h "$ARTIFACT" | cut -f1)
echo ""
echo "=== Build complete ==="
echo "AppImage: $ARTIFACT ($SIZE)"
