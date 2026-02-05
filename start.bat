@echo off
chcp 65001 >nul
title Hindi Shadow Trainer

cls
echo ========================================
echo    Hindi Shadow Trainer
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

:: Create venv if not exists
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

:: Activate venv
call venv\Scripts\activate.bat

:: Check dependencies
echo [INFO] Checking dependencies...
python -c "import whisper" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies (first run)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Dependencies ready
echo.
echo ========================================
echo    Starting application...
echo ========================================
echo.

:: Run app
python main.py

:: Pause before close
echo.
echo ========================================
echo    Application closed
pause
