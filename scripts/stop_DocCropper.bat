@echo off
setlocal
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\
cd /d %APP_DIR%

if exist "%APP_DIR%\env\python_path.env" (
    for /f "usebackq tokens=1* delims==" %%A in ("%APP_DIR%\env\python_path.env") do (
        set "%%A=%%B"
    )
)

if exist main.py (
    if defined PYTHON_CMD "%PYTHON_CMD%" main.py --stop >nul 2>&1
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

rem Fallback: terminate any Python or Pythonw process whose command line references DocCropper
for /f "tokens=2 delims==" %%p in ('wmic process where "(name='python.exe' or name='pythonw.exe') and CommandLine like '%%DocCropper%%'" get ProcessId /value ^| find "="') do (
    taskkill /F /T /PID %%p >nul 2>&1
)

rem Also try to stop precompiled wrappers if present
taskkill /F /T /IM DocCropper.exe >nul 2>&1
taskkill /F /T /IM DocCropperTray.exe >nul 2>&1

endlocal
