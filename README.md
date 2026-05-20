# RIGEL Business v4.1.0 — PyQt6 Build Guide
**Stella Lumen (Pty) Ltd**
Contact: info@stella-lumen.com | 031 944 4635
Website: www.stella-lumen.com | Pricing: R350 ZAR

---

## File Overview

```
rigel_pyqt6/
  rigel_core.py           Complete application (1,955 lines, 30 classes)
  assets_b64.py           Real logo (PNG) + product box (JPEG) embedded as base64
  rigel_trial_win.py      Windows trial entry point  (BUILD_MODE=TRIAL)
  rigel_full_win.py       Windows full entry point   (BUILD_MODE=FULL)
  rigel_trial_mac.py      macOS trial entry point    (BUILD_MODE=TRIAL)
  rigel_full_mac.py       macOS full entry point     (BUILD_MODE=FULL)
  rigel_trial_win.spec    PyInstaller spec: RIGEL_Business_Trial.exe
  rigel_full_win.spec     PyInstaller spec: RIGEL_Business_Full.exe
  rigel_trial_mac.spec    PyInstaller spec: RIGEL_Business_Trial.app/.dmg
  rigel_full_mac.spec     PyInstaller spec: RIGEL_Business_Full.app/.dmg
  build_windows.bat       One-click Windows build (both .exe files)
  build_macos.sh          One-click macOS build (both .dmg files)
  entitlements.plist      macOS Hardened Runtime entitlements
  admin_keygen.py         PRIVATE: generate customer license keys
  requirements.txt        pip dependencies (PyQt6 only)
```

---

## STEP 0 — Change the Secret Salt (MANDATORY before any build)

Open rigel_core.py, find line ~65:

    SECRET_SALT = "StellLumen#Rigel2025_PROD_CHANGEME"

Replace with your own private string (20+ chars, mixed symbols).
Also update admin_keygen.py to match the same value.
Store it in a password manager. Never commit to any public repo.

---

## Windows Build (.exe files)

### Prerequisites
  Python 3.11 or 3.12 from python.org — tick "Add to PATH" during install
  Run from inside the rigel_pyqt6 folder

### One-command build
    build_windows.bat

### Manual build
    pip install PyQt6 pyinstaller
    pyinstaller rigel_trial_win.spec --clean --noconfirm
    pyinstaller rigel_full_win.spec  --clean --noconfirm

### Output
    dist\RIGEL_Business_Trial.exe    (30-day trial)
    dist\RIGEL_Business_Full.exe     (requires license key)

### Code signing (removes SmartScreen warning)
    signtool sign /f cert.pfx /p %CERT_PASSWORD% ^
        /tr http://timestamp.comodoca.com /td sha256 ^
        "dist\RIGEL_Business_Trial.exe"

Without signing: users see SmartScreen warning.
Click "More info" then "Run anyway" (documented in your BETA_WARNING.txt).
Purchase Comodo/Sectigo EV certificate ~R3,500/year to eliminate this.

---

## macOS Build (.dmg files)

### Prerequisites
    brew install python@3.12
    xcode-select --install
    brew install create-dmg

### One-command build
    chmod +x build_macos.sh && ./build_macos.sh

### Manual build
    pip3 install PyQt6 pyinstaller
    pyinstaller rigel_trial_mac.spec --clean --noconfirm
    create-dmg --volname "RIGEL Business (Trial)" \
      --window-size 660 400 --icon-size 100 \
      --icon "RIGEL_Business_Trial.app" 175 185 \
      --app-drop-link 475 185 \
      dist/RIGEL_Business_Trial.dmg dist/RIGEL_Business_Trial.app

### hdiutil fallback (no create-dmg)
    hdiutil create -volname "RIGEL Business Trial" \
      -srcfolder dist/RIGEL_Business_Trial.app \
      -ov -format UDZO dist/RIGEL_Business_Trial.dmg

### macOS code signing + notarisation
    codesign --deep --force --options runtime \
        --sign "Developer ID Application: Stella Lumen (XXXXXXXXXX)" \
        --entitlements entitlements.plist \
        dist/RIGEL_Business_Full.app

    xcrun notarytool submit dist/RIGEL_Business_Full.dmg \
        --apple-id "you@email.com" --team-id "XXXXXXXXXX" \
        --password "xxxx-xxxx-xxxx-xxxx" --wait

    xcrun stapler staple dist/RIGEL_Business_Full.dmg

Requires Apple Developer Program ~R2,100/year.
Without signing: users right-click the app and choose Open on first launch.

---

## Build Matrix

  Output file                  Build machine  Command
  RIGEL_Business_Trial.exe     Windows        pyinstaller rigel_trial_win.spec
  RIGEL_Business_Full.exe      Windows        pyinstaller rigel_full_win.spec
  RIGEL_Business_Trial.dmg     macOS          pyinstaller rigel_trial_mac.spec + DMG wrap
  RIGEL_Business_Full.dmg      macOS          pyinstaller rigel_full_mac.spec  + DMG wrap

PyInstaller cannot cross-compile. .exe must be built on Windows. .dmg on macOS.

---

## Deploying to Your Website

### Vercel (current live site)
    cp dist/RIGEL_Business_*.{exe,dmg} your-site/public/assets/downloads/
    git add public/assets/downloads/
    git commit -m "RIGEL Business v4.1.0 installers"
    git push
    (Vercel auto-deploys in ~60 seconds)

Check Vercel 100MB limit per file. Use GitHub Releases if exceeded.

### cPanel (legacy beta path: /downloads/rigel-business/)
Upload files, update index.html download link.
Keep _htaccess, BETA_WARNING.txt, ReleaseNotes.txt in same folder.
Your existing _htaccess already bypasses WordPress for file serving.

### MIME types (add to _htaccess if needed)
    AddType application/octet-stream .exe .dmg

---

## License Key Workflow

1. Customer launches trial, opens activation dialog, copies their Machine ID
2. Customer purchases at www.stella-lumen.com and sends you the Machine ID
3. On your private admin machine run: python3 admin_keygen.py
4. Enter their Machine ID, get RIGEL-XXXX-XXXX-XXXX-XXXX, email it
5. Customer enters key + company name, app activates permanently

License file locations:
  Windows: %APPDATA%\RIGELBusiness\.rigel_license
  macOS:   ~/Library/Application Support/RIGELBusiness/.rigel_license

---

## Colour Reference (pixel/XML confirmed from xlsb binary)

  App background:        #5A6061   (pixel: image1.png)
  Header bars:           #4A5254   (pixel: image1.png)
  Sidebar:               #363F41   (drawing analysis)
  Primary button:        #021B0D   (pixel: button centre)
  INDEX nav buttons:     #003300   (drawing3.xml solidFill)
  Action buttons:        #00B050   (drawings XML)
  POST TRANSACTION:      #00B0F0   (drawings XML)
  Edit/secondary:        #5F6B6B   (drawings XML)
  Logout danger:         #821E2B   (pixel: logout button)
  Logo green:            #47BB6E   (PDF vector)
  Logo teal:             #3DAD9B   (PDF vector)
  Logo grey wing:        #939598   (PDF pixel)
  RIGEL text:            #42B96A   (JPEG pixel)
  Headline dark green:   #142E21   (pixel: headline area)

---

## Module Checklist

  Installer wizard:  Welcome, License, Progress (7 steps), Finish
  Splash screen:     Real logo + box, exact xlsb layout, 3 buttons
  Main dashboard:    KPI cards, Performance chart, Working Capital chart
  Accounting:        Trial Balance, GL, VAT, Performance, Balance Sheet
  Operations:        Cash Book, Customers, Suppliers, Employees, Assets
  Finance:           Inventories, Loans, Investments, Directors, Projects
  HR:                Employees masterdata, Payslips (SARS 2025/2026)
  Licensing:         30-day trial, machine-bound full key, admin keygen
