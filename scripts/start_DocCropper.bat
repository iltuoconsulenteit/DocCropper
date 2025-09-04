@echo off
setlocal EnableDelayedExpansion

:: Directory where this script resides
set "SCRIPT_DIR=%~dp0"

:: Locate DocCropper's main.py either here or one level up
if exist "!SCRIPT_DIR!main.py" (
    set "APP_DIR=!SCRIPT_DIR!"
) else (
    set "APP_DIR=!SCRIPT_DIR!\.."
)

cd /d "!APP_DIR!"

rem Copy default environment files if missing
if not exist "!APP_DIR!\.env" if exist "!APP_DIR!\.env.example" copy "!APP_DIR!\.env.example" "!APP_DIR!\.env" >nul 2>&1
if not exist "!APP_DIR!\env\auth.env" (
    if exist "!APP_DIR!\env\auth.env.example" (
        if not exist "!APP_DIR!\env" mkdir "!APP_DIR!\env"
        copy "!APP_DIR!\env\auth.env.example" "!APP_DIR!\env\auth.env" >nul 2>&1
    )
)

if not exist main.py (
    echo [ERROR] main.py not found in !APP_DIR!
    pause
    exit /b 1
)

:: Log file in temp directory
set "LOG_FILE=%TEMP%\DocCropper_start.log"
echo [INFO] Avvio DocCropper > "!LOG_FILE!"
echo [INFO] Directory script: !SCRIPT_DIR! >> "!LOG_FILE!"
echo [INFO] Directory app: !APP_DIR! >> "!LOG_FILE!"

:: Default port
set "PORT=8765"
if exist settings.json (
    for /f "delims=" %%p in ('python -c "import json,sys;print(json.load(open('settings.json')).get('port', 8765))" 2^>nul') do set "PORT=%%p"
)
echo [INFO] Porta usata: %PORT% >> "!LOG_FILE!"

:: Check if tray helper is running using PID file
set "TRAY_PID_FILE=%TEMP%\doccropper_tray.pid"
set "TRAY_RUNNING=0"
if exist "!TRAY_PID_FILE!" (
    for /f %%p in (!TRAY_PID_FILE!) do set "TRAY_PID=%%p"
    tasklist /FI "PID eq !TRAY_PID!" | find "!TRAY_PID!" >nul && set "TRAY_RUNNING=1"
    if "!TRAY_RUNNING!"=="0" del /f /q "!TRAY_PID_FILE!" >nul 2>&1
)

:: Check if server already running using PID file
set "PID_FILE=%TEMP%\doccropper.pid"
set "SERVER_RUNNING=0"
if exist "!PID_FILE!" (
    for /f %%p in (!PID_FILE!) do set "PID=%%p"
    tasklist /FI "PID eq !PID!" | find "!PID!" >nul && set "SERVER_RUNNING=1"
)

if "!TRAY_RUNNING!"=="0" (
    echo [INFO] Avvio tray helper >> "!LOG_FILE!"
    start "" cmd /c "set DOCROPPER_PROC=DocCropperTray && pythonw doccropper_tray.pyw" >> "!LOG_FILE!" 2>&1
    timeout /t 2 >nul
)

rem refresh server status after possible tray launch
set "SERVER_RUNNING=0"
if exist "!PID_FILE!" (
    for /f %%p in (!PID_FILE!) do set "PID=%%p"
    tasklist /FI "PID eq !PID!" | find "!PID!" >nul && set "SERVER_RUNNING=1"
)

set "OPEN_URL=%DOCROPPER_OPEN_URL%"
if "%OPEN_URL%"=="" set "OPEN_URL=http://localhost:%PORT%/"

if "!SERVER_RUNNING!"=="1" (
    echo [INFO] DocCropper gia in esecuzione con PID !PID! >> "!LOG_FILE!"
    start "" "%OPEN_URL%"
    goto finish
)

:: Ensure virtual environment
if not exist venv (
    echo [INFO] Creo ambiente virtuale venv... >> "!LOG_FILE!"
    python -m venv venv >> "!LOG_FILE!" 2>&1
)

:: Activate environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERRORE: attivazione ambiente virtuale fallita! >> "!LOG_FILE!"
    echo ❌ Attivazione ambiente virtuale fallita!
    pause
    exit /b
)

:: Install or update dependencies
if exist requirements.txt (
    echo [INFO] Aggiornamento dipendenze Python >> "!LOG_FILE!"
    python -m pip install --upgrade pip >> "!LOG_FILE!" 2>&1
    pip install -r requirements.txt >> "!LOG_FILE!" 2>&1
)

:: Stop any running instance
python main.py --stop >> "!LOG_FILE!" 2>&1

:: Launch application
echo [INFO] Avvio DocCropper sulla porta %PORT% >> "!LOG_FILE!"
start "" /b cmd /c "set DOCROPPER_PROC=DocCropper && python main.py --port %PORT%" >> "!LOG_FILE!" 2>&1
if "%DOCROPPER_TUNNEL%"=="true" (
    where cloudflared >nul 2>&1 && (
        echo Starting Cloudflare Tunnel... >> "!LOG_FILE!"
        start "tunnel" /b cloudflared tunnel --url http://localhost:%PORT% >> "!LOG_FILE!" 2>&1
    )
)

if errorlevel 1 (
    echo ❌ ERRORE: esecuzione fallita! Vedi log: %LOG_FILE%
) else (
    echo ✅ Avvio completato. Apri %OPEN_URL%
    start "" "%OPEN_URL%"
)

goto finish

:finish
echo [INFO] Script completato >> "!LOG_FILE!"
pause
endlocal
exit /b

:log
set MSG=%*
echo %MSG%
echo %MSG%>>"%LOG_FILE%"
exit /b
