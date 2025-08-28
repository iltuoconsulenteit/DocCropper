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

OPEN_URL="${DOCROPPER_OPEN_URL:-http://127.0.0.1:$PORT/}"

if [ "$SERVER_RUNNING" -eq 1 ]; then
  echo "DocCropper already running on port $PORT"
  if command -v xdg-open >/dev/null; then xdg-open "$OPEN_URL" >/dev/null 2>&1; fi
  exit 0
fi

# Setup virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip >/dev/null
REQ_HASH=$(md5sum requirements.txt | cut -d' ' -f1)
HASH_FILE="venv/requirements.hash"
if [ ! -f "$HASH_FILE" ] || [ "$REQ_HASH" != "$(cat "$HASH_FILE" 2>/dev/null)" ]; then
  pip install -r requirements.txt >/dev/null
  echo "$REQ_HASH" > "$HASH_FILE"
fi

# Stop any running instance without importing plugins
PID_FILE=$(python3 - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper.pid'))
PY
)
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if ps -p "$PID" >/dev/null 2>&1; then
    kill "$PID" 2>/dev/null || sudo -n kill "$PID" || true
  fi
  rm -f "$PID_FILE" 2>/dev/null || sudo -n rm -f "$PID_FILE" || true
fi

echo "Starting DocCropper on port $PORT..."
python3 main.py --host 0.0.0.0 --port "$PORT" &
sleep 2
if [ "$TRAY_RUNNING" -eq 0 ]; then
  echo "Starting tray helper..."
  python3 doccropper_tray.py &
fi
if command -v xdg-open >/dev/null; then
  xdg-open "$OPEN_URL" >/dev/null 2>&1 || true
fi
if [ "${DOCROPPER_TUNNEL}" = "true" ] && command -v cloudflared >/dev/null; then
  echo "Starting Cloudflare Tunnel..."
  cloudflared tunnel --url http://localhost:$PORT > "${TMPDIR:-/tmp}/doccropper_tunnel.log" 2>&1 &
fi
