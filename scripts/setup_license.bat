@echo off
setlocal EnableDelayedExpansion

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

set "ENVFILE=env\developer.env"

echo.>"%TEMP%\_writetest.tmp" 2>NUL
if errorlevel 1 (
    echo Access denied. Please run this script as Administrator.
    pause
    exit /b 1
)
del "%TEMP%\_writetest.tmp" 2>NUL

2>nul ( >"!ENVFILE!" echo DOCROPPER_LICENSE_KEY=!LICENSE_KEY! ) || (
    echo Access denied. Please run this script as Administrator.
    pause
    exit /b 1
)
echo DOCROPPER_LICENSE_NAME=!LICENSE_NAME!>> "!ENVFILE!"
echo DOCROPPER_DEV_LICENSE=!LICENSE_KEY!>> "!ENVFILE!"
echo DOCROPPER_LICENSE_LEVEL=developer>> "!ENVFILE!"
echo DOCROPPER_DEV_PASSWORD=87654321>> "!ENVFILE!"
echo DOCROPPER_SETTINGS_PASSWORD=12345678>> "!ENVFILE!"
python - <<PY
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
pause
endlocal
