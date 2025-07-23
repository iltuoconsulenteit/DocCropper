@echo off
setlocal
set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%main.py" (
    set "APP_DIR=%SCRIPT_DIR%"
) else (
    set "APP_DIR=%SCRIPT_DIR%..\"
)
cd /d "%APP_DIR%"
set "LOG_FILE=%APP_DIR%doccropper.log"

for /f "delims=" %%p in ('python -c "import json,sys;\
try: d=json.load(open('settings.json')); print(d.get('port',8000))\
except Exception: print(8000)"') do set PORT=%%p

if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip >>"%LOG_FILE%" 2>&1
pip install -r requirements.txt >>"%LOG_FILE%" 2>&1

echo Starting DocCropper on port %PORT%...
where pythonw >nul 2>&1 && (
    pythonw main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
) || (
    python main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
)
endlocal
