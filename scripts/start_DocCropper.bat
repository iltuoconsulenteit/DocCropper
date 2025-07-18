@echo off
setlocal enabledelayedexpansion

rem Determine installation directory
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "SCRIPT_DIR=%~dp0"
    set "APP_DIR=%SCRIPT_DIR%..\"
)

if not exist "%APP_DIR%\main.py" (
    echo DocCropper not found at "%APP_DIR%".
    set /p APP_DIR=Enter the path to your DocCropper installation: 
)

if not exist "%APP_DIR%\main.py" (
    echo Could not locate DocCropper. Exiting.
    pause
    exit /b 1
)

cd /d "%APP_DIR%"

for /f "delims=" %%p in ('python -c "import json,sys;\
try: d=json.load(open('settings.json')); print(d.get('port',8000))\
except Exception: print(8000)"') do set PORT=%%p

if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip >nul
pip install -r requirements.txt >nul

echo Starting DocCropper on port %PORT%...
where pythonw >nul 2>&1 && (
    pythonw main.py --host 0.0.0.0 --port %PORT%
) || (
    python main.py --host 0.0.0.0 --port %PORT%
)
endlocal
