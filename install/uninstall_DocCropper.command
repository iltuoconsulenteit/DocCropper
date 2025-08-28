#!/bin/bash
set -e
DEFAULT_DIR="/Applications/DocCropper"
read -r -p "Uninstall directory [$DEFAULT_DIR]: " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}

read -r -p "Remove $TARGET_DIR ? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

if [ -f "$TARGET_DIR/scripts/stop_DocCropper.command" ]; then
  bash "$TARGET_DIR/scripts/stop_DocCropper.command"
fi

# run uninstall cleanup to remove config files
if [ -f "$TARGET_DIR/scripts/uninstall_DocCropper.command" ]; then
  bash "$TARGET_DIR/scripts/uninstall_DocCropper.command"
fi

# move outside of target directory before removing it
cd /tmp
rm -rf "$TARGET_DIR"
echo "DocCropper uninstalled."
