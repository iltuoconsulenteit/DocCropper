@echo off
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
set "LOG_FILE=%APP_DIR%\install.log"

if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo Unable to create %APP_DIR%. Falling back to "%~dp0DocCropper"
        set "APP_DIR=%~dp0DocCropper"
        set "LOG_FILE=%APP_DIR%\install.log"
        if not exist "%APP_DIR%" mkdir "%APP_DIR%"
    )
)

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
        echo Please choose an empty directory or remove its contents.
        exit /b 1
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

echo Avvio DocCropper...
start "DocCropper" "%APP_DIR%\scripts\start_DocCropper.bat"

exit /b
