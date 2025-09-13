param(
    [string]$PythonDir = "$PSScriptRoot\..\python"
)
$builder = Join-Path $PSScriptRoot "build_wrappers.py"
if (!(Test-Path $builder)) { exit 0 }
$python = Join-Path $PythonDir "python.exe"
if (!(Test-Path $python)) { exit 0 }
& $python $builder $PythonDir
