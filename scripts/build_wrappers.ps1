param([string]$PythonDir)

# locate C# compiler
$csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path $csc)) {
    $csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
}
if (-not (Test-Path $csc)) {
    Write-Error 'csc.exe not found'
    exit 1
}

# compile console wrapper
$docSrc = @"
using System;
using System.Diagnostics;
using System.IO;

class Program {
    static void Main(string[] args) {
        var exe = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "python.exe");
        var psi = new ProcessStartInfo(exe, string.Join(" ", args)) {
            UseShellExecute = false,
            CreateNoWindow = true
        };
        var p = Process.Start(psi);
        p.WaitForExit();
    }
}
"@
$docCs = Join-Path $env:TEMP 'DocCropper.cs'
Set-Content -Path $docCs -Value $docSrc -Encoding UTF8
& $csc /nologo /target:exe /out:(Join-Path $PythonDir 'DocCropper.exe') $docCs
Remove-Item $docCs -ErrorAction SilentlyContinue

# compile tray wrapper
$traySrc = @"
using System;
using System.Diagnostics;
using System.IO;

class Program {
    static void Main(string[] args) {
        var exe = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "pythonw.exe");
        var psi = new ProcessStartInfo(exe, string.Join(" ", args)) {
            UseShellExecute = false,
            CreateNoWindow = true
        };
        Process.Start(psi);
    }
}
"@
$trayCs = Join-Path $env:TEMP 'DocCropperTray.cs'
Set-Content -Path $trayCs -Value $traySrc -Encoding UTF8
& $csc /nologo /target:winexe /out:(Join-Path $PythonDir 'DocCropperTray.exe') $trayCs
Remove-Item $trayCs -ErrorAction SilentlyContinue
