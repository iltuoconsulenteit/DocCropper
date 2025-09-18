from __future__ import annotations

import importlib
import sys
import sysconfig
import zipfile


def test_platform_imports_from_embeddable_zip(tmp_path, monkeypatch):
    """Ensure the shim loads ``platform`` from pythonXY.zip archives."""

    base = tmp_path / "python"
    stdlib_dir = base / "Lib"
    stdlib_dir.mkdir(parents=True)

    # Create a minimal pythonXY.zip archive that exposes a stub platform module
    # with a distinct marker so we can assert it was loaded.
    zip_path = base / "python311.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("platform.py", "ZIP_MARKER = 'zip-stdlib'\n")

    # Simulate running under the embeddable interpreter.
    fake_python = base / "python.exe"
    fake_python.write_text("", encoding="utf-8")

    original_get_path = sysconfig.get_path

    def fake_get_path(name, *args, **kwargs):
        if name == "stdlib":
            return str(stdlib_dir)
        return original_get_path(name, *args, **kwargs)

    monkeypatch.setattr(sysconfig, "get_path", fake_get_path)
    monkeypatch.setattr(sys, "executable", str(fake_python))

    # Remove the previously imported shim so importing ``platform`` below
    # exercises the loader with the fake environment.
    sys.modules.pop("platform", None)

    module = importlib.import_module("platform")
    try:
        assert getattr(module, "ZIP_MARKER", None) == "zip-stdlib"
    finally:
        # Restore the normal module for any later tests.
        sys.modules.pop("platform", None)
        importlib.import_module("platform")
