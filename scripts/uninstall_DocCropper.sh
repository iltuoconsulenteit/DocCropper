#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "Uninstalling DocCropper from $APP_DIR"

if [ -f "$SCRIPT_DIR/stop_DocCropper.sh" ]; then
  "$SCRIPT_DIR/stop_DocCropper.sh" >/dev/null 2>&1 || true
fi

# Backup settings and license into user profile
BACKUP_DIR="$HOME/DocCropperBackup"
mkdir -p "$BACKUP_DIR"/env
if [ -f "$APP_DIR/settings.json" ]; then
  cp "$APP_DIR/settings.json" "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -f "$APP_DIR/env/license.env" ]; then
  cp "$APP_DIR/env/license.env" "$BACKUP_DIR/env/license.env" 2>/dev/null || true
fi
echo "Config and license backed up to $BACKUP_DIR"

cd / >/dev/null 2>&1
sudo rm -rf "$APP_DIR"

echo "Uninstallation complete."
