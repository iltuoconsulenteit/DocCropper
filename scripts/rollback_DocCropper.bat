@echo off
setlocal
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\
set PREV_FILE=%APP_DIR%previous_commit
if not exist "%PREV_FILE%" (
  echo No previous commit information found.
  exit /b 1
)
for /f %%H in (%PREV_FILE%) do set HASH=%%H
cd /d "%APP_DIR%"
call git rev-parse %%HASH%% >nul 2>&1 || (
  echo Stored commit %%HASH%% not found.
  exit /b 1
)
call git reset --hard %%HASH%%
echo Restored to commit %%HASH%%
endlocal
