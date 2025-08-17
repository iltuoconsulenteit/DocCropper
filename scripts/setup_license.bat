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
echo DOCROPPER_LICENSE_LEVEL=full>> "!ENVFILE!"
echo DOCROPPER_DEV_PASSWORD=87654321>> "!ENVFILE!"

echo Developer license saved to !ENVFILE!
pause
endlocal
