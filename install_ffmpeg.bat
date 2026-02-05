@echo off
title Installing FFmpeg
echo ========================================
echo   Installing FFmpeg for Windows
echo ========================================
echo.

:: Create directory
if not exist "ffmpeg" mkdir ffmpeg
cd ffmpeg

:: Download FFmpeg (essential build)
echo [INFO] Downloading FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

if not exist "ffmpeg.zip" (
    echo [ERROR] Download failed!
    echo.
    echo Please download manually from:
    echo https://www.gyan.dev/ffmpeg/builds/
    pause
    exit /b 1
)

:: Extract
echo [INFO] Extracting...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"

:: Find extracted folder
for /d %%i in (ffmpeg-*) do (
    echo [INFO] Found: %%i
    
    :: Copy to bin folder
    if not exist "bin" mkdir bin
    xcopy /s /y "%%i\bin\*.exe" "bin\" >nul
    
    :: Add to PATH
    echo [INFO] Adding to PATH...
    setx PATH "%PATH%;%~dp0bin" /M
    
    echo [OK] FFmpeg installed!
    echo.
    echo Please RESTART your terminal/command prompt
echo to use FFmpeg.
)

:: Cleanup
del /q ffmpeg.zip
rmdir /s /q ffmpeg-* 2>nul

echo.
pause
