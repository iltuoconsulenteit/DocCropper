@echo off
setlocal EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
if exist "!SCRIPT_DIR!main.py" (
    set "APP_DIR=!SCRIPT_DIR!"
) else (
    set "APP_DIR=!SCRIPT_DIR!..\"
)
cd /d "!APP_DIR!"
if defined TEMP (
    set "LOG_FILE=%TEMP%\DocCropper_start.log"
) else (
    set "LOG_FILE=!APP_DIR!doccropper.log"
)
call :log "DocCropper start script"

set "PORT=8000"
if exist settings.json (
    for /f "delims=" %%p in ('python -c "import json,sys;print(json.load(open(^"settings.json^")).get(^"port^",8000))" 2^>nul') do set PORT=%%p
)

if not exist venv (
    call :log "Creating virtual environment..."
    python -m venv venv >>"%LOG_FILE%" 2>&1 || (
        call :log "Failed to create virtual environment"
        exit /b 1
    )
)

call :log "Activating virtual environment"
call venv\Scripts\activate.bat

call :log "Installing dependencies..."
pip install --upgrade pip >>"%LOG_FILE%" 2>&1
pip install -r requirements.txt >>"%LOG_FILE%" 2>&1

call :log "Launching DocCropper on port %PORT%"
set "PYW=%APP_DIR%venv\Scripts\pythonw.exe"
set "PYC=%APP_DIR%venv\Scripts\python.exe"
if exist "%PYW%" (
    start "" "%PYW%" main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
) else (
    start "" "%PYC%" main.py --host 0.0.0.0 --port %PORT% >>"%LOG_FILE%" 2>&1
)

timeout /t 2 >nul
start "" http://127.0.0.1:%PORT%/

call :log "Start script completed"
endlocal
exit /b

:log
set MSG=%*
echo %MSG%
echo %MSG%>>"%LOG_FILE%"
exit /b
