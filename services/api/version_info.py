from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple


BASE_DIR = Path(__file__).resolve().parents[2]


def _read_version_env(path: Path) -> tuple[str, str]:
    """Return version metadata stored in ``env/version.env`` if available."""

    version = ""
    date = ""
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.upper().startswith("DOCROPPER_VERSION="):
                version = line.split("=", 1)[1].strip()
            elif line.upper().startswith("DOCROPPER_VERSION_DATE="):
                date = line.split("=", 1)[1].strip()
    except OSError:
        return "", ""

    return version, date


def _shorten(commit: str | None) -> str:
    if not commit:
        return ""
    commit = commit.strip()
    if len(commit) > 40:
        # git hashes are 40 chars; trim anything longer just in case
        commit = commit[:40]
    if len(commit) > 7:
        return commit[:7]
    return commit


def _read_git_commit(git_dir: Path) -> tuple[str, Path | None]:
    head_path = git_dir / "HEAD"
    try:
        head_data = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "", None

    ref_path: Path | None = None
    commit = ""

    if head_data.startswith("ref:"):
        ref = head_data.split(" ", 1)[1].strip()
        ref_path = git_dir / ref
        try:
            commit = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            packed_path = git_dir / "packed-refs"
            try:
                with open(packed_path, "r", encoding="utf-8") as pf:
                    for line in pf:
                        line = line.strip()
                        if not line or line.startswith("#") or line.startswith("^"):
                            continue
                        parts = line.split()
                        if len(parts) == 2 and parts[1] == ref:
                            commit = parts[0]
                            break
            except OSError:
                commit = ""
    else:
        commit = head_data
        ref_path = head_path

    return commit, ref_path


def get_version_info(base_dir: Path | None = None) -> Tuple[str, str]:
    """Return the current application version and commit date.

    The lookup prefers the current Git HEAD but gracefully falls back to the
    ``last_commit`` marker written during installation or to the raw contents
    of ``.git/HEAD`` so that packaged builds without Git still expose their
    revision.
    """

    if base_dir is None:
        base_dir = BASE_DIR

    env_version = (os.getenv("DOCROPPER_VERSION") or "").strip()
    env_date = (os.getenv("DOCROPPER_VERSION_DATE") or "").strip()

    if env_version:
        return env_version, env_date

    version = ""
    date = env_date

    version_env = base_dir / "env" / "version.env"
    if version_env.is_file():
        file_version, file_date = _read_version_env(version_env)
        if file_version:
            version = file_version.strip()
        if not date and file_date:
            date = file_date.strip()

    if not version:
        try:
            version = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=base_dir,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            date = (
                subprocess.check_output(
                    ["git", "log", "-1", "--format=%cd", "--date=short"],
                    cwd=base_dir,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
        except Exception:
            version = ""
            date = ""

    if not version:
        last_commit_path = base_dir / "last_commit"
        try:
            if last_commit_path.exists():
                candidate = last_commit_path.read_text(encoding="utf-8").strip()
                if candidate:
                    version = _shorten(candidate)
                if not date:
                    try:
                        mtime = last_commit_path.stat().st_mtime
                        date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                    except OSError:
                        date = ""
        except OSError:
            pass

    if not version:
        git_dir = base_dir / ".git"
        commit, ref_path = _read_git_commit(git_dir)
        if commit:
            version = _shorten(commit)
            if not date:
                target = ref_path if ref_path and ref_path.exists() else git_dir / "HEAD"
                try:
                    mtime = target.stat().st_mtime
                    date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                except OSError:
                    pass

    if not version:
        version = "unknown"

    return version, date


def get_cache_bust(base_dir: Path | None = None) -> str:
    version, _ = get_version_info(base_dir=base_dir)
    return f"?v={version}" if version != "unknown" else ""


__all__ = ["get_version_info", "get_cache_bust"]

