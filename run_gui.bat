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
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

:: Create venv
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

:: Activate
call venv\Scripts\activate.bat

:: Install flet if needed
python -c "import flet" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Flet...
    pip install flet
)

echo [OK] Starting GUI...
echo.

:: Run GUI
python gui.py

pause
