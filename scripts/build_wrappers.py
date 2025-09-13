import os
import sys
import subprocess
import tempfile
import textwrap

def find_csc():
    windir = os.environ.get('WINDIR')
    if not windir:
        return None
    candidates = [
        os.path.join(windir, 'Microsoft.NET', 'Framework64', 'v4.0.30319', 'csc.exe'),
        os.path.join(windir, 'Microsoft.NET', 'Framework', 'v4.0.30319', 'csc.exe'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def compile_wrapper(csc, code, out_path, winexe=False):
    with tempfile.NamedTemporaryFile('w', suffix='.cs', delete=False, encoding='utf-8') as fh:
        fh.write(textwrap.dedent(code))
        src = fh.name
    target = 'winexe' if winexe else 'exe'
    subprocess.check_call([csc, '/nologo', f'/target:{target}', f'/out:{out_path}', src])
    os.remove(src)

def main():
    if len(sys.argv) != 2:
        print('usage: build_wrappers.py <python_dir>', file=sys.stderr)
        sys.exit(1)
    python_dir = sys.argv[1]
    csc = find_csc()
    if not csc:
        raise RuntimeError('csc.exe not found')
    console_code = """
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
"""
    tray_code = """
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
"""
    compile_wrapper(csc, console_code, os.path.join(python_dir, 'DocCropper.exe'))
    compile_wrapper(csc, tray_code, os.path.join(python_dir, 'DocCropperTray.exe'), winexe=True)

if __name__ == '__main__':
    main()
