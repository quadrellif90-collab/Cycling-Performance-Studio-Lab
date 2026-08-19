#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# CPSL macOS DMG Builder
# ═══════════════════════════════════════════════════════════════
# Usage: ./build_dmg.sh [--notarize]
# Output: ~/Desktop/CyclingPerformanceStudioLab.dmg
#
# Modes:
#   --notarize  Sign + notarize (requires .notarize.env)
#   (default)   Ad-hoc sign only
# ═══════════════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

export MACOSX_DEPLOYMENT_TARGET=11.0
MACOS_MIN="11.0"
PYINSTALLER="pyinstaller"
if [ ! -x ".venv-build/bin/pyinstaller" ]; then
    echo "  Build venv missing — creating it..."
    if [ -f scripts/setup_build_venv.sh ]; then
        bash scripts/setup_build_venv.sh
    fi
fi
if [ -x ".venv-build/bin/pyinstaller" ]; then
    PYINSTALLER=".venv-build/bin/pyinstaller"
    echo "  Using isolated build venv (.venv-build)"
fi

DMG_NAME="CyclingPerformanceStudioLab"
DMG_PATH="$HOME/Desktop/${DMG_NAME}.dmg"
STAGING="/tmp/dmg_staging"
RW_DMG="/tmp/${DMG_NAME}_rw.dmg"
APP_ZIP="/tmp/${DMG_NAME}.app.zip"
ICON_PNG="assets/icon.png"
ICON_ICNS="assets/icon.icns"
ENTITLEMENTS="entitlements.plist"

NOTARIZE_MODE="adhoc"
if [ "$1" = "--notarize" ] && [ -f .notarize.env ]; then
    source .notarize.env
    if [ -n "$NOTARIZE_IDENTITY" ] && [ -n "$NOTARIZE_APPLE_ID" ] \
       && [ -n "$NOTARIZE_APP_PASSWORD" ] && [ -n "$NOTARIZE_TEAM_ID" ]; then
        NOTARIZE_MODE="notarize"
    fi
fi

echo "=== CPSL macOS DMG Build (mode: $NOTARIZE_MODE) ==="

# Detach stale volumes
for mp in $(ls -d "/Volumes/${DMG_NAME}"* 2>/dev/null); do
    echo "  Detaching stale volume: $mp"
    hdiutil detach "$mp" -force >/dev/null 2>&1 || true
done

# 1. Build with PyInstaller
echo "[1/8] Building app with PyInstaller..."
"$PYINSTALLER" CyclingPerformanceStudioLab.spec --clean --noconfirm 2>&1 | tail -3

# 1b. Version smoke-test
REPO_VER="$(tr -d '[:space:]' < VERSION)"
BUNDLED_VER_FILE="$(find dist/CyclingPerformanceStudioLab.app -name VERSION -path '*Resources*' 2>/dev/null | head -1)"
[ -z "$BUNDLED_VER_FILE" ] && BUNDLED_VER_FILE="$(find dist/CyclingPerformanceStudioLab.app -name VERSION 2>/dev/null | head -1)"
BUNDLED_VER="$(tr -d '[:space:]' < "$BUNDLED_VER_FILE" 2>/dev/null)"
if [ -z "$BUNDLED_VER_FILE" ] || [ "$BUNDLED_VER" != "$REPO_VER" ]; then
    echo "FATAL: bundled VERSION ('$BUNDLED_VER') != repo VERSION ('$REPO_VER')" >&2
    exit 1
fi
echo "[1b/8] Version smoke-test OK — bundle reports $BUNDLED_VER"

# 2. Code signing
SIGN_IDENTITY="-"
if [ "$NOTARIZE_MODE" = "notarize" ]; then
    echo "[2/8] Resolving signing identity..."
    if [ -f .p12.env ]; then
        source .p12.env
        security import "$P12_PATH" -k ~/Library/Keychains/login.keychain-db \
            -P "$P12_PASSWORD" -T /usr/bin/codesign 2>/dev/null || true
    fi
    SIGN_IDENTITY=$(security find-identity -v -p codesigning 2>/dev/null \
        | grep "Developer ID Application" | head -1 | awk -F'"' '{print $2}')
    if [ -z "$SIGN_IDENTITY" ]; then
        echo "  No Developer ID found — falling back to ad-hoc"
        SIGN_IDENTITY="-"
    else
        echo "  Identity: $SIGN_IDENTITY"
    fi
fi

echo "[2/8] Signing app bundle..."
find dist/CyclingPerformanceStudioLab.app -type f \( -name '*.dylib' -o -name '*.so' -o -perm +111 \) \
    -exec codesign --force --sign "$SIGN_IDENTITY" --timestamp --options runtime \
    --entitlements "$ENTITLEMENTS" {} \; 2>/dev/null || true
codesign --force --sign "$SIGN_IDENTITY" --timestamp --options runtime \
    --entitlements "$ENTITLEMENTS" \
    dist/CyclingPerformanceStudioLab.app 2>/dev/null || true

# 3. Notarize .app (if notarize mode)
if [ "$NOTARIZE_MODE" = "notarize" ]; then
    echo "[3/8] Notarizing .app..."
    rm -f "$APP_ZIP"
    ditto -c -k --keepParent dist/CyclingPerformanceStudioLab.app "$APP_ZIP"
    xcrun notarytool submit "$APP_ZIP" \
        --apple-id "$NOTARIZE_APPLE_ID" \
        --password "$NOTARIZE_APP_PASSWORD" \
        --team-id "$NOTARIZE_TEAM_ID" \
        --wait --timeout 30m
    xcrun stapler staple dist/CyclingPerformanceStudioLab.app
    echo "  .app notarized and stapled"
else
    echo "[3/8] Skipping notarization (adhoc mode)"
fi

# 4. Create DMG
echo "[4/8] Creating DMG..."
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -a dist/CyclingPerformanceStudioLab.app "$STAGING/"
ln -s /Applications "$STAGING/Applications"

rm -f "$RW_DMG" "$DMG_PATH"
hdiutil create -srcfolder "$STAGING" -volname "$DMG_NAME" \
    -fs HFS+ -fsargs "-c c=64,a=16,e=16" \
    -format UDRW "$RW_DMG"

# 5. Set DMG icon
echo "[5/8] Setting DMG icon..."
if [ -f "$ICON_ICNS" ]; then
    cp "$ICON_ICNS" "$STAGING/.VolumeIcon.icns"
    SetFile -c icnC "$STAGING/.VolumeIcon.icns" 2>/dev/null || true
    SetFile -a C "$STAGING" 2>/dev/null || true
fi

# 6. Finder layout
echo "[6/8] Applying Finder layout..."
osascript <<APPLESCRIPT 2>/dev/null || true
tell application "Finder"
    tell disk "$DMG_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 640, 440}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 96
        set position of item "$DMG_NAME.app" of container window to {160, 200}
        set position of item "Applications" of container window to {380, 200}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
APPLESCRIPT

# 7. Compress DMG
echo "[7/8] Compressing DMG..."
hdiutil convert "$RW_DMG" -format UDZO -imagekey zlib-level=9 \
    -o "$DMG_PATH"
rm -f "$RW_DMG"

# 8. Sign + notarize DMG (if notarize mode)
if [ "$NOTARIZE_MODE" = "notarize" ]; then
    echo "[8/8] Signing + notarizing DMG..."
    codesign --force --sign "$SIGN_IDENTITY" --timestamp "$DMG_PATH"
    xcrun notarytool submit "$DMG_PATH" \
        --apple-id "$NOTARIZE_APPLE_ID" \
        --password "$NOTARIZE_APP_PASSWORD" \
        --team-id "$NOTARIZE_TEAM_ID" \
        --wait --timeout 30m
    xcrun stapler staple "$DMG_PATH"
    echo "  DMG notarized and stapled"
else
    echo "[8/8] Skipping DMG notarization (adhoc mode)"
fi

# Cleanup
rm -rf "$STAGING" "$APP_ZIP"

SIZE=$(du -h "$DMG_PATH" | cut -f1)
echo ""
echo "=== Build complete ==="
echo "DMG: $DMG_PATH ($SIZE)"
echo "Mode: $NOTARIZE_MODE"
