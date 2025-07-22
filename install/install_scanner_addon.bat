@echo off
cd /d "%~dp0.."
if not exist scanner_requirements.txt (
    echo scanner_requirements.txt not found
    pause
    exit /b 1
)
if not exist venv\Scripts\activate.bat (
    echo Run install_DocCropper.bat first to create the environment.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
pip install -r scanner_requirements.txt || (
    echo Failed to install scanner dependencies.
    echo You may need to run install_scanner_tools.bat first.
)
echo Scanner add-on installation complete.
pause

