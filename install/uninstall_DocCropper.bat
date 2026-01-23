@echo off
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Elevating privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

setlocal EnableDelayedExpansion
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%ProgramFiles%\DocCropper"
)
set /p TARGET_DIR=Uninstall directory [!APP_DIR!]:
if not "!TARGET_DIR!"=="" set "APP_DIR=!TARGET_DIR!"

echo Will remove "!APP_DIR!"
set /p CONFIRM=Proceed? [y/N]:
if /I not "!CONFIRM!"=="y" (
    echo Cancelled.
    exit /b
)

if exist "!APP_DIR!\scripts\stop_DocCropper.bat" (
    call "!APP_DIR!\scripts\stop_DocCropper.bat"
)

rmdir /S /Q "!APP_DIR!"

echo DocCropper uninstalled.
endlocal
pause
