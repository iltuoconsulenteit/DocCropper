@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%..\"
cd /d "%APP_DIR%"

:: Stop running DocCropper processes
if exist "%SCRIPT_DIR%stop_DocCropper.bat" call "%SCRIPT_DIR%stop_DocCropper.bat"

:: Wait briefly to ensure processes exit
ping -n 2 127.0.0.1 >nul

:: Remove temp log files
for %%f in ("%TEMP%\DocCropper_start.log" "%TEMP%\doccropper_tray.log" "%TEMP%\doccropper_stop.log") do (
    if exist %%f del /f /q %%f >nul 2>&1
)

:: Remove virtual environment and install directory
if exist venv rmdir /s /q venv >nul 2>&1
if exist install rmdir /s /q install >nul 2>&1

:: Remove database file if not in use
if exist db.sqlite3 del /f /q db.sqlite3 >nul 2>&1

:: Remove configuration and license files
if exist settings.json del /f /q settings.json >nul 2>&1
if exist env rmdir /s /q env >nul 2>&1

:: Optional: remove pid files
for %%f in ("%TEMP%\doccropper.pid" "%TEMP%\doccropper_tray.pid") do (
    if exist %%f del /f /q %%f >nul 2>&1
)

echo DocCropper files removed where possible.
endlocal
exit /b
