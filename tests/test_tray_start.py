import sys
import types
from pathlib import Path


def test_tray_start_uses_auto_flag(monkeypatch, tmp_path):
    """Ensure the tray helper launches the Windows start script in auto mode."""
    import importlib

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parent.parent))

    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)

    tray = importlib.import_module("doccropper_tray")

    commands = []

    class DummyPopen:  # pragma: no cover - simple recorder
        def __init__(self, cmd, env=None, stdout=None, stderr=None, creationflags=0):
            commands.append(cmd)

    monkeypatch.setattr(tray, "SYSTEM", "Windows")
    monkeypatch.setattr(tray, "LOG_FILE", Path(tmp_path) / "tray.log")
    monkeypatch.setattr(tray.subprocess, "Popen", DummyPopen)
    monkeypatch.setattr(tray.logging, "info", lambda *args, **kwargs: None)

    tray.start_app()

    assert commands, "start_app did not attempt to run the start script"
    cmd = commands[0]
    script_path = str(tray.SCRIPTS_DIR / tray.START_SCRIPTS)
    assert cmd[:3] == ["cmd", "/c", script_path]
    assert cmd[-1] == "--auto"
