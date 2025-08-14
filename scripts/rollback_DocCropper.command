#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
PREV_FILE="$APP_DIR/previous_commit"
if [ ! -f "$PREV_FILE" ]; then
  echo "No previous commit information found." >&2
  exit 1
fi
HASH="$(cat "$PREV_FILE")"
cd "$APP_DIR"
if git rev-parse "$HASH" >/dev/null 2>&1; then
  git reset --hard "$HASH"
  echo "Restored to commit $HASH"
else
  echo "Stored commit $HASH not found." >&2
  exit 1
fi
