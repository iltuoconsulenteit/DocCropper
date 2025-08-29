from __future__ import annotations

import datetime
import shutil
from pathlib import Path

DB_PATH = Path("db.sqlite3")
CONFIG_FILES = [Path("settings.json"), Path("license_overrides.json")]
BACKUP_ROOT = Path("backups")


def backup_all() -> Path:
    """Create a timestamped backup of the database and config files."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_ROOT / timestamp
    dest.mkdir(parents=True, exist_ok=True)
    for src in [DB_PATH, *CONFIG_FILES]:
        if src.exists():
            shutil.copy2(src, dest / src.name)
    return dest


def restore_backup(timestamp: str) -> None:
    """Restore files from a backup created by :func:`backup_all`."""
    src_dir = BACKUP_ROOT / timestamp
    if not src_dir.exists():
        raise FileNotFoundError(f"Backup '{timestamp}' not found")
    for name in [DB_PATH.name, *(f.name for f in CONFIG_FILES)]:
        src_file = src_dir / name
        if src_file.exists():
            shutil.copy2(src_file, DB_PATH.parent / name)
