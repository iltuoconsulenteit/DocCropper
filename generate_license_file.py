#!/usr/bin/env python3
"""Simple license file generator.

This utility creates a `.dcl` license file based on the provided
fingerprint.  The generated file is written to the ``temp`` directory and
the absolute path is printed to stdout so callers can handle the file as
needed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a DocCropper license file")
    parser.add_argument("--fingerprint", required=True, help="Client fingerprint")
    args = parser.parse_args()

    out_dir = Path("temp")
    out_dir.mkdir(exist_ok=True)
    license_path = out_dir / f"{args.fingerprint}.dcl"

    data = {"fingerprint": args.fingerprint}
    with open(license_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)

    # Print the path so callers (e.g. webhook) can capture it
    print(license_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

