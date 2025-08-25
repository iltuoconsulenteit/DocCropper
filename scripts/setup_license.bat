@echo off
setlocal EnableDelayedExpansion

set "LOGFILE=temp\license_setup.log"
if not exist temp mkdir temp

if not "%~1"=="am_admin" (
    openfiles >nul 2>&1
    if errorlevel 1 (
        powershell -Command "Start-Process '%~f0' -ArgumentList 'am_admin' -Verb RunAs"
        exit /b
    )
)

:main
>>"%LOGFILE%" echo %date% %time% License setup started

:: Determine application directory (where main.py resides)
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%main.py" (
    set "APP_DIR=%SCRIPT_DIR%"
) else (
    set "APP_DIR=%SCRIPT_DIR%.."
)
cd /d "%APP_DIR%"

if not exist env mkdir env

rem ensure server and tray are stopped so files are writable
if exist scripts\stop_DocCropper.bat (
    >>"%LOGFILE%" echo %date% %time% Stopping running DocCropper
    call scripts\stop_DocCropper.bat >nul 2>&1
)

set /p LICENSE_KEY=Enter license key:
set /p LICENSE_NAME=Enter license name:
>>"%LOGFILE%" echo %date% %time% Key entered !LICENSE_KEY! for !LICENSE_NAME!

set "ENVFILE=env\developer.env"

(
    echo DOCROPPER_LICENSE_KEY=!LICENSE_KEY!
    echo DOCROPPER_LICENSE_NAME=!LICENSE_NAME!
    echo DOCROPPER_DEV_LICENSE=!LICENSE_KEY!
    echo DOCROPPER_LICENSE_LEVEL=developer
    echo DOCROPPER_DEV_PASSWORD=87654321
    echo DOCROPPER_SETTINGS_PASSWORD=12345678
) >"%ENVFILE%" && >>"%LOGFILE%" echo %date% %time% Wrote %ENVFILE%

set "PYFILE=%TEMP%\docc_update.py"
(
    echo import json, os
    echo path = 'settings.json'
    echo try:
    echo     data = json.load(open(path))
    echo except Exception:
    echo     data = {}
    echo data['license_key'] = os.environ.get('LICENSE_KEY','')
    echo data['license_name'] = os.environ.get('LICENSE_NAME','')
    echo data['license_level'] = 'developer'
    echo json.dump(data, open(path,'w'), indent=2)
) >"%PYFILE%"
python "%PYFILE%" && >>"%LOGFILE%" echo %date% %time% Updated settings.json
del "%PYFILE%"

if exist license_overrides.json del license_overrides.json

echo Developer license saved to %ENVFILE% and settings.json
echo Log written to %LOGFILE%
>>"%LOGFILE%" echo %date% %time% License setup completed
pause
endlocal
