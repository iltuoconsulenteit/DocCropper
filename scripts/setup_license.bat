@echo off

setlocal EnableDelayedExpansion



:: Determine application directory (where main.py resides)

set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%main.py" (

    set "APP_DIR=%SCRIPT_DIR%"

) else (

    set "APP_DIR=%SCRIPT_DIR%.."

)

cd /d "%APP_DIR%"



if not exist env mkdir env



set /p LICENSE_KEY=Enter manual license key:

set /p LICENSE_NAME=Enter license name:



set "ENVFILE=env\license.env"



echo DOCROPPER_MANUAL_LICENSE=%LICENSE_KEY%> "%ENVFILE%"

echo DOCROPPER_LICENSE_KEY=%LICENSE_KEY%>> "%ENVFILE%"

echo DOCROPPER_LICENSE_NAME=%LICENSE_NAME%>> "%ENVFILE%"

echo LICENSE_CHECK=false>> "%ENVFILE%"

set "LICENSE_KEY=%LICENSE_KEY%"

set "LICENSE_NAME=%LICENSE_NAME%"



REM Update settings.json and restart server

set "PYTMP=%TEMP%\update_license.py"

>%PYTMP% echo import json,os,urllib.request,shutil,pathlib,time

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

>>%PYTMP% echo for p in pathlib.Path('.').rglob('__pycache__'):

>>%PYTMP% echo^    shutil.rmtree(p, ignore_errors=True)

>>%PYTMP% echo try:

>>%PYTMP% echo^    req=urllib.request.Request('http://localhost:8765/restart/', data=b'', method='POST')

>>%PYTMP% echo^    urllib.request.urlopen(req, timeout=2)

>>%PYTMP% echo^    time.sleep(1)

>>%PYTMP% echo except Exception:

>>%PYTMP% echo^    pass

python "%PYTMP%"

del "%PYTMP%"



echo Manual license saved to %ENVFILE% and settings.json updated

pause

endlocal

