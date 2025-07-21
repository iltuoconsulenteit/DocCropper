@echo off
setlocal
if defined DOCROPPER_HOME (
    set "APP_DIR=%DOCROPPER_HOME%"
) else (
    set "APP_DIR=%~dp0.."
)
if not exist "%APP_DIR%\venv\Scripts\activate.bat" (
    echo DocCropper not installed at %APP_DIR%.
    pause
    exit /b 1
)
call "%APP_DIR%\venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%APP_DIR%\scanner_requirements.txt"
if errorlevel 1 (
    echo Installation failed. If the log mentions a C++ compiler,
    echo run install_scanner_tools.bat then retry.
    pause
)
endlocal
