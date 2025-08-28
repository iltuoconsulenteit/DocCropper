@echo off
setlocal
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\
cd /d %APP_DIR%

if exist venv\Scripts\python.exe (
    set "PY=venv\Scripts\python.exe"
) else (
set "PY=python"
)

set "LOG_FILE=%TEMP%\doccropper_stop.log"
call :log "Stop requested"

set "PID_FILE=%TEMP%\doccropper.pid"
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    for /f "delims=" %%c in ('wmic process where "ProcessId=%PID%" get CommandLine 2^>nul ^| findstr /I "DocCropper"') do set "IS_DOC=1"
    if defined IS_DOC (
        taskkill /PID %PID% >nul 2>&1
        timeout /T 1 >nul
        tasklist /FI "PID eq %PID%" | find "%PID%" >nul && taskkill /F /PID %PID% >nul 2>&1 && call :log "Force killed DocCropper PID %PID%" || call :log "Stopped DocCropper PID %PID%"
    ) else (
        call :log "PID %PID% does not belong to DocCropper"
    )
    del "%PID_FILE%" >nul 2>&1
)

set "TRAY_PID_FILE=%TEMP%\doccropper_tray.pid"
if exist "%TRAY_PID_FILE%" (
    for /f %%p in (%TRAY_PID_FILE%) do (
        for /f "delims=" %%c in ('wmic process where "ProcessId=%%p" get CommandLine 2^>nul ^| findstr /I "doccropper_tray"') do set "IS_TRAY=1"
        if defined IS_TRAY (
            taskkill /PID %%p >nul 2>&1
            timeout /T 1 >nul
            tasklist /FI "PID eq %%p" | find "%%p" >nul && taskkill /F /PID %%p >nul 2>&1 && call :log "Force killed tray helper PID %%p" || call :log "Stopped tray helper PID %%p"
        ) else (
            call :log "PID %%p does not belong to tray helper"
        )
        set "IS_TRAY="
    )
    del "%TRAY_PID_FILE%" >nul 2>&1
)

REM Fallback if PID files missing: search processes by command line
if not exist "%PID_FILE%" (
    for /f %%p in ('wmic process where "CommandLine like '%%DocCropper%%main.py%%'" get ProcessId 2^>nul ^| findstr [0-9]') do (
        taskkill /PID %%p >nul 2>&1 & taskkill /F /PID %%p >nul 2>&1 & call :log "Stopped DocCropper PID %%p"
    )
)
if not exist "%TRAY_PID_FILE%" (
    for /f %%p in ('wmic process where "CommandLine like '%%doccropper_tray%%'" get ProcessId 2^>nul ^| findstr [0-9]') do (
        taskkill /PID %%p >nul 2>&1 & taskkill /F /PID %%p >nul 2>&1 & call :log "Stopped tray helper PID %%p"
    )
)
call :log "Stop script completed"
endlocal
exit /b

:log
echo %date% %time% %~1>>"%LOG_FILE%"
exit /b
