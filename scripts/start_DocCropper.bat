@echo off
setlocal enabledelayedexpansion

set "LOG_FILE=%~dp0..\doccropper.log"

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
    echo Creating virtual environment...
    python -m venv venv || (
        echo Failed to create venv.
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat
echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Some packages failed to install. Continuing anyway...
)

echo Starting DocCropper on port %PORT%...
if exist "%LOG_FILE%" del "%LOG_FILE%"
where pythonw >nul 2>&1 && (
    start "DocCropper" pythonw -u main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
) || (
    start "DocCropper" python -u main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
)
echo Log written to %LOG_FILE%
endlocal
