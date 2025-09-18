from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ensure_requirements.py"


def run_helper(tmp_path: Path, requirements: str, extra_env: dict[str, str] | None = None):
    req_path = tmp_path / "requirements.txt"
    req_path.write_text(requirements, encoding="utf-8")
    output_path = tmp_path / "needs.txt"

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(req_path), "--output", str(output_path)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    return result, output_path


def test_marks_missing_packages(tmp_path):
    result, output_path = run_helper(tmp_path, "not-a-real-package==0.0.1\n")

    assert result.returncode == 0
    assert output_path.read_text(encoding="utf-8").strip() == "not-a-real-package==0.0.1"


def test_skips_already_installed_packages(tmp_path):
    result, output_path = run_helper(tmp_path, "pip\n")

    assert result.returncode == 0
    assert output_path.read_text(encoding="utf-8") == ""


def test_falls_back_to_pip_vendor_packaging(tmp_path):
    stub_dir = tmp_path / "stub"
    (stub_dir / "packaging").mkdir(parents=True)
    (stub_dir / "packaging" / "__init__.py").write_text("", encoding="utf-8")

    original = os.environ.get("PYTHONPATH")
    if original:
        py_path = os.pathsep.join((str(stub_dir), original))
    else:
        py_path = str(stub_dir)
    env = {"PYTHONPATH": py_path}

    result, output_path = run_helper(tmp_path, "pip\n", env)

    assert result.returncode == 0
    assert output_path.read_text(encoding="utf-8") == ""


def test_uses_pip_list_when_metadata_missing(tmp_path):
    env = {"ENSURE_REQUIREMENTS_USE_PIP_LIST": "1"}

    result, output_path = run_helper(tmp_path, "pip\n", env)

    assert result.returncode == 0
    assert output_path.read_text(encoding="utf-8") == ""
