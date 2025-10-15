"""Utility to expose DocCropper build metadata outside the API server."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_helpers():
    base_dir = Path(__file__).resolve().parents[1]
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    from services.api.version_info import get_version_info  # noqa: WPS433 (runtime import)

    return get_version_info, base_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print DocCropper version info")
    parser.add_argument("--print-env", action="store_true", help="Emit DOCROPPER_* assignments")
    args = parser.parse_args(argv)

    get_version_info, base_dir = _load_helpers()
    version, date = get_version_info(base_dir)

    if args.print_env:
        print(f"DOCROPPER_VERSION={version}")
        if date:
            print(f"DOCROPPER_VERSION_DATE={date}")
    else:
        print(version)
        if date:
            print(date)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

