@echo off
cd /d "%~dp0"

:: Ensure we have administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Elevating privileges...
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c','""%~f0""' -Verb RunAs -WindowStyle Normal -Wait"
    exit /b
)

setlocal EnableDelayedExpansion

rem Set up logging
if defined TEMP (
    set "LOG_FILE=%TEMP%\DocCropper_install.log"
) else (
    set "LOG_FILE=%~dp0install.log"
)
echo Logging to %LOG_FILE%
echo DocCropper installer log - %DATE% %TIME% > "%LOG_FILE%"

rem We'll define these after APP_DIR is known

rem Default installation directory
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%ProgramFiles%\DocCropper"
)
set /p TARGET_DIR=Installation directory [%APP_DIR%]:
if not "!TARGET_DIR!"=="" set "APP_DIR=!TARGET_DIR!"
call :log "Installation directory: !APP_DIR!"
set "REPO_URL=https://github.com/iltuoconsulenteit/DocCropper.git"

rem Now that APP_DIR is known, store commit markers
set "LAST_FILE=!APP_DIR!\last_commit"
set "PREV_FILE=!APP_DIR!\previous_commit"

rem Default developer branch
set "SCRIPT_DIR=%~dp0"
set "BRANCH_FILE=%SCRIPT_DIR%dev_branch"
if defined DOCROPPER_DEV_BRANCH (
    set "DEV_BRANCH=%DOCROPPER_DEV_BRANCH%"
) else if exist "%BRANCH_FILE%" (
    set /p DEV_BRANCH=<"%BRANCH_FILE%"
) else (
    set "DEV_BRANCH=work"
)
echo %DEV_BRANCH%>"%BRANCH_FILE%"

if not defined DOCROPPER_BRANCH (
    echo.
    echo Choose branch to install:
    echo  1^) main
    echo  2^) !DEV_BRANCH!
    set /p BSEL=Selection [2]:
    if "!BSEL!"=="1" (
        set "BRANCH=main"
    ) else (
        set "BRANCH=!DEV_BRANCH!"
    )
) else (
    set "BRANCH=%DOCROPPER_BRANCH%"
)
call :log "Using branch: !BRANCH!"

set "CONFIG_FILE=settings.json"
set "BACKUP_FILE=settings.local.json.bak"

if not exist "!APP_DIR!" (
    mkdir "!APP_DIR!" >nul 2>&1
    if errorlevel 1 (
        call :log "Unable to create !APP_DIR!. Run this script as Administrator."
        endlocal
        pause
        exit /b 1
    )
)

call :main
set "MAIN_ERR=%ERRORLEVEL%"
if not "%MAIN_ERR%"=="0" (
    echo Installation failed. See %LOG_FILE% for details.
    endlocal
    pause
    exit /b %MAIN_ERR%
)

endlocal
exit /b 0

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
        powershell -NoProfile -Command "Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%TEMP%\git_installer.exe'" >>"%LOG_FILE%" 2>&1
        if exist "%TEMP%\git_installer.exe" (
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


if exist "!APP_DIR!\scripts\stop_DocCropper.bat" (
    call :log "Stopping running DocCropper..."
    call "!APP_DIR!\scripts\stop_DocCropper.bat" >nul 2>&1
)

if not exist "!APP_DIR!\.git" (
    dir /b "!APP_DIR!" | findstr . >nul 2>&1
    if not errorlevel 1 (
        call :log "Destination !APP_DIR! exists and is not empty."
        set /p wipe_choice=Delete contents and continue? [y/N]:
        if /I "!wipe_choice!"=="y" (
            call :log "Removing old files..."
            rmdir /S /Q "!APP_DIR!" >>"%LOG_FILE%" 2>&1
            mkdir "!APP_DIR!" >>"%LOG_FILE%" 2>&1
        ) else (
            call :log "Please choose another directory."
            exit /b 1
        )
    )
    call :log "Cloning repository..."
    git clone --branch !BRANCH! %REPO_URL% "!APP_DIR!" >>"%LOG_FILE%" 2>&1
    for /f %%h in ('git -C "!APP_DIR!" rev-parse HEAD') do echo %%h>"!LAST_FILE!"
    if errorlevel 1 (
        call :log "Clone failed. Check your network connection, permissions, and that !APP_DIR! is empty."
        exit /b 1
    )
) else (
    call :log "Repository present in !APP_DIR!"
    cd /d "!APP_DIR!"
    if exist "!LAST_FILE!" (
        copy /Y "!LAST_FILE!" "!PREV_FILE!" >nul 2>&1
    ) else (
        for /f %%h in ('git rev-parse HEAD') do echo %%h>"!PREV_FILE!"
    )
    if exist "!CONFIG_FILE!" (
        git status --porcelain | findstr "!CONFIG_FILE!" >nul && (
            call :log "Backup !CONFIG_FILE! to !BACKUP_FILE!..."
            copy /Y "!CONFIG_FILE!" "!BACKUP_FILE!" >>"%LOG_FILE%" 2>&1
            git restore "!CONFIG_FILE!"
        )
    )
    set "LIC_BACKUP=%TEMP%\license.env"
    if exist "env\license.env" copy /Y "env\license.env" "%LIC_BACKUP%" >nul
    call :log "Updating repository..."
    git fetch --all --prune >>"%LOG_FILE%" 2>&1 || (
        call :log "Failed to fetch updates from origin"
        exit /b 1
    )
    git merge --abort >nul 2>&1
    git rebase --abort >nul 2>&1
    git checkout !BRANCH! >>"%LOG_FILE%" 2>&1 || git checkout -B !BRANCH! origin/!BRANCH! >>"%LOG_FILE%" 2>&1
    git reset --hard origin/!BRANCH! >>"%LOG_FILE%" 2>&1
    git clean -ffdx -e python/ >>"%LOG_FILE%" 2>&1
    for /f %%h in ('git rev-parse HEAD') do echo %%h>"!LAST_FILE!"
    if exist "%LIC_BACKUP%" (
        if not exist "env" mkdir "env"
        copy /Y "%LIC_BACKUP%" "env\license.env" >nul
    )
    if exist "!BACKUP_FILE!" (
        call :log "Merge !BACKUP_FILE! in !CONFIG_FILE! (manual merge suggested)"
        del "!BACKUP_FILE!" >>"%LOG_FILE%" 2>&1
    )
    cd /d "%~dp0"
)

rem Remove cached Python bytecode so updates load correctly
call :log "Cleaning Python cache..."
powershell -NoProfile -Command "Get-ChildItem -Path `"!APP_DIR!`" -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force; Get-ChildItem -Path `"!APP_DIR!`" -Recurse -Filter '*.pyc' | Remove-Item -Force" >nul 2>&1

cd /d "!APP_DIR!"

call :log "Last 10 commits:"
git log -n 10 --pretty=format:"%%h | %%ad | %%s" --date=short >>"%LOG_FILE%" 2>&1

echo.
set /p commit_hash=Restore to a specific commit? (leave empty to continue):
if not "!commit_hash!"=="" (
    call :log "Checking out commit !commit_hash!..."
    git checkout !commit_hash! >>"%LOG_FILE%" 2>&1
    for /f %%h in ('git rev-parse HEAD') do echo %%h>"!LAST_FILE!"
)

rem Restore settings and license from backup
set "BACKUP_DIR=%USERPROFILE%\DocCropperBackup"
if exist "%BACKUP_DIR%\settings.json" copy /Y "%BACKUP_DIR%\settings.json" "!APP_DIR!\settings.json" >nul
if exist "%BACKUP_DIR%\env\license.env" (
    if not exist "!APP_DIR!\env" mkdir "!APP_DIR!\env"
    copy /Y "%BACKUP_DIR%\env\license.env" "!APP_DIR!\env\license.env" >nul
)

rem Copy default environment files if missing
if not exist "!APP_DIR!\.env" if exist "!APP_DIR!\.env.example" copy "!APP_DIR!\.env.example" "!APP_DIR!\.env" >nul
if not exist "!APP_DIR!\env\auth.env" (
    if exist "!APP_DIR!\env\auth.env.example" (
        if not exist "!APP_DIR!\env" mkdir "!APP_DIR!\env"
        copy "!APP_DIR!\env\auth.env.example" "!APP_DIR!\env\auth.env" >nul
    )
)

rem Determine required Python version
set "PY_VER=3.11.7"
if exist "env\python.env" (
    for /f "usebackq tokens=1,2 delims==" %%A in ("env\python.env") do (
        if /I "%%A"=="PYTHON_VERSION" set "PY_VER=%%B"
    )
)
for /f "tokens=1,2 delims=." %%A in ("%PY_VER%") do set "PY_SHORT=%%A%%B"
call :log "Required Python version: %PY_VER%"

rem Ensure Python runtime is available
call :ensure_python || exit /b 1

rem Ensure our Python directory is on PATH for subsequent scripts
set "PATH=!PY_DIR!;!PY_DIR!\Scripts;!PATH!"

if not defined PY_EMBED (
    if not exist "venv\Scripts\activate.bat" (
        call :log "Creating virtual environment..."
        rmdir /S /Q venv 2>>"%LOG_FILE%" 1>&2
        "!PYTHON_CMD!" -m venv venv >>"%LOG_FILE%" 2>&1 || (
            call :log "Error creating venv"
            exit /b 1
        )
    )
    call venv\Scripts\activate.bat
) else (
    call :log "Using embeddable Python environment"
)

if exist requirements.txt (
    call :log "Installing Python packages..."
    "!PYTHON_CMD!" -m pip install --upgrade pip >>"%LOG_FILE%" 2>&1
    "!PYTHON_CMD!" -m pip install -r requirements.txt >>"%LOG_FILE%" 2>&1
    if exist "!PY_DIR!\Scripts\pywin32_postinstall.py" (
        call :log "Running pywin32 postinstall..."
        "!PYTHON_CMD!" "!PY_DIR!\Scripts\pywin32_postinstall.py" -install >>"%LOG_FILE%" 2>&1
    )
) else (
    call :log "requirements.txt not found!"
)

set /p RUN_APP=Launch DocCropper with tray icon now? [Y/n]:
if /I "!RUN_APP!"=="n" (
    rem user chose not to run
) else (
    pushd "!APP_DIR!" >nul
    if exist "!PYTHONW_CMD!" (
        call :log "Launching tray icon"
        start "" "!PYTHONW_CMD!" "!APP_DIR!\doccropper_tray.py" --auto-start
    ) else (
        call :log "Launching tray icon"
        start "" "!PYTHON_CMD!" "!APP_DIR!\doccropper_tray.py" --auto-start
    )
    popd >nul
)

call :log "Log saved to !LOG_FILE!"
echo Installation complete. See !LOG_FILE! for details.
pause
exit /b

:ensure_python
set "PYTHON_CMD="
set "PYTHONW_CMD="
set "PY_FOUND="
set "PY_EMBED="
set "PY_DIR=!APP_DIR!\python"
if exist "!PY_DIR!\python.exe" (
    for /f "tokens=2 delims= " %%V in ('"!PY_DIR!\python.exe" -V 2^>^&1') do set "PY_FOUND=%%V"
    if "!PY_FOUND!"=="%PY_VER%" (
        set "PYTHON_CMD=!PY_DIR!\python.exe"
        set "PYTHONW_CMD=!PY_DIR!\pythonw.exe"
        set "PY_EMBED=1"
        call :log "Using Python at !PYTHON_CMD!"
        exit /b 0
    )
)

for %%P in (python.exe) do if not defined PYTHON_CMD set "PYTHON_CMD=%%~$PATH:%%P"
if defined PYTHON_CMD (
    for /f "tokens=2 delims= " %%V in ('"!PYTHON_CMD!" -V 2^>^&1') do set "PY_FOUND=%%V"
    if "!PY_FOUND!"=="%PY_VER%" (
        set "PYTHONW_CMD=!PYTHON_CMD:python.exe=pythonw.exe!"
        call :log "Using Python at !PYTHON_CMD!"
        exit /b 0
    ) else (
        set "PYTHON_CMD="
    )
)

call :log "Python %PY_VER% not found. Downloading embeddable runtime..."
set "PY_ZIP=python-%PY_VER%-embed-amd64.zip"
if not exist "%TEMP%" mkdir "%TEMP%"
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/!PY_VER!/!PY_ZIP!' -OutFile '%TEMP%\!PY_ZIP!'" >>"%LOG_FILE%" 2>&1
if not exist "%TEMP%\!PY_ZIP!" (
    call :log "Failed to download Python !PY_VER! embeddable package."
    exit /b 1
)
if exist "!PY_DIR!" rmdir /S /Q "!PY_DIR!" >>"%LOG_FILE%" 2>&1
mkdir "!PY_DIR!" >>"%LOG_FILE%" 2>&1
powershell -NoProfile -Command "Expand-Archive -Path '%TEMP%\!PY_ZIP!' -DestinationPath '!PY_DIR!'" >>"%LOG_FILE%" 2>&1
del "%TEMP%\!PY_ZIP!" >>"%LOG_FILE%" 2>&1
powershell -NoProfile -Command "(Get-Content '!PY_DIR!\python!PY_SHORT!._pth') -replace '#import site','import site' | Set-Content '!PY_DIR!\python!PY_SHORT!._pth'" >>"%LOG_FILE%" 2>&1
set "PYTHON_CMD=!PY_DIR!\python.exe"
set "PYTHONW_CMD=!PY_DIR!\pythonw.exe"
set "PY_EMBED=1"
call :log "Bootstrapping pip..."
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '!PY_DIR!\get-pip.py'" >>"%LOG_FILE%" 2>&1
"!PYTHON_CMD!" "!PY_DIR!\get-pip.py" >>"%LOG_FILE%" 2>&1
del "!PY_DIR!\get-pip.py" >>"%LOG_FILE%" 2>&1
call :log "Using Python at !PYTHON_CMD!"
exit /b 0
