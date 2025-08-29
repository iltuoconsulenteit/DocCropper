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
    powershell -NoProfile -Command "try { Get-Process -Id %PID% -ErrorAction Stop | Where-Object { $_.Path -like '*DocCropper*' } | Stop-Process -Force } catch {}"
    del "%PID_FILE%" >nul 2>&1
)

set "TRAY_PID_FILE=%TEMP%\doccropper_tray.pid"
if exist "%TRAY_PID_FILE%" (
    set /p TPID=<"%TRAY_PID_FILE%"
    powershell -NoProfile -Command "try { Get-Process -Id %TPID% -ErrorAction Stop | Where-Object { $_.Path -like '*doccropper_tray*' } | Stop-Process -Force } catch {}"
    del "%TRAY_PID_FILE%" >nul 2>&1
)

REM Fallback if PID files missing: search processes by command line
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%%DocCropper%%main.py%%'\" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%%doccropper_tray%%'\" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
call :log "Stop script completed"
endlocal
exit /b

:log
echo %date% %time% %~1>>"%LOG_FILE%"
exit /b
