@echo off
echo ============================================================
echo Installing Tesseract OCR for Hybrid Detection
echo ============================================================
echo.

REM Check if chocolatey is installed
where choco >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Chocolatey found! Installing Tesseract...
    choco install tesseract -y
    echo.
    echo ============================================================
    echo Tesseract installed via Chocolatey
    echo ============================================================
) else (
    echo Chocolatey not found.
    echo.
    echo Please install Tesseract manually:
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Install to C:\Program Files\Tesseract-OCR
    echo 3. Add to PATH
    echo.
    echo Or install Chocolatey first:
    echo    https://chocolatey.org/install
    echo.
    pause
    exit /b 1
)

echo.
echo Installing Python package...
pip install pytesseract

echo.
echo ============================================================
echo Verifying installation...
echo ============================================================
tesseract --version

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Tesseract is installed and ready
    echo ============================================================
    echo.
    echo Next steps:
    echo 1. Test: python test_hybrid_detection.py screenshots\2026-01-30_02-25-35\B_ss_000.png
    echo 2. Run monitoring: Send /check from phone
    echo.
) else (
    echo.
    echo ============================================================
    echo WARNING: Tesseract may not be in PATH
    echo ============================================================
    echo Please add C:\Program Files\Tesseract-OCR to your PATH
    echo.
)

pause
