#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
cd "$APP_DIR"

PY="python3"
if [ -x "venv/bin/python" ]; then
  PY="venv/bin/python"
fi

"$PY" main.py --stop || sudo "$PY" main.py --stop || true

TRAY_PID_FILE="$($PY - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper_tray.pid'))
PY
)"
if [ -f "$TRAY_PID_FILE" ] && ps -p "$(cat "$TRAY_PID_FILE")" >/dev/null 2>&1; then
  kill "$(cat "$TRAY_PID_FILE")" 2>/dev/null || sudo kill "$(cat "$TRAY_PID_FILE")"
  rm -f "$TRAY_PID_FILE" 2>/dev/null || sudo rm -f "$TRAY_PID_FILE"
  echo "Stopped tray helper"
fi
