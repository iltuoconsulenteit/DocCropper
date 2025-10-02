import sys
from pathlib import Path


def _build_args(tmp_path: Path, log_name: str = "log.txt"):
    from types import SimpleNamespace

    return SimpleNamespace(
        python=sys.executable,
        main="dummy_main.py",
        port=8765,
        log=str(tmp_path / log_name),
        pid_file=str(tmp_path / "doccropper.pid"),
        cwd=str(tmp_path),
    )


def test_launch_app_success(monkeypatch, tmp_path):
    import scripts.launch_app as launch_app

    class DummyProc:
        pid = 123

        def poll(self):  # pragma: no cover - invoked indirectly
            return None

    captured_commands = {}

    def fake_popen(cmd, cwd=None, stdout=None, stderr=None, creationflags=0):  # pragma: no cover - patched into subprocess
        captured_commands["cmd"] = cmd
        captured_commands["cwd"] = cwd
        return DummyProc()

    monkeypatch.setattr(launch_app.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(launch_app.time, "sleep", lambda *_: None)

    args = _build_args(tmp_path)
    result = launch_app.launch(args)

    assert result == 0
    assert Path(args.pid_file).read_text(encoding="utf-8") == "123"
    log_content = Path(args.log).read_text(encoding="utf-8")
    assert "started DocCropper with PID 123" in log_content
    assert captured_commands["cmd"][0] == sys.executable
    assert captured_commands["cwd"] == args.cwd


def test_launch_app_immediate_failure(monkeypatch, tmp_path):
    import scripts.launch_app as launch_app

    class FailingProc:
        pid = 456

        def poll(self):  # pragma: no cover - invoked indirectly
            return 1

    monkeypatch.setattr(launch_app.subprocess, "Popen", lambda *_, **__: FailingProc())
    monkeypatch.setattr(launch_app.time, "sleep", lambda *_: None)

    args = _build_args(tmp_path, "failure.log")
    result = launch_app.launch(args)

    assert result == 1
    log_content = Path(args.log).read_text(encoding="utf-8")
    assert "exited immediately" in log_content
