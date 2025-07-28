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

%PY% main.py --stop

set "TRAY_PID_FILE=%TEMP%\doccropper_tray.pid"
if exist "%TRAY_PID_FILE%" (
    for /f %%p in (%TRAY_PID_FILE%) do (
        tasklist /FI "PID eq %%p" | find "%%p" >nul && taskkill /F /PID %%p >nul 2>&1
    )
    del "%TRAY_PID_FILE%" >nul 2>&1
    echo Tray helper stopped
)
endlocal
