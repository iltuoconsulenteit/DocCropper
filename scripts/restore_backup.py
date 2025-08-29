#!/usr/bin/env python
"""Restore files from a backup created by backup_now.py."""

import argparse
import sys
from pathlib import Path

# Ensure repository root is on the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.utils.backup import restore_backup


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore a DocCropper backup")
    parser.add_argument("timestamp", help="Timestamp of the backup to restore")
    args = parser.parse_args()
    restore_backup(args.timestamp)
    print("Backup restored.")


if __name__ == "__main__":
    main()
