#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    echo "Re-running with sudo..."
    exec sudo "$0" "$@"
  else
    echo "Please run this uninstaller as root." >&2
    exit 1
  fi
fi

DEFAULT_DIR="/opt/DocCropper"
read -r -p "Uninstall directory [$DEFAULT_DIR]: " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}

read -r -p "Remove $TARGET_DIR ? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

if [ -f "$TARGET_DIR/scripts/stop_DocCropper.sh" ]; then
  bash "$TARGET_DIR/scripts/stop_DocCropper.sh"
fi

# run uninstall cleanup to remove config files
if [ -f "$TARGET_DIR/scripts/uninstall_DocCropper.sh" ]; then
  bash "$TARGET_DIR/scripts/uninstall_DocCropper.sh"
fi

# move outside of target directory before removing it
cd /tmp
rm -rf "$TARGET_DIR"
echo "DocCropper uninstalled."
