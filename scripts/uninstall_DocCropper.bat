@echo off
cd /d "%~dp0"
setlocal

if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%ProgramFiles%\DocCropper"
)

echo Uninstalling DocCropper from "%APP_DIR%"...

if exist "%APP_DIR%\scripts\stop_DocCropper.bat" (
    call "%APP_DIR%\scripts\stop_DocCropper.bat" >nul 2>&1
)

:: Backup settings and license to user profile
set "BACKUP_DIR=%USERPROFILE%\DocCropperBackup"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" >nul 2>&1
if exist "%APP_DIR%\settings.json" copy /Y "%APP_DIR%\settings.json" "%BACKUP_DIR%\settings.json" >nul
if exist "%APP_DIR%\env\license.env" (
    if not exist "%BACKUP_DIR%\env" mkdir "%BACKUP_DIR%\env" >nul 2>&1
    copy /Y "%APP_DIR%\env\license.env" "%BACKUP_DIR%\env\license.env" >nul
)

:: Take ownership and grant permissions to avoid access denied
if exist "%APP_DIR%" (
    takeown /f "%APP_DIR%" /r /d y >nul 2>&1
    icacls "%APP_DIR%" /grant *S-1-1-0:F /t >nul 2>&1
)

rmdir /S /Q "%APP_DIR%" 2>nul
if exist "%APP_DIR%" (
    powershell -NoProfile -Command "Remove-Item -Path '%APP_DIR%' -Recurse -Force" 2>nul
)

if exist "%APP_DIR%" (
    echo Failed to remove %APP_DIR%. Close any running applications and try again.
    exit /b 1
)

echo Uninstallation complete.
exit /b 0
