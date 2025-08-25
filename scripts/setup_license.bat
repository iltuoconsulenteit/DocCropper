@echo off
setlocal EnableDelayedExpansion

set "LOGFILE=temp\license_setup.log"
if not exist temp mkdir temp

if "%~1"=="am_admin" goto main
net session >nul 2>&1
if not %errorlevel%==0 (
    powershell -Command "Start-Process '%~f0' -ArgumentList 'am_admin' -Verb RunAs"
    exit /b
)

:main
>>"%LOGFILE%" echo %date% %time% License setup started

:: Determine application directory (where main.py resides)
set "SCRIPT_DIR=%~dp0"
if exist "!SCRIPT_DIR!main.py" (
    set "APP_DIR=!SCRIPT_DIR!"
) else (
    set "APP_DIR=!SCRIPT_DIR!\.."
)
cd /d "!APP_DIR!"

if not exist env mkdir env

set /p LICENSE_KEY=Enter license key:
set /p LICENSE_NAME=Enter license name:
>>"%LOGFILE%" echo %date% %time% Key entered

set "ENVFILE=env\developer.env"

{
    echo DOCROPPER_LICENSE_KEY=!LICENSE_KEY!
    echo DOCROPPER_LICENSE_NAME=!LICENSE_NAME!
    echo DOCROPPER_DEV_LICENSE=!LICENSE_KEY!
    echo DOCROPPER_LICENSE_LEVEL=developer
    echo DOCROPPER_DEV_PASSWORD=87654321
    echo DOCROPPER_SETTINGS_PASSWORD=12345678
} >"!ENVFILE!" && >>"%LOGFILE%" echo %date% %time% Wrote !ENVFILE!

python - <<PY && >>"%LOGFILE%" echo %date% %time% Updated settings.json
import json,sys
path='settings.json'
try:
    data=json.load(open(path))
except Exception:
    data={}
data['license_key']=r'%LICENSE_KEY%'
data['license_name']=r'%LICENSE_NAME%'
data['license_level']='developer'
json.dump(data,open(path,'w'),indent=2)
PY
if exist license_overrides.json del license_overrides.json

echo Developer license saved to !ENVFILE! and settings.json
>>"%LOGFILE%" echo %date% %time% License setup completed
pause
endlocal
