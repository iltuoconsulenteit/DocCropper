#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "Uninstalling DocCropper from $APP_DIR"

if [ -f "$SCRIPT_DIR/stop_DocCropper.sh" ]; then
  "$SCRIPT_DIR/stop_DocCropper.sh" >/dev/null 2>&1 || true
fi

sudo rm -rf "$APP_DIR"

echo "Uninstallation complete."
