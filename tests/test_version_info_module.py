from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import importlib.util

ROOT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT_DIR / "services" / "api" / "version_info.py"
spec = importlib.util.spec_from_file_location("version_info", MODULE_PATH)
version_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(version_module)  # type: ignore[assignment]
get_version_info = version_module.get_version_info


def test_get_version_info_uses_environment(monkeypatch):
    monkeypatch.setenv("DOCROPPER_VERSION", "env1234")
    monkeypatch.setenv("DOCROPPER_VERSION_DATE", "2025-01-31")

    version, date = get_version_info(Path.cwd())

    assert version == "env1234"
    assert date == "2025-01-31"


def test_get_version_info_reads_version_env(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DOCROPPER_VERSION", raising=False)
    monkeypatch.delenv("DOCROPPER_VERSION_DATE", raising=False)

    env_dir = tmp_path / "env"
    env_dir.mkdir()
    env_file = env_dir / "version.env"
    env_file.write_text(
        "DOCROPPER_VERSION=zip1234\nDOCROPPER_VERSION_DATE=2025-03-04\n",
        encoding="utf-8",
    )

    version, date = get_version_info(tmp_path)

    assert version == "zip1234"
    assert date == "2025-03-04"


def test_get_version_info_reads_last_commit(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DOCROPPER_VERSION", raising=False)
    monkeypatch.delenv("DOCROPPER_VERSION_DATE", raising=False)

    commit = "abcdef1234567890"
    marker = tmp_path / "last_commit"
    marker.write_text(commit, encoding="utf-8")
    timestamp = datetime(2024, 12, 25, 10, 30).timestamp()
    os.utime(marker, (timestamp, timestamp))

    version, date = get_version_info(tmp_path)

    assert version == commit[:7]
    assert date == datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def test_get_version_info_reads_git_head(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DOCROPPER_VERSION", raising=False)
    monkeypatch.delenv("DOCROPPER_VERSION_DATE", raising=False)

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    head = git_dir / "HEAD"
    commit = "1234567890abcdef1234567890abcdef12345678"
    head.write_text(commit, encoding="utf-8")
    timestamp = datetime(2023, 6, 1, 12, 0).timestamp()
    os.utime(head, (timestamp, timestamp))

    version, date = get_version_info(tmp_path)

    assert version == commit[:7]
    assert date == datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
