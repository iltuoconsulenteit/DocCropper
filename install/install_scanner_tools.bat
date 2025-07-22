@echo off
setlocal

echo 🔧 Downloading Visual Studio Build Tools bootstrapper...

curl -LO https://aka.ms/vs/17/release/vs_BuildTools.exe

echo 🏗️ Installing required components silently...

vs_BuildTools.exe ^
  --quiet --wait --norestart --nocache ^
  --installPath "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools" ^
  --add Microsoft.VisualStudio.Workload.VCTools ^
  --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
  --add Microsoft.VisualStudio.Component.Windows10SDK.19041 ^
  --add Microsoft.VisualStudio.Component.VC.CMake.Project ^
  --includeRecommended

echo ✅ Installazione completata. Premere un tasto per uscire.
pause

