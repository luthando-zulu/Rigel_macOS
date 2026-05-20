#!/usr/bin/env bash
# ============================================================
#  RIGEL Business — macOS Build Script
#  Produces: RIGEL_Business_Trial.dmg + RIGEL_Business_Full.dmg
#  Run from the rigel_pyqt6/ folder on macOS 12+
# ============================================================
set -e

echo ""
echo " ============================================================"
echo "  RIGEL Business — macOS Build"
echo "  Stella Lumen (Pty) Ltd"
echo " ============================================================"
echo ""

# ── Colours for output ────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC}    $1"; }
fail() { echo -e "  ${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "  ${YELLOW}[INFO]${NC}  $1"; }

# ── Step 1: Check environment ─────────────────────────────────
echo "[1/6] Checking environment..."
python3 --version >/dev/null 2>&1 || fail "Python 3 not found. Install via Homebrew: brew install python@3.12"
ok "Python 3 found: $(python3 --version)"

xcode-select -p >/dev/null 2>&1 || fail "Xcode CLI tools missing. Run: xcode-select --install"
ok "Xcode CLI tools present"

# ── Step 2: Install dependencies ─────────────────────────────
echo ""
echo "[2/6] Installing Python dependencies..."
pip3 install PyQt6 pyinstaller --upgrade --quiet
ok "PyQt6 + PyInstaller installed"

# Check create-dmg
if command -v create-dmg >/dev/null 2>&1; then
    ok "create-dmg found: $(create-dmg --version 2>/dev/null | head -1)"
    USE_CREATE_DMG=1
else
    info "create-dmg not found. Using hdiutil fallback."
    info "For professional DMG layout: brew install create-dmg"
    USE_CREATE_DMG=0
fi

# ── Helper: wrap .app → .dmg ──────────────────────────────────
make_dmg() {
    local APP_NAME="$1"    # e.g. RIGEL_Business_Trial
    local DISPLAY="$2"     # e.g. "RIGEL Business (Trial)"
    local APP_PATH="dist/${APP_NAME}.app"
    local DMG_PATH="dist/${APP_NAME}.dmg"

    if [ ! -d "$APP_PATH" ]; then
        fail ".app bundle not found: $APP_PATH"
    fi

    rm -f "$DMG_PATH"

    if [ "$USE_CREATE_DMG" -eq 1 ]; then
        create-dmg \
            --volname "$DISPLAY" \
            --volicon "$APP_PATH/Contents/Resources/rigel.icns" 2>/dev/null || true \
            --window-pos 200 120 \
            --window-size 660 400 \
            --icon-size 100 \
            --icon "${APP_NAME}.app" 175 185 \
            --hide-extension "${APP_NAME}.app" \
            --app-drop-link 475 185 \
            --background-color "#595F60" \
            "$DMG_PATH" \
            "$APP_PATH"
    else
        # hdiutil fallback
        local STAGING=$(mktemp -d)
        cp -r "$APP_PATH" "$STAGING/"
        # Symlink to Applications
        ln -s /Applications "$STAGING/Applications" 2>/dev/null || true
        hdiutil create \
            -volname "$DISPLAY" \
            -srcfolder "$STAGING" \
            -ov -format UDZO \
            "$DMG_PATH"
        rm -rf "$STAGING"
    fi
    ok "${APP_NAME}.dmg created ($(du -sh "$DMG_PATH" | cut -f1))"
}

# ── Step 3: Build Trial .app ──────────────────────────────────
echo ""
echo "[3/6] Building TRIAL .app bundle..."
pyinstaller rigel_trial_mac.spec --clean --noconfirm
make_dmg "RIGEL_Business_Trial" "RIGEL Business (Trial)"

# ── Step 4: Build Full .app ───────────────────────────────────
echo ""
echo "[4/6] Building FULL .app bundle..."
pyinstaller rigel_full_mac.spec --clean --noconfirm
make_dmg "RIGEL_Business_Full" "RIGEL Business"

# ── Step 5: Code signing + notarisation (optional) ────────────
echo ""
echo "[5/6] Code signing + notarisation..."

IDENTITY="${APPLE_IDENTITY:-}"   # e.g. "Developer ID Application: Stella Lumen (XXXXXXXXXX)"
APPLE_ID="${APPLE_ID:-}"
TEAM_ID="${TEAM_ID:-}"
APP_PASSWORD="${APP_PASSWORD:-}" # App-specific password from appleid.apple.com

if [ -n "$IDENTITY" ] && [ -n "$APPLE_ID" ]; then
    for APP_NAME in RIGEL_Business_Trial RIGEL_Business_Full; do
        info "Signing dist/${APP_NAME}.app ..."
        codesign \
            --deep --force --options runtime \
            --sign "$IDENTITY" \
            --entitlements entitlements.plist \
            "dist/${APP_NAME}.app"

        info "Notarising dist/${APP_NAME}.dmg ..."
        xcrun notarytool submit "dist/${APP_NAME}.dmg" \
            --apple-id  "$APPLE_ID"      \
            --team-id   "$TEAM_ID"       \
            --password  "$APP_PASSWORD"  \
            --wait

        xcrun stapler staple "dist/${APP_NAME}.dmg"
        ok "${APP_NAME}.dmg notarised and stapled"
    done
else
    info "Skipping code signing — APPLE_IDENTITY / APPLE_ID not set."
    info "To sign, export these env vars before running this script:"
    info "  export APPLE_IDENTITY=\"Developer ID Application: Stella Lumen (XXXXXXXXXX)\""
    info "  export APPLE_ID=\"your@apple.id\""
    info "  export TEAM_ID=\"XXXXXXXXXX\""
    info "  export APP_PASSWORD=\"xxxx-xxxx-xxxx-xxxx\""
    info "Without signing, users must right-click → Open on first launch."
fi

# ── Step 6: Summary ───────────────────────────────────────────
echo ""
echo " ============================================================"
echo "  BUILD COMPLETE"
echo ""
echo "  Output files:"
ls -lh dist/*.dmg 2>/dev/null | awk '{print "    "$NF,"("$5")"}'
echo ""
echo "  Upload both .dmg files to:"
echo "    public/assets/downloads/ in your GitHub repo, OR"
echo "    cPanel File Manager → /downloads/rigel-business/"
echo " ============================================================"
echo ""
