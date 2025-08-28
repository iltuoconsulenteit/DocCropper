#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
cd "$APP_DIR"

# Stop running DocCropper processes
if [ -x "$SCRIPT_DIR/stop_DocCropper.sh" ]; then
  "$SCRIPT_DIR/stop_DocCropper.sh" >/dev/null 2>&1 || true
fi

# Remove temp log files
rm -f /tmp/DocCropper_start.log /tmp/doccropper_tray.log /tmp/doccropper_stop.log 2>/dev/null || true

# Remove virtual environment and install directory
rm -rf venv install 2>/dev/null || true

# Remove database file
rm -f db.sqlite3 2>/dev/null || true

# Remove configuration and license files
rm -f settings.json 2>/dev/null || true
rm -rf env 2>/dev/null || true

# Remove PID files
rm -f /tmp/doccropper.pid /tmp/doccropper_tray.pid 2>/dev/null || true

echo "DocCropper files removed where possible."
