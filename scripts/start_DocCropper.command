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

# Copy default environment files if missing
if [ ! -f "$APP_DIR/.env" ] && [ -f "$APP_DIR/.env.example" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
fi
if [ ! -f "$APP_DIR/env/auth.env" ] && [ -f "$APP_DIR/env/auth.env.example" ]; then
  mkdir -p "$APP_DIR/env"
  cp "$APP_DIR/env/auth.env.example" "$APP_DIR/env/auth.env"
fi

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

# Detect running tray via PID file
TRAY_PID_FILE=$(python3 - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper_tray.pid'))
PY
)
if [ -f "$TRAY_PID_FILE" ]; then
  TPID=$(cat "$TRAY_PID_FILE")
  if ps -p "$TPID" >/dev/null 2>&1; then
    TRAY_RUNNING=1
  else
    TRAY_RUNNING=0
    rm -f "$TRAY_PID_FILE"
  fi
else
  TRAY_RUNNING=0
fi

# Check if server already running via PID file
PID_FILE=$(python3 - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper.pid'))
PY
)
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if ps -p "$PID" >/dev/null 2>&1; then
    SERVER_RUNNING=1
  else
    SERVER_RUNNING=0
    rm -f "$PID_FILE"
  fi
else
  SERVER_RUNNING=0
fi

if [ "$TRAY_RUNNING" -eq 0 ]; then
  echo "Starting tray helper..."
  python3 doccropper_tray.py &
  sleep 2
  if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") >/dev/null 2>&1; then
    SERVER_RUNNING=1
  else
    SERVER_RUNNING=0
  fi
fi

OPEN_URL="${DOCROPPER_OPEN_URL:-http://127.0.0.1:$PORT/}"

if [ "$SERVER_RUNNING" -eq 1 ]; then
  echo "DocCropper already running on port $PORT"
  open "$OPEN_URL"
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
open "$OPEN_URL"
if [ "$DOCROPPER_TUNNEL" = "true" ] && command -v cloudflared >/dev/null; then
  echo "Starting Cloudflare Tunnel..."
  cloudflared tunnel --url http://localhost:$PORT > "$TMPDIR/doccropper_tunnel.log" 2>&1 &
fi
