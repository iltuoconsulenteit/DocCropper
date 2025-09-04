param([string]$PythonDir)

# Compile DocCropper.exe wrapper
$docSrc = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
[assembly: AssemblyTitle(""DocCropper"")]
[assembly: AssemblyProduct(""DocCropper"")]
[assembly: AssemblyDescription(""DocCropper"")]
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

Add-Type -OutputAssembly (Join-Path $PythonDir "DocCropper.exe") -OutputType ConsoleApplication $docSrc

# Compile DocCropperTray.exe wrapper
$traySrc = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
[assembly: AssemblyTitle(""DocCropperTray"")]
[assembly: AssemblyProduct(""DocCropperTray"")]
[assembly: AssemblyDescription(""DocCropper Tray"")]
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

Add-Type -OutputAssembly (Join-Path $PythonDir "DocCropperTray.exe") -OutputType WindowsApplication $traySrc
