#!/usr/bin/env python3
"""Determine which requirements need installation.

This helper reads a requirements-style file, filters out entries that are
already satisfied in the current interpreter, and writes the remaining
requirements to an output file. The batch wrappers can then ask pip to install
just the missing or out-of-spec packages instead of forcing reinstallations.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from typing import Any

try:  # pragma: no cover - exercised in integration tests
    from packaging.requirements import Requirement  # type: ignore
    from packaging.markers import default_environment  # type: ignore
    from packaging.utils import canonicalize_name  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Windows embeddable Python may miss packaging
    try:
        from pip._vendor.packaging.requirements import Requirement  # type: ignore
        from pip._vendor.packaging.markers import default_environment  # type: ignore
        from pip._vendor.packaging.utils import canonicalize_name  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - extremely unlikely
        Requirement = None  # type: ignore
        default_environment = None  # type: ignore
        canonicalize_name = None  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirements", type=Path, help="Path to requirements.txt")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="File that will receive the subset of requirements needing install",
    )
    return parser.parse_args()


PACKAGING_AVAILABLE = Requirement is not None and default_environment is not None
if os.environ.get("ENSURE_REQUIREMENTS_FORCE_SIMPLE") == "1":
    PACKAGING_AVAILABLE = False

_SIMPLE_REQ_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_.-]+)"  # package name
    r"(?:\[[^\]]*\])?"  # optional extras, ignored for matching
    r"\s*(?P<operator>==)?\s*"  # currently we only support == in the fallback
    r"(?P<version>[A-Za-z0-9_.+-]+)?\s*$"
)

_INSTALLED_CACHE: dict[str, str] = {}
_METADATA_SCANNED = False
_PIP_LIST_SCANNED = False
_USE_PIP_ONLY = os.environ.get("ENSURE_REQUIREMENTS_USE_PIP_LIST") == "1"


def requirement_applies(req: Any) -> bool:
    if not PACKAGING_AVAILABLE:
        return True
    if req.marker is None:
        return True
    try:
        env = default_environment()
    except Exception:  # pragma: no cover - defensive, shouldn't occur
        return True
    return req.marker.evaluate(env)


def needs_install(req: Any) -> bool:
    if not PACKAGING_AVAILABLE:
        raise RuntimeError("packaging requirement unavailable")
    if not requirement_applies(req):
        return False
    installed_version = lookup_installed(req.name)
    if installed_version is None:
        return True
    if not req.specifier:
        return False
    return not req.specifier.contains(installed_version, prereleases=True)


def lookup_installed(name: str) -> str | None:
    """Return the installed version for *name* if available."""

    if canonicalize_name is None:  # pragma: no cover - packaging unavailable
        normalized = name.lower().replace("_", "-")
    else:
        normalized = canonicalize_name(name)

    cached = _INSTALLED_CACHE.get(normalized)
    if cached is not None:
        return cached

    if not _USE_PIP_ONLY:
        try:
            version = metadata.version(name)
        except metadata.PackageNotFoundError:
            version = None
        except Exception:  # pragma: no cover - defensive
            version = None
        if version is not None:
            _INSTALLED_CACHE[normalized] = version
            return version

        _populate_from_metadata()
        cached = _INSTALLED_CACHE.get(normalized)
        if cached is not None:
            return cached

    _populate_from_pip()
    return _INSTALLED_CACHE.get(normalized)


def _populate_from_metadata() -> None:
    global _METADATA_SCANNED
    if _METADATA_SCANNED or _USE_PIP_ONLY:
        return
    _METADATA_SCANNED = True
    try:
        for dist in metadata.distributions():
            name = dist.metadata.get("Name")
            if not name:
                continue
            if canonicalize_name is None:  # pragma: no cover
                normalized = name.lower().replace("_", "-")
            else:
                normalized = canonicalize_name(name)
            _INSTALLED_CACHE[normalized] = dist.version
    except Exception:  # pragma: no cover - safety net
        pass


def _populate_from_pip() -> None:
    global _PIP_LIST_SCANNED
    if _PIP_LIST_SCANNED:
        return
    _PIP_LIST_SCANNED = True
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:  # pragma: no cover - interpreter missing pip module
        return

    if result.returncode != 0:
        return

    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError:  # pragma: no cover - pip emitted unexpected text
        return

    for entry in entries:
        name = entry.get("name")
        version = entry.get("version")
        if not name or not version:
            continue
        if canonicalize_name is None:  # pragma: no cover
            normalized = name.lower().replace("_", "-")
        else:
            normalized = canonicalize_name(name)
        _INSTALLED_CACHE.setdefault(normalized, version)


def main() -> int:
    args = parse_args()
    requirements_path = args.requirements
    output_path = args.output

    if not requirements_path.exists():
        print(f"[ensure] requirements file not found: {requirements_path}", file=sys.stderr)
        return 1

    if Requirement is None:
        print(
            "[ensure] packaging module unavailable; cannot analyze requirements",
            file=sys.stderr,
        )
        return 1

    lines_to_install: list[str] = []
    try:
        raw_text = requirements_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - rely on caller to log the error
        print(f"[ensure] unable to read {requirements_path}: {exc}", file=sys.stderr)
        return 1

    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if PACKAGING_AVAILABLE:
            try:
                req = Requirement(stripped)
            except Exception as exc:  # pragma: no cover - invalid requirement
                print(
                    f"[ensure] skipping invalid requirement '{raw_line}': {exc}",
                    file=sys.stderr,
                )
                lines_to_install.append(stripped)
                continue
            try:
                if needs_install(req):
                    lines_to_install.append(stripped)
            except RuntimeError:
                # Extremely defensive: if packaging suddenly disappears mid-run,
                # fall back to the simplified checker.
                if _fallback_needs_install(stripped):
                    lines_to_install.append(stripped)
        else:
            if _fallback_needs_install(stripped):
                lines_to_install.append(stripped)

    try:
        if lines_to_install:
            output_path.write_text("\n".join(lines_to_install) + "\n", encoding="utf-8")
        else:
            # Ensure the file exists but is empty so callers can detect the state.
            output_path.write_text("", encoding="utf-8")
    except OSError as exc:  # pragma: no cover - relies on caller handling failures
        print(f"[ensure] unable to write {output_path}: {exc}", file=sys.stderr)
        return 1

    print(
        f"[ensure] requirements satisfied: {len(lines_to_install) == 0}; "
        f"pending installs: {len(lines_to_install)}"
    )
    return 0


def _fallback_needs_install(raw_line: str) -> bool:
    """Best-effort requirement evaluator used when ``packaging`` is unavailable.

    The fallback understands the common ``package==version`` pattern and ignores
    extras. Any requirement it cannot safely evaluate is treated as needing
    installation to stay on the safe side.
    """

    marker_split = raw_line.split(";", 1)
    requirement_text = marker_split[0].strip()
    # Without packaging we cannot evaluate environment markers reliably, so we
    # conservatively assume they apply to the current interpreter.

    match = _SIMPLE_REQ_RE.match(requirement_text)
    if not match:
        return True

    name = match.group("name")
    operator = match.group("operator")
    version = match.group("version")

    installed_version = lookup_installed(name)
    if installed_version is None:
        return True

    if not operator:
        # No version specifier -> already satisfied if package exists.
        return False

    if operator == "==" and version is not None:
        return installed_version != version

    # Unsupported operator; force installation to ensure correctness.
    return True


if __name__ == "__main__":
    sys.exit(main())
