@echo off
title Hindi Shadow Trainer - YouTube Learning
chcp 65001 >nul

cls
echo ========================================
echo   YouTube Learning Mode
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

:: Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Check FFmpeg and install if needed
echo [INFO] Checking FFmpeg...
python -c "import subprocess; subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] FFmpeg not found, installing automatically...
    python install_ffmpeg.py
    if errorlevel 1 (
        echo [ERROR] FFmpeg installation failed!
        pause
        exit /b 1
    )
)
echo [OK] FFmpeg is ready
echo.

:: Run YouTube CLI with arguments
echo ========================================
echo   Starting YouTube Learning Tool
echo ========================================
echo.

python youtube_cli.py %*

pause
