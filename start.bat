@echo off
chcp 65001 >nul
title 印地语影子跟读训练器 - Hindi Shadow Trainer
color 0A

echo.
echo ========================================
echo   印地语影子跟读训练器
echo   Hindi Shadow Trainer
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python安装！
    echo [Error] Python not detected!
    echo.
    echo 请先安装Python 3.8或更高版本
    echo Please install Python 3.8 or higher
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python已安装
python --version
echo.

:: 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败！
        pause
        exit /b 1
    )
    echo [OK] 虚拟环境创建成功
) else (
    echo [OK] 虚拟环境已存在
)

echo.

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查依赖是否安装
echo [信息] 检查依赖...
python -c "import whisper" >nul 2>&1
if errorlevel 1 (
    echo [信息] 首次运行，正在安装依赖（这可能需要几分钟）...
    echo [Info] First run, installing dependencies (this may take a few minutes)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖失败！
        echo [Error] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
) else (
    echo [OK] 依赖已安装
)

echo.
echo ========================================
echo   启动程序...
echo   Starting application...
echo ========================================
echo.
timeout /t 1 /nobreak >nul

:: 运行程序
python main.py

:: 退出时暂停
echo.
echo ========================================
echo   程序已退出
echo   Application closed
pause
