#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../main.py" ]; then
  APP_DIR="$(dirname "$SCRIPT_DIR")"
else
  echo "Unable to locate DocCropper directory relative to $SCRIPT_DIR" >&2
  exit 1
fi
cd "$APP_DIR"

# Determine port from settings
PORT=$(python3 - <<'PY'
import json
try:
    with open('settings.json') as f:
        data=json.load(f)
    print(data.get('port',8765))
except Exception:
    print(8765)
PY
)

# Setup virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# Stop any running instance
python3 main.py --stop >/dev/null 2>&1 || true

echo "Starting DocCropper on port $PORT..."
python3 main.py --host 0.0.0.0 --port "$PORT" &
sleep 2
xdg-open "http://127.0.0.1:$PORT/" >/dev/null 2>&1 || true
