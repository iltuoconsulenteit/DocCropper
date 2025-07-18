@echo off
setlocal EnableDelayedExpansion

rem Installation directory next to this script
set "APP_DIR=%cd%\DocCropper"
set "REPO_URL=https://github.com/iltuoconsulenteit/DocCropper.git"

rem Default branches
if defined DOCROPPER_DEV_BRANCH (
    set "DEV_BRANCH=%DOCROPPER_DEV_BRANCH%"
) else (
    set "DEV_BRANCH=dgwo4q-codex/add-features-from-doccropper-project"
)

if not defined DOCROPPER_BRANCH (
    echo.
    echo Choose branch to install:
    echo  1^) main
    echo  2^) %DEV_BRANCH%
    set /p BSEL=Selection [1]: 
    if "%BSEL%"=="2" (
        set "BRANCH=%DEV_BRANCH%"
    ) else (
        set "BRANCH=main"
    )
) else (
    set "BRANCH=%DOCROPPER_BRANCH%"
)
set "CONFIG_FILE=settings.json"
set "BACKUP_FILE=settings.local.json.bak"
set "LOG_FILE=%APP_DIR%\install.log"

if not exist "%APP_DIR%" mkdir "%APP_DIR%"

echo Logging to %LOG_FILE%
where powershell >nul 2>&1 && set "PWSH=powershell"
if defined PWSH (
    %PWSH% -NoProfile -Command "Start-Transcript -Path '%LOG_FILE%' -Append" >nul
)
call :main
if defined PWSH (
    %PWSH% -NoProfile -Command "Stop-Transcript" >nul
)
if exist "%LOG_FILE%" echo Log saved to %LOG_FILE%
endlocal
pause
exit /b

:main
where git >nul 2>&1
if errorlevel 1 (
    echo Git not found. Trying to install with winget...
    where winget >nul 2>&1 || (
        echo winget not available. Install Git manually.
        exit /b 1
    )
    winget install --id Git.Git -e --source winget
)

if not exist "%APP_DIR%\.git" (
    echo Cloning repository...
    git clone --branch %BRANCH% %REPO_URL% "%APP_DIR%"
) else (
    echo Repository present in %APP_DIR%
    set /p update_choice=Vuoi aggiornare il repository da GitHub? [s/N] 
    if /I "%update_choice%"=="s" (
        cd /d "%APP_DIR%"
        if exist "%CONFIG_FILE%" (
            git status --porcelain | findstr "%CONFIG_FILE%" >nul && (
                echo Backup di %CONFIG_FILE% in %BACKUP_FILE%...
                copy /Y "%CONFIG_FILE%" "%BACKUP_FILE%"
                git restore "%CONFIG_FILE%"
            )
        )
        git checkout %BRANCH%
        git pull origin %BRANCH%
        if exist "%BACKUP_FILE%" (
            echo Merge %BACKUP_FILE% in %CONFIG_FILE% (richiede tool esterno)
            echo >> Merging skipped on Windows - manual merge suggested.
            del "%BACKUP_FILE%"
        )
        cd /d "%~dp0"
    )
)

cd /d "%APP_DIR%"

:: show last 10 commits
echo.
echo Ultimi 10 commit:
git log -n 10 --pretty=format:"%%h | %%ad | %%s" --date=short

echo.
set /p commit_hash=Vuoi ripristinare un commit specifico? (lascia vuoto per continuare): 
if not "%commit_hash%"=="" (
    echo Checkout del commit %commit_hash%...
    git checkout %commit_hash%
)

if not exist "venv\Scripts\activate.bat" (
    echo Creazione ambiente virtuale...
    rmdir /S /Q venv 2>nul
    python -m venv venv || (
        echo Errore durante la creazione del venv
        exit /b 1
    )
)

call venv\Scripts\activate.bat

if exist requirements.txt (
    echo Installazione pacchetti Python...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo File requirements.txt non trovato!
)

echo Avvio DocCropper tray...
if exist "venv\Scripts\pythonw.exe" (
    start "" venv\Scripts\pythonw.exe doccropper_tray.py --auto-start
) else (
    start "" venv\Scripts\python.exe doccropper_tray.py --auto-start
)

exit /b
