@echo off
title Hindi Shadow Trainer - Modern GUI
chcp 65001 >nul

cls
echo ========================================
echo   Hindi Shadow Trainer - Modern GUI
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Install dependencies if needed
echo [INFO] Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Tkinter not found! Please reinstall Python with Tk support.
    pause
    exit /b 1
)

echo [OK] Dependencies ready
echo.
echo ========================================
echo   Starting Modern GUI...
echo ========================================
echo.

:: Run GUI
python main_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] GUI failed to start!
    pause
)
