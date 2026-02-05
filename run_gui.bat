@echo off
title Hindi Shadow Trainer GUI
chcp 65001 >nul

cls
echo ========================================
echo   Hindi Shadow Trainer - GUI
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

:: Create venv
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

:: Activate
call venv\Scripts\activate.bat

:: Install dependencies
echo [INFO] Checking/Installing dependencies (this may take a few minutes on first run)...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection.
    pause
    exit /b 1
)

echo [OK] All dependencies ready
echo.
echo ========================================
echo   Starting Application...
echo ========================================
echo.

:: Run GUI
python gui.py

pause
