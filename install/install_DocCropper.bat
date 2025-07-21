@echo off

:: Ensure we have administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Elevating privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

rem Previous versions logged installer output using PowerShell's Start-Transcript
rem but this sometimes failed with a "Path argument is null" error. For now we
rem run the installer directly without logging so setup can continue smoothly.
setlocal EnableDelayedExpansion

rem Default installation directory
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%ProgramFiles%\DocCropper"
)
set /p TARGET_DIR=Installation directory [%APP_DIR%]:
if not "%TARGET_DIR%"=="" set "APP_DIR=%TARGET_DIR%"
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

if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo Unable to create %APP_DIR%. Falling back to "%~dp0DocCropper"
        set "APP_DIR=%~dp0DocCropper"
        if not exist "%APP_DIR%" mkdir "%APP_DIR%"
    )
)

call :main

endlocal
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
    echo Git not found. Trying to install...
    where winget >nul 2>&1
    if not errorlevel 1 (
        winget install --id Git.Git -e --source winget
    ) else (
        echo winget not available. Downloading Git installer...
        if defined PROCESSOR_ARCHITEW6432 (
            set "GIT_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.44.0-64-bit.exe"
        ) else (
            set "GIT_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.44.0-32-bit.exe"
        )
        powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%TEMP%\git_installer.exe' -ErrorAction Stop } catch { exit 1 }"
        if exist "%TEMP%\git_installer.exe" (
            echo Running Git installer...
            start /wait "" "%TEMP%\git_installer.exe" /VERYSILENT /NORESTART
            del "%TEMP%\git_installer.exe"
        ) else (
            echo Failed to download Git installer. Install Git manually.
            exit /b 1
        )
    )
    where git >nul 2>&1 || (
        echo Git installation failed. Install Git manually.
        exit /b 1
    )
)

if not exist "%APP_DIR%\.git" (
    rem ensure destination directory is empty before cloning
    dir /b "%APP_DIR%" | findstr . >nul 2>&1
    if not errorlevel 1 (
        echo Destination %APP_DIR% exists and is not empty.
        set /p wipe_choice=Delete contents and continue? [y/N] 
        if /I "!wipe_choice!"=="y" (
            echo Removing old files...
            rmdir /S /Q "%APP_DIR%" && mkdir "%APP_DIR%"
        ) else (
            echo Please choose another directory.
            exit /b 1
        )
    )
    echo Cloning repository...
    git clone --branch %BRANCH% %REPO_URL% "%APP_DIR%"
    if errorlevel 1 (
        echo Clone failed. Check your network connection, permissions, and that %APP_DIR% is empty.
        exit /b 1
    )
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

rem Ensure wrapper start/stop scripts exist in the installation root
echo Aggiornamento script di avvio...
copy /Y "%~dp0..\start_DocCropper.bat" "%APP_DIR%" >nul
copy /Y "%~dp0..\stop_DocCropper.bat"  "%APP_DIR%" >nul

set /p RUN_APP=Launch DocCropper with tray icon now? [Y/n]
if /I "%RUN_APP%" NEQ "n" if /I "%RUN_APP%" NEQ "N" (
    pushd "%APP_DIR%" >nul
    where pythonw >nul 2>&1 && (
        start "" pythonw doccropper_tray.py --auto-start
    ) || (
        start "" python doccropper_tray.py --auto-start
    )
    popd >nul
)
exit /b
