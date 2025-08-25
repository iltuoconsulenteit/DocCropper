#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
cd "$APP_DIR"

PY="python3"
if [ -x "venv/bin/python" ]; then
  PY="venv/bin/python"
fi

LOG_FILE="$($PY - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper_stop.log'))
PY
)"
log(){
  echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >>"$LOG_FILE"
}
log "Stop requested"

PID_FILE="$($PY - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper.pid'))
PY
)"
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if ps -p "$PID" >/dev/null 2>&1; then
    kill "$PID" 2>/dev/null || sudo -n kill "$PID" || true
    sleep 1
    if ps -p "$PID" >/dev/null 2>&1; then
      kill -9 "$PID" 2>/dev/null || sudo -n kill -9 "$PID" || true
      log "Force killed DocCropper PID $PID"
    else
      log "Stopped DocCropper PID $PID"
    fi
  fi
  rm -f "$PID_FILE" 2>/dev/null || sudo -n rm -f "$PID_FILE" || true
fi

TRAY_PID_FILE="$($PY - <<'PY'
import tempfile, os
print(os.path.join(tempfile.gettempdir(), 'doccropper_tray.pid'))
PY
)"
if [ -f "$TRAY_PID_FILE" ]; then
  TPID=$(cat "$TRAY_PID_FILE")
  if ps -p "$TPID" >/dev/null 2>&1; then
    kill "$TPID" 2>/dev/null || sudo -n kill "$TPID" || true
    sleep 1
    if ps -p "$TPID" >/dev/null 2>&1; then
      kill -9 "$TPID" 2>/dev/null || sudo -n kill -9 "$TPID" || true
      log "Force killed tray helper PID $TPID"
    else
      log "Stopped tray helper PID $TPID"
    fi
  fi
  rm -f "$TRAY_PID_FILE" 2>/dev/null || sudo -n rm -f "$TRAY_PID_FILE"
fi

# Fallback: kill processes by name if PID files not present or stale
if [ ! -f "$PID_FILE" ]; then
  PIDS=$(pgrep -f "$APP_DIR/main.py" || true)
  if [ -n "$PIDS" ]; then
    log "Stopping DocCropper processes: $PIDS"
    kill $PIDS 2>/dev/null || sudo -n kill $PIDS || true
  fi
fi

if [ ! -f "$TRAY_PID_FILE" ]; then
  TPIDS=$(pgrep -f doccropper_tray || true)
  if [ -n "$TPIDS" ]; then
    kill $TPIDS 2>/dev/null || sudo -n kill $TPIDS || true
    log "Stopped stray tray helper ($TPIDS)"
  fi
fi
log "Stop script completed"
