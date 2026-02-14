@echo off
SETLOCAL EnableDelayedExpansion

:: --- ANZA PRO ONE-CLICK LAUNCHER ---

:: Try python then python3
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PY=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PY=python3
    ) else (
        echo ❌ ERROR: Python not found. Please install it!
        pause
        exit /b
    )
)

:: Run the orchestrator
%PY% launcher.py --auto

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ System stopped.
)
pause
