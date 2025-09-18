#!/usr/bin/env python3
"""Determine which requirements need installation.

This helper reads a requirements-style file, filters out entries that are
already satisfied in the current interpreter, and writes the remaining
requirements to an output file. The batch wrappers can then ask pip to install
just the missing or out-of-spec packages instead of forcing reinstallations.
"""
from __future__ import annotations

import argparse
import sys
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.markers import default_environment


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


def requirement_applies(req: Requirement) -> bool:
    if req.marker is None:
        return True
    try:
        env = default_environment()
    except Exception:  # pragma: no cover - defensive, shouldn't occur
        return True
    return req.marker.evaluate(env)


def needs_install(req: Requirement) -> bool:
    if not requirement_applies(req):
        return False
    try:
        installed_version = metadata.version(req.name)
    except metadata.PackageNotFoundError:
        return True
    if not req.specifier:
        return False
    return not req.specifier.contains(installed_version, prereleases=True)


def main() -> int:
    args = parse_args()
    requirements_path = args.requirements
    output_path = args.output

    if not requirements_path.exists():
        print(f"[ensure] requirements file not found: {requirements_path}", file=sys.stderr)
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
        try:
            req = Requirement(stripped)
        except Exception as exc:  # pragma: no cover - invalid requirement
            print(f"[ensure] skipping invalid requirement '{raw_line}': {exc}", file=sys.stderr)
            lines_to_install.append(stripped)
            continue
        if needs_install(req):
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


if __name__ == "__main__":
    sys.exit(main())
