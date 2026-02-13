@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo 🚀 ANZA OPTION ANALYSIS - ONE CLICK SETUP 🚀
echo ====================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found! Please install Python from python.org
    pause
    exit /b
)

:: Run launcher with auto-start
python launcher.py --auto

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ System stopped or error occurred.
    echo 💡 Check if you need to fill credentials in .env file
)

pause
