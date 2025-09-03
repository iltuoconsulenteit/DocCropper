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

set /p LICENSE_KEY=Enter manual license key:
set /p LICENSE_NAME=Enter license name:

set "ENVFILE=env\license.env"

echo.>"%TEMP%\_writetest.tmp" 2>NUL
if errorlevel 1 (
    echo Access denied. Please run this script as Administrator.
    pause
    exit /b 1
)
del "%TEMP%\_writetest.tmp" 2>NUL

2>nul ( >"!ENVFILE!" echo DOCROPPER_MANUAL_LICENSE=!LICENSE_KEY! ) || (
    echo Access denied. Please run this script as Administrator.
    pause
    exit /b 1
)
echo DOCROPPER_LICENSE_KEY=!LICENSE_KEY!>> "!ENVFILE!"
echo DOCROPPER_LICENSE_NAME=!LICENSE_NAME!>> "!ENVFILE!"
echo LICENSE_CHECK=false>> "!ENVFILE!"
set "LICENSE_KEY=!LICENSE_KEY!"
set "LICENSE_NAME=!LICENSE_NAME!"
REM Update settings.json using a temporary Python script
set "PYTMP=%TEMP%\update_license.py"
>%PYTMP% echo import json,os
>>%PYTMP% echo path="settings.json"
>>%PYTMP% echo try:
>>%PYTMP% echo^    f=open(path)
>>%PYTMP% echo^    data=json.load(f)
>>%PYTMP% echo^    f.close()
>>%PYTMP% echo except Exception:
>>%PYTMP% echo^    data={}
>>%PYTMP% echo data['license_key']=os.environ['LICENSE_KEY']
>>%PYTMP% echo data['license_name']=os.environ['LICENSE_NAME']
>>%PYTMP% echo data['license_check']=False
>>%PYTMP% echo f=open(path,'w')
>>%PYTMP% echo json.dump(data,f)
>>%PYTMP% echo f.close()
python "%PYTMP%"
del "%PYTMP%"

echo Manual license saved to !ENVFILE! and settings.json updated
pause
endlocal
