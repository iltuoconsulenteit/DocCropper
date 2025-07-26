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

:: Stop any running instance
python main.py --stop >> "!LOG_FILE!" 2>&1

:: Launch application
echo [INFO] Avvio DocCropper sulla porta %PORT% >> "!LOG_FILE!"
start "" /b python main.py --port %PORT% >> "!LOG_FILE!" 2>&1
if "%DOCROPPER_TUNNEL%"=="true" (
    where cloudflared >nul 2>&1 && (
        echo Starting Cloudflare Tunnel... >> "!LOG_FILE!"
        start "tunnel" /b cloudflared tunnel --url http://localhost:%PORT% >> "!LOG_FILE!" 2>&1
    )
)

if errorlevel 1 (
    echo ❌ ERRORE: esecuzione fallita! Vedi log: %LOG_FILE%
) else (
    echo ✅ Avvio completato. Apri http://localhost:%PORT%
    start "" "http://localhost:%PORT%"
)

echo [INFO] Script completato >> "!LOG_FILE!"
pause
endlocal
exit /b

:log
set MSG=%*
echo %MSG%
echo %MSG%>>"%LOG_FILE%"
exit /b
