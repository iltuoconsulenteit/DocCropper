#!/usr/bin/env python
"""Create a backup of the database and configuration files."""

import sys
from pathlib import Path

# Ensure repository root is on the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.utils.backup import backup_all


def main() -> None:
    path = backup_all()
    print(f"Backup created at {path}")


if __name__ == "__main__":
    main()
