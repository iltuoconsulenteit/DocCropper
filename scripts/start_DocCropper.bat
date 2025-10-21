@echo off
setlocal EnableDelayedExpansion

set "AUTO_MODE=0"
set "FORCED_DEPS_CHOICE="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--auto" (
    set "AUTO_MODE=1"
) else if /I "%~1"=="--deps=skip" (
    set "FORCED_DEPS_CHOICE=S"
) else if /I "%~1"=="--deps=s" (
    set "FORCED_DEPS_CHOICE=S"
) else if /I "%~1"=="--deps=missing" (
    set "FORCED_DEPS_CHOICE=M"
) else if /I "%~1"=="--deps=m" (
    set "FORCED_DEPS_CHOICE=M"
) else if /I "%~1"=="--deps=all" (
    set "FORCED_DEPS_CHOICE=T"
) else if /I "%~1"=="--deps=t" (
    set "FORCED_DEPS_CHOICE=T"
)
shift
goto parse_args

:args_done

if defined DOCROPPER_DEP_CHOICE (
    if not defined FORCED_DEPS_CHOICE set "FORCED_DEPS_CHOICE=%DOCROPPER_DEP_CHOICE%"
)

:: Directory where this script resides
set "SCRIPT_DIR=%~dp0"

:: Locate DocCropper's main.py either here or one level up
if exist "!SCRIPT_DIR!main.py" (
    set "APP_DIR=!SCRIPT_DIR!"
) else (
    set "APP_DIR=!SCRIPT_DIR!\.."
)

cd /d "!APP_DIR!"

:: Load Python path info recorded by installer
if exist "!APP_DIR!\env\python_path.env" (
    for /f "usebackq tokens=1* delims==" %%A in ("!APP_DIR!\env\python_path.env") do (
        set "%%A=%%B"
    )
)

if not defined PYTHON_CMD (
    set "PY_DIR=!APP_DIR!\python"
    set "PY=!PY_DIR!\python.exe"
    set "PYW=!PY_DIR!\pythonw.exe"
) else (
    set "PY=%PYTHON_CMD%"
    set "PYW=%PYTHONW_CMD%"
    if not defined PY_DIR set "PY_DIR=%APP_DIR%\python"
)

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
    for /f "delims=" %%p in ('"%PY%" -c "import json,sys;print(json.load(open('settings.json')).get('port', 8765))" 2^>nul') do set "PORT=%%p"
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
set "START_TRAY=0"
if "!TRAY_RUNNING!"=="0" (
    set "START_TRAY=1"
)

set "OPEN_URL=%DOCROPPER_OPEN_URL%"
if "%OPEN_URL%"=="" set "OPEN_URL=http://localhost:%PORT%/"

:: Use Python executables directly (no wrapper compilation)
set "DOC_EXE=!PY!"
set "TRAY_EXE=!PYW!"

if "!START_TRAY!"=="1" (
    echo [INFO] Avvio tray helper >> "!LOG_FILE!"
    set "DOCROPPER_PROC=DocCropperTray"
    start "" "!TRAY_EXE!" doccropper_tray.pyw >> "!LOG_FILE!" 2>&1
    set "DOCROPPER_PROC="
    timeout /t 2 >nul
)

rem refresh server status after possible tray launch or legacy runs
set "SERVER_RUNNING=0"
if exist "!PID_FILE!" (
    for /f %%p in (!PID_FILE!) do set "PID=%%p"
    tasklist /FI "PID eq !PID!" | find "!PID!" >nul && set "SERVER_RUNNING=1"
)
if "!SERVER_RUNNING!"=="0" (
    call :check_existing_server %PORT%
)
if "!SERVER_RUNNING!"=="1" (
    echo [INFO] DocCropper gia in esecuzione sulla porta %PORT% >> "!LOG_FILE!"
)

:: Install or update dependencies
if exist requirements.txt (
    echo [INFO] Aggiornamento dipendenze Python >> "!LOG_FILE!"
    for /f "delims=" %%h in ('certutil -hashfile requirements.txt MD5 ^| find /i /v "hash" ^| find /i /v "CertUtil"') do set "REQ_HASH=%%h"
    set "OLD_HASH_FILE=!PY_DIR!\requirements.hash"
    call :resolve_hash_root
    set "HASH_FILE=!HASH_ROOT!\requirements.hash"
    echo [INFO] Percorso file hash: !HASH_FILE! >> "!LOG_FILE!"
    set "NEED_INSTALL=1"
    set "DEFAULT_CHOICE=M"
    set "EXISTING_HASH="
    set "ENSURE_SCRIPT=!APP_DIR!\scripts\ensure_requirements.py"
    set "TEMP_REQ=%TEMP%\doccropper_requirements_install.txt"
    if exist "!TEMP_REQ!" del /f /q "!TEMP_REQ!" >nul 2>&1
    if exist "!HASH_FILE!" (
        set /p EXISTING_HASH=<"!HASH_FILE!"
    ) else if exist "!OLD_HASH_FILE!" (
        set /p EXISTING_HASH=<"!OLD_HASH_FILE!"
        copy /y "!OLD_HASH_FILE!" "!HASH_FILE!" >nul 2>&1
        if errorlevel 1 (
            echo [WARN] Impossibile migrare il file hash in !HASH_FILE! >> "!LOG_FILE!"
        ) else (
            echo [INFO] Migrazione hash dipendenze in !HASH_FILE! >> "!LOG_FILE!"
        )
    )
    if defined EXISTING_HASH (
        if /I "!EXISTING_HASH!"=="!REQ_HASH!" (
            set "NEED_INSTALL=0"
            set "DEFAULT_CHOICE=S"
        )
    )
    set "ENSURE_SUCCESS=0"
    set "ENSURE_MISSING_COUNT="
    if exist "!ENSURE_SCRIPT!" (
        "%PY%" "!ENSURE_SCRIPT!" requirements.txt --output "!TEMP_REQ!" >> "!LOG_FILE!" 2>&1
        if errorlevel 1 (
            if exist "!TEMP_REQ!" del /f /q "!TEMP_REQ!" >nul 2>&1
            echo [WARN] Analisi automatica delle dipendenze non riuscita >> "!LOG_FILE!"
        ) else (
            set "ENSURE_SUCCESS=1"
            set "ENSURE_MISSING_COUNT=0"
            if exist "!TEMP_REQ!" (
                for %%I in ("!TEMP_REQ!") do if %%~zI GTR 0 (
                    for /f %%C in ('find /c /v "" ^< "!TEMP_REQ!"') do set "ENSURE_MISSING_COUNT=%%C"
                )
            )
            if "!ENSURE_MISSING_COUNT!"=="" set "ENSURE_MISSING_COUNT=0"
            if "!ENSURE_MISSING_COUNT!"=="0" (
                echo [INFO] Analisi dipendenze: nessun pacchetto da installare >> "!LOG_FILE!"
                if "!NEED_INSTALL!"=="1" (
                    set "NEED_INSTALL=0"
                    set "DEFAULT_CHOICE=S"
                )
            ) else (
                echo [INFO] Pacchetti mancanti rilevati: !ENSURE_MISSING_COUNT! >> "!LOG_FILE!"
            )
        )
    )
    set "CHOICE="
    set "CHOICE_SOURCE="
    if defined FORCED_DEPS_CHOICE (
        set "CHOICE=!FORCED_DEPS_CHOICE!"
        set "CHOICE_SOURCE=forced"
    )
    if not defined CHOICE if "!AUTO_MODE!"=="1" (
        if "!NEED_INSTALL!"=="0" (
            set "CHOICE=S"
            set "CHOICE_SOURCE=auto-skip"
        ) else (
            set "CHOICE=M"
            set "CHOICE_SOURCE=auto-missing"
        )
    )
    if not defined CHOICE (
        set /p CHOICE=Gestione dipendenze Python - (S^)alta, (M^)ancanti, (T^)utte [!DEFAULT_CHOICE!]:
        if "!CHOICE!"=="" set "CHOICE=!DEFAULT_CHOICE!"
        set "CHOICE_SOURCE=prompt"
    )
    set "CHOICE=!CHOICE:~0,1!"
    if /I "!CHOICE_SOURCE!"=="forced" (
        echo [INFO] Gestione dipendenze forzata: !CHOICE! >> "!LOG_FILE!"
    ) else if /I "!CHOICE_SOURCE!"=="auto-skip" (
        echo [INFO] Modalita automatica: requisiti invariati, salto installazione >> "!LOG_FILE!"
    ) else if /I "!CHOICE_SOURCE!"=="auto-missing" (
        echo [INFO] Modalita automatica: aggiorno solo pacchetti mancanti/obsoleti >> "!LOG_FILE!"
    )
    set "DEPENDENCIES_OK=0"
    set "PIP_PREPARED=0"
    if /I "!CHOICE!"=="S" (
        if "!NEED_INSTALL!"=="0" (
            echo [INFO] Requisiti Python gia aggiornati >> "!LOG_FILE!"
            set "DEPENDENCIES_OK=1"
        ) else (
            echo [INFO] Installazione dipendenze saltata >> "!LOG_FILE!"
        )
    ) else if /I "!CHOICE!"=="T" (
        call :prepare_pip
        "%PY%" -m pip install --upgrade --force-reinstall -r requirements.txt >> "!LOG_FILE!" 2>&1
        if errorlevel 1 (
            echo [WARN] Reinstallazione completa dei pacchetti fallita >> "!LOG_FILE!"
        ) else (
            set "DEPENDENCIES_OK=1"
        )
    ) else (
        if not exist "!ENSURE_SCRIPT!" (
            call :prepare_pip
            "%PY%" -m pip install -r requirements.txt >> "!LOG_FILE!" 2>&1
            if errorlevel 1 (
                echo [WARN] Aggiornamento pacchetti fallito >> "!LOG_FILE!"
            ) else (
                set "DEPENDENCIES_OK=1"
            )
        ) else (
            if "!ENSURE_SUCCESS!"=="1" (
                set "NEEDS_TARGETED=0"
                if exist "!TEMP_REQ!" (
                    for %%I in ("!TEMP_REQ!") do if %%~zI GTR 0 set "NEEDS_TARGETED=1"
                )
            ) else (
                call :prepare_pip
                "%PY%" "!ENSURE_SCRIPT!" requirements.txt --output "!TEMP_REQ!" >> "!LOG_FILE!" 2>&1
                if errorlevel 1 (
                    echo [WARN] Controllo dipendenze fallito, eseguo installazione completa >> "!LOG_FILE!"
                    call :prepare_pip
                    "%PY%" -m pip install -r requirements.txt >> "!LOG_FILE!" 2>&1
                    if errorlevel 1 (
                        echo [WARN] Aggiornamento pacchetti fallito >> "!LOG_FILE!"
                    ) else (
                        set "DEPENDENCIES_OK=1"
                    )
                    if exist "!TEMP_REQ!" del /f /q "!TEMP_REQ!" >nul 2>&1
                    goto deps_done
                ) else (
                    set "NEEDS_TARGETED=0"
                    if exist "!TEMP_REQ!" (
                        for %%I in ("!TEMP_REQ!") do if %%~zI GTR 0 set "NEEDS_TARGETED=1"
                    )
                    set "ENSURE_SUCCESS=1"
                )
            )
            if "!NEEDS_TARGETED!"=="1" (
                call :prepare_pip
                "%PY%" -m pip install -r "!TEMP_REQ!" >> "!LOG_FILE!" 2>&1
                if errorlevel 1 (
                    echo [WARN] Aggiornamento mirato fallito, eseguo installazione completa >> "!LOG_FILE!"
                    call :prepare_pip
                    "%PY%" -m pip install -r requirements.txt >> "!LOG_FILE!" 2>&1
                    if errorlevel 1 (
                        echo [WARN] Aggiornamento pacchetti fallito >> "!LOG_FILE!"
                    ) else (
                        set "DEPENDENCIES_OK=1"
                    )
                ) else (
                    set "DEPENDENCIES_OK=1"
                )
            ) else (
                echo [INFO] Tutti i pacchetti richiesti sono gia installati >> "!LOG_FILE!"
                set "DEPENDENCIES_OK=1"
            )
        )
        :deps_done
        if exist "!TEMP_REQ!" del /f /q "!TEMP_REQ!" >nul 2>&1
    )
    if "!DEPENDENCIES_OK!"=="1" (
        >"!HASH_FILE!" echo(!REQ_HASH!
        if not exist "!HASH_FILE!" (
            echo [WARN] Impossibile salvare l'hash in !HASH_FILE! >> "!LOG_FILE!"
        )
    )
)

:: Capture version information for the launched process
set "DOCROPPER_VERSION="
set "DOCROPPER_VERSION_DATE="
if exist "!APP_DIR!\scripts\version_info.py" (
    for /f "tokens=1* delims==" %%A in ('"%PY%" "!APP_DIR!\scripts\version_info.py" --print-env 2^>nul') do (
        if /I "%%A"=="DOCROPPER_VERSION" set "DOCROPPER_VERSION=%%B"
        if /I "%%A"=="DOCROPPER_VERSION_DATE" set "DOCROPPER_VERSION_DATE=%%B"
    )
    if defined DOCROPPER_VERSION (
        set "VERSION_ENV_DIR=!APP_DIR!\env"
        if not exist "!VERSION_ENV_DIR!" mkdir "!VERSION_ENV_DIR!" >nul 2>&1
        set "VERSION_ENV_FILE=!VERSION_ENV_DIR!\version.env"
        >"!VERSION_ENV_FILE!" echo DOCROPPER_VERSION=!DOCROPPER_VERSION!
        if defined DOCROPPER_VERSION_DATE (
            >>"!VERSION_ENV_FILE!" echo DOCROPPER_VERSION_DATE=!DOCROPPER_VERSION_DATE!
        )
    )
)

:: Stop any running instance
"%PY%" main.py --stop >> "!LOG_FILE!" 2>&1

call :check_existing_server %PORT%
if "!SERVER_RUNNING!"=="1" (
    echo [WARN] DocCropper risulta ancora attivo sulla porta %PORT%, salto il nuovo avvio >> "!LOG_FILE!"
    echo ⚠️ DocCropper risulta gia in esecuzione sulla porta %PORT%. Chiudi l'istanza precedente e riprova.
    start "" "%OPEN_URL%"
    goto finish
)

:: Launch application
echo [INFO] Avvio DocCropper sulla porta %PORT% >> "!LOG_FILE!"
set "LAUNCH_HELPER=!APP_DIR!\scripts\launch_app.py"
if not exist "!LAUNCH_HELPER!" (
    echo [ERROR] launch_app.py non trovato in !APP_DIR!\scripts >> "!LOG_FILE!"
    echo ❌ ERRORE: impossibile avviare DocCropper. >> "!LOG_FILE!"
    echo ❌ ERRORE: launch_app.py mancante, verifica l'installazione.
    goto finish
)
"%PY%" "!LAUNCH_HELPER!" --python "!DOC_EXE!" --main "!APP_DIR!\main.py" --port %PORT% --log "!LOG_FILE!" --pid-file "!PID_FILE!" --cwd "!APP_DIR!" >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
    echo [ERROR] Avvio DocCropper fallito, controlla il log: %LOG_FILE% >> "!LOG_FILE!"
    echo ❌ ERRORE: avvio fallito! Vedi log: %LOG_FILE%
    goto finish
)

set "SERVER_RUNNING=0"
set "WAIT_ITER=0"
:wait_for_pid
if exist "!PID_FILE!" (
    for /f %%p in (!PID_FILE!) do set "PID=%%p"
    set "SERVER_RUNNING=1"
    goto server_status_known
)
set /a WAIT_ITER+=1
if "!WAIT_ITER!" GEQ "15" goto server_status_known
ping -n 2 127.0.0.1 >nul
goto wait_for_pid

:server_status_known
if "!SERVER_RUNNING!"=="0" (
    echo [ERROR] Nessun PID rilevato, controlla il log: %LOG_FILE% >> "!LOG_FILE!"
    echo ❌ ERRORE: esecuzione fallita! Vedi log: %LOG_FILE%
    goto finish
)

if "%DOCROPPER_TUNNEL%"=="true" (
    where cloudflared >nul 2>&1 && (
        echo Starting Cloudflare Tunnel... >> "!LOG_FILE!"
        start "tunnel" /b cloudflared tunnel --url http://localhost:%PORT% >> "!LOG_FILE!" 2>&1
    )
)

echo [INFO] DocCropper avviato con PID !PID! >> "!LOG_FILE!"
echo ✅ Avvio completato. Apri %OPEN_URL%
start "" "%OPEN_URL%"

goto finish

:finish
echo [INFO] Script completato >> "!LOG_FILE!"
pause
endlocal
exit /b

:resolve_hash_root
set "HASH_ROOT="
if defined DOCROPPER_HASH_DIR if not "%DOCROPPER_HASH_DIR%"=="" set "HASH_ROOT=%DOCROPPER_HASH_DIR%"
if not defined HASH_ROOT if defined LOCALAPPDATA set "HASH_ROOT=%LOCALAPPDATA%\DocCropper"
if not defined HASH_ROOT if defined APPDATA set "HASH_ROOT=%APPDATA%\DocCropper"
if not defined HASH_ROOT if defined USERPROFILE set "HASH_ROOT=%USERPROFILE%\DocCropper"
if not defined HASH_ROOT if defined PROGRAMDATA set "HASH_ROOT=%PROGRAMDATA%\DocCropper"
if not defined HASH_ROOT if defined TEMP set "HASH_ROOT=%TEMP%\DocCropper"
if not defined HASH_ROOT set "HASH_ROOT=%APP_DIR%\temp\DocCropper"
if "!HASH_ROOT!"=="" set "HASH_ROOT=%TEMP%\DocCropper"
if not exist "!HASH_ROOT!" (
    mkdir "!HASH_ROOT!" >nul 2>&1
    if errorlevel 1 (
        if defined TEMP (
            set "HASH_ROOT=%TEMP%\DocCropper"
            if not exist "!HASH_ROOT!" mkdir "!HASH_ROOT!" >nul 2>&1
        )
    )
)
if not exist "!HASH_ROOT!" set "HASH_ROOT=%TEMP%"
exit /b 0

:check_existing_server
set "SERVER_RUNNING=0"
set "_CHECK_PORT=%~1"
if "!_CHECK_PORT!"=="" set "_CHECK_PORT=%PORT%"
"%PY%" -c "import sys, urllib.request;\nport = int(sys.argv[1]);\nurl = f'http://127.0.0.1:{port}/license/status';\ntry:\n    with urllib.request.urlopen(url, timeout=1) as resp:\n        sys.exit(0 if resp.status == 200 else 1)\nexcept Exception:\n    sys.exit(1)" "!_CHECK_PORT!" >nul 2>&1
if errorlevel 1 (
    set "SERVER_RUNNING=0"
) else (
    set "SERVER_RUNNING=1"
)
exit /b 0

:prepare_pip
if "%PIP_PREPARED%"=="1" exit /b 0
"%PY%" -m pip install --upgrade pip >> "!LOG_FILE!" 2>&1
set "PIP_PREPARED=1"
exit /b 0

:log
set MSG=%*
echo %MSG%
echo %MSG%>>"%LOG_FILE%"
exit /b
