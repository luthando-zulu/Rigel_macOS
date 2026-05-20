@echo off
REM ============================================================
REM  RIGEL Business — Windows Build Script
REM  Produces: RIGEL_Business_Trial.exe + RIGEL_Business_Full.exe
REM  Run from the rigel_pyqt6\ folder as Administrator
REM ============================================================

echo.
echo  ============================================================
echo   RIGEL Business — Windows Build
echo   Stella Lumen (Pty) Ltd
echo  ============================================================
echo.

REM ── Step 1: Check Python ──────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause & exit /b 1
)
echo [OK] Python found.

REM ── Step 2: Install dependencies ─────────────────────────────
echo.
echo [1/4] Installing dependencies...
pip install PyQt6 pyinstaller --upgrade --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause & exit /b 1
)
echo [OK] Dependencies installed.

REM ── Step 3: Build Trial .exe ──────────────────────────────────
echo.
echo [2/4] Building TRIAL .exe...
pyinstaller rigel_trial_win.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] Trial build failed. Check output above.
    pause & exit /b 1
)
echo [OK] dist\RIGEL_Business_Trial.exe created.

REM ── Step 4: Build Full .exe ───────────────────────────────────
echo.
echo [3/4] Building FULL .exe...
pyinstaller rigel_full_win.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] Full build failed. Check output above.
    pause & exit /b 1
)
echo [OK] dist\RIGEL_Business_Full.exe created.

REM ── Step 5: Code signing (optional) ──────────────────────────
echo.
echo [4/4] Code signing (optional — skipped if cert.pfx not present)...
if exist cert.pfx (
    echo     Signing Trial .exe...
    signtool sign /f cert.pfx /p %CERT_PASSWORD% ^
        /tr http://timestamp.comodoca.com /td sha256 ^
        "dist\RIGEL_Business_Trial.exe"
    echo     Signing Full .exe...
    signtool sign /f cert.pfx /p %CERT_PASSWORD% ^
        /tr http://timestamp.comodoca.com /td sha256 ^
        "dist\RIGEL_Business_Full.exe"
    echo [OK] Code signing complete.
) else (
    echo [SKIP] cert.pfx not found — skipping code signing.
    echo        Users will see SmartScreen warning on first run.
    echo        Purchase Comodo/Sectigo EV cert to eliminate this.
)

echo.
echo  ============================================================
echo   BUILD COMPLETE
echo   Output files:
echo     dist\RIGEL_Business_Trial.exe
echo     dist\RIGEL_Business_Full.exe
echo  ============================================================
echo.
pause
