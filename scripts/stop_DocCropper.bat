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

set "PID_FILE=%TEMP%\doccropper.pid"
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    tasklist /FI "PID eq %PID%" | find "%PID%" >nul && taskkill /F /T /PID %PID% >nul 2>&1
    del "%PID_FILE%" >nul 2>&1
    echo Stopped DocCropper (PID %PID%)
)

set "TRAY_PID_FILE=%TEMP%\doccropper_tray.pid"
if exist "%TRAY_PID_FILE%" (
    for /f %%p in (%TRAY_PID_FILE%) do (
        tasklist /FI "PID eq %%p" | find "%%p" >nul && taskkill /F /T /PID %%p >nul 2>&1
    )
    del "%TRAY_PID_FILE%" >nul 2>&1
    echo Tray helper stopped
)

rem Fallback: terminate any Python process whose command line references DocCropper
for /f "tokens=2 delims==" %%p in ('wmic process where "name='python.exe' and CommandLine like '%%DocCropper%%'" get ProcessId /value ^| find "="') do (
    taskkill /F /T /PID %%p >nul 2>&1
)

endlocal
