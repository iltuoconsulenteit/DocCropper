@echo off

:: Ensure we have administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Elevating privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

rem Set up simple logging so we can diagnose installation issues
setlocal EnableDelayedExpansion
if defined TEMP (
    set "LOG_FILE=%TEMP%\DocCropper_install.log"
 ) else (
    set "LOG_FILE=%~dp0install.log"
)
echo Logging to %LOG_FILE%
echo DocCropper installer log - %DATE% %TIME% > "%LOG_FILE%"

rem Default installation directory
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%ProgramFiles%\DocCropper"
)
set /p TARGET_DIR=Installation directory [%APP_DIR%]:
if not "%TARGET_DIR%"=="" set "APP_DIR=%TARGET_DIR%"
call :log "Installation directory: %APP_DIR%"
set "REPO_URL=https://github.com/iltuoconsulenteit/DocCropper.git"

rem Default branches
if defined DOCROPPER_DEV_BRANCH (
    set "DEV_BRANCH=%DOCROPPER_DEV_BRANCH%"
) else (
    set "DEV_BRANCH=codex/move-version-number-to-bottom-right"
)

if not defined DOCROPPER_BRANCH (
    echo.
    echo Choose branch to install:
    echo  1^) main
    echo  2^) %DEV_BRANCH%
    set /p BSEL=Selection [1]:
    if "!BSEL!"=="2" (
        set "BRANCH=%DEV_BRANCH%"
    ) else (
        set "BRANCH=main"
    )
) else (
    set "BRANCH=%DOCROPPER_BRANCH%"
)
call :log "Using branch: %BRANCH%"
set "CONFIG_FILE=settings.json"
set "BACKUP_FILE=settings.local.json.bak"

if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%" >nul 2>&1
    if errorlevel 1 (
        call :log "Unable to create %APP_DIR%. Run this script as Administrator."
        exit /b 1
    )
)

call :main

endlocal
exit /b

:log
set MSG=%*
echo %MSG%
echo %MSG%>>"%LOG_FILE%"
exit /b

:main
where git >nul 2>&1
if errorlevel 1 (
    rem Git may be installed but not in PATH - check common locations
    if exist "%ProgramFiles%\Git\cmd\git.exe" (
        set "PATH=%ProgramFiles%\Git\cmd;%PATH%"
    ) else if exist "%ProgramFiles(x86)%\Git\cmd\git.exe" (
        set "PATH=%ProgramFiles(x86)%\Git\cmd;%PATH%"
    )
)

where git >nul 2>&1
if errorlevel 1 (
    call :log "Git not found. Trying to install..."
    where winget >nul 2>&1
    if not errorlevel 1 (
        winget install --id Git.Git -e --source winget >>"%LOG_FILE%" 2>&1
    ) else (
        call :log "winget not available. Downloading Git installer..."
        if defined PROCESSOR_ARCHITEW6432 (
            set "GIT_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.44.0-64-bit.exe"
        ) else (
            set "GIT_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.44.0-32-bit.exe"
        )
        powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%TEMP%\git_installer.exe' -ErrorAction Stop } catch { exit 1 }" >>"%LOG_FILE%" 2>&1
        if exist "%TEMP%\git_installer.exe" (
            call :log "Running Git installer..."
            start /wait "" "%TEMP%\git_installer.exe" /VERYSILENT /NORESTART >>"%LOG_FILE%" 2>&1
            del "%TEMP%\git_installer.exe" >>"%LOG_FILE%" 2>&1
        ) else (
            call :log "Failed to download Git installer. Install Git manually."
            exit /b 1
        )
    )
    where git >nul 2>&1 || (
        call :log "Git installation failed. Install Git manually."
        exit /b 1
    )
)

if not exist "%APP_DIR%\.git" (
    rem ensure destination directory is empty before cloning
    dir /b "%APP_DIR%" | findstr . >nul 2>&1
    if not errorlevel 1 (
        call :log "Destination %APP_DIR% exists and is not empty."
        set /p wipe_choice=Delete contents and continue? [y/N] 
        if /I "!wipe_choice!"=="y" (
            call :log "Removing old files..."
            rmdir /S /Q "%APP_DIR%" >>"%LOG_FILE%" 2>&1 && mkdir "%APP_DIR%" >>"%LOG_FILE%" 2>&1
        ) else (
            call :log "Please choose another directory."
            exit /b 1
        )
    )
    call :log "Cloning repository..."
    git clone --branch %BRANCH% %REPO_URL% "%APP_DIR%" >>"%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "Clone failed. Check your network connection, permissions, and that %APP_DIR% is empty."
        exit /b 1
    )
) else (
    call :log "Repository present in %APP_DIR%"
    set /p update_choice=Vuoi aggiornare il repository da GitHub? [s/N]
    if /I "!update_choice!"=="s" (
        cd /d "%APP_DIR%"
        if exist "%CONFIG_FILE%" (
            git status --porcelain | findstr "%CONFIG_FILE%" >nul && (
                call :log "Backup di %CONFIG_FILE% in %BACKUP_FILE%..."
                copy /Y "%CONFIG_FILE%" "%BACKUP_FILE%" >>"%LOG_FILE%" 2>&1
                git restore "%CONFIG_FILE%"
            )
        )
        call :log "Updating repository..."
        git checkout %BRANCH% >>"%LOG_FILE%" 2>&1
        git fetch origin %BRANCH% >>"%LOG_FILE%" 2>&1
        git reset --hard origin/%BRANCH% >>"%LOG_FILE%" 2>&1
        git clean -fd >>"%LOG_FILE%" 2>&1
        git pull --ff-only >>"%LOG_FILE%" 2>&1
        if exist "%BACKUP_FILE%" (
            call :log "Merge %BACKUP_FILE% in %CONFIG_FILE% (manual merge suggested)"
            del "%BACKUP_FILE%" >>"%LOG_FILE%" 2>&1
        )
        cd /d "%~dp0"
    )
)

cd /d "%APP_DIR%"

:: show last 10 commits
echo.
call :log "Ultimi 10 commit:"
git log -n 10 --pretty=format:"%%h | %%ad | %%s" --date=short >>"%LOG_FILE%" 2>&1

echo.
set /p commit_hash=Vuoi ripristinare un commit specifico? (lascia vuoto per continuare): 
if not "%commit_hash%"=="" (
    call :log "Checkout del commit %commit_hash%..."
    git checkout %commit_hash% >>"%LOG_FILE%" 2>&1
)

if not exist "venv\Scripts\activate.bat" (
    call :log "Creazione ambiente virtuale..."
    rmdir /S /Q venv 2>>"%LOG_FILE%" 1>&2
    python -m venv venv >>"%LOG_FILE%" 2>&1 || (
        call :log "Errore durante la creazione del venv"
        exit /b 1
    )
)

call venv\Scripts\activate.bat

if exist requirements.txt (
    call :log "Installazione pacchetti Python..."
    python -m pip install --upgrade pip >>"%LOG_FILE%" 2>&1
    pip install -r requirements.txt >>"%LOG_FILE%" 2>&1
) else (
    call :log "File requirements.txt non trovato!"
)

rem Ensure wrapper start/stop scripts exist in the installation root
call :log "Aggiornamento script di avvio..."
copy /Y "%~dp0..\start_DocCropper.bat" "%APP_DIR%\start_DocCropper.bat" >>"%LOG_FILE%" 2>&1
copy /Y "%~dp0..\stop_DocCropper.bat"  "%APP_DIR%\stop_DocCropper.bat" >>"%LOG_FILE%" 2>&1

set /p RUN_APP=Launch DocCropper with tray icon now? [Y/n]
if /I "%RUN_APP%" NEQ "n" if /I "%RUN_APP%" NEQ "N" (
    pushd "%APP_DIR%" >nul
    where pythonw >nul 2>&1 && (
        call :log "Launching tray icon"
        start "" pythonw doccropper_tray.py --auto-start >>"%LOG_FILE%" 2>&1
    ) || (
        call :log "Launching tray icon"
        start "" python doccropper_tray.py --auto-start >>"%LOG_FILE%" 2>&1
    )
    popd >nul
)
exit /b
