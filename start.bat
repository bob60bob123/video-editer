@echo off
chcp 65001 >nul
title Video Editor

echo ========================================
echo   Video Editor v1.0
echo ========================================
echo.

set PYTHON=C:\Users\HUAWEI\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON%" (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

"%PYTHON%" -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt5...
    "%PYTHON%" -m pip install PyQt5
    if errorlevel 1 (
        echo [ERROR] PyQt5 install failed
        pause
        exit /b 1
    )
)

echo [START] Launching Video Editor...
cd /d "%~dp0"
"%PYTHON%" main.py

pause
