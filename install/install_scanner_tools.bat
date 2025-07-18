@echo off
setlocal EnableDelayedExpansion

rem Check if Build Tools already installed
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Visual Studio Build Tools already installed.
    goto :end
)

echo Downloading Visual Studio Build Tools bootstrapper...
curl -L -o "%TEMP%\vs_BuildTools.exe" https://aka.ms/vs/17/release/vs_BuildTools.exe
if not exist "%TEMP%\vs_BuildTools.exe" (
    echo Failed to download Build Tools.
    pause
    exit /b 1
)

echo Installing required components silently...
"%TEMP%\vs_BuildTools.exe" ^
  --quiet --wait --norestart --nocache ^
  --installPath "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools" ^
  --add Microsoft.VisualStudio.Workload.VCTools ^
  --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
  --add Microsoft.VisualStudio.Component.Windows10SDK.19041 ^
  --add Microsoft.VisualStudio.Component.VC.CMake.Project ^
  --includeRecommended

if exist "%TEMP%\vs_BuildTools.exe" del "%TEMP%\vs_BuildTools.exe"

echo Installation complete.
:end
echo Press any key to exit.
pause
