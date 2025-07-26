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

PORT=$(python3 - <<'PY'
import json
try:
    with open('settings.json') as f:
        d=json.load(f)
    print(d.get('port',8765))
except Exception:
    print(8765)
PY
)

# Detect running tray
if pgrep -f doccropper_tray.py >/dev/null 2>&1; then
  TRAY_RUNNING=1
else
  TRAY_RUNNING=0
fi

# Check if server already running via PID file
PID_FILE=$(python3 - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper.pid'))
PY
)
if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") >/dev/null 2>&1; then
  SERVER_RUNNING=1
else
  SERVER_RUNNING=0
fi

if [ "$TRAY_RUNNING" -eq 0 ]; then
  echo "Starting tray helper..."
  python3 doccropper_tray.py --auto-start &
  sleep 2
  if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") >/dev/null 2>&1; then
    SERVER_RUNNING=1
  else
    SERVER_RUNNING=0
  fi
fi

if [ "$SERVER_RUNNING" -eq 1 ]; then
  echo "DocCropper already running on port $PORT"
  open "http://127.0.0.1:$PORT/"
  exit 0
fi

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
open "http://127.0.0.1:$PORT/"
if [ "$DOCROPPER_TUNNEL" = "true" ] && command -v cloudflared >/dev/null; then
  echo "Starting Cloudflare Tunnel..."
  cloudflared tunnel --url http://localhost:$PORT > "$TMPDIR/doccropper_tunnel.log" 2>&1 &
fi
