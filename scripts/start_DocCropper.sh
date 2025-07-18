#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
cd "$APP_DIR"

# Determine port from settings
PORT=$(python3 - <<'PY'
import json
try:
    with open('settings.json') as f:
        data=json.load(f)
    print(data.get('port',8000))
except Exception:
    print(8000)
PY
)

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create venv"; exit 1; }
fi
source venv/bin/activate
echo "Installing Python packages..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt || { echo "Package installation failed"; exit 1; }

echo "Starting DocCropper on port $PORT..."
python3 main.py --host 0.0.0.0 --port "$PORT"
