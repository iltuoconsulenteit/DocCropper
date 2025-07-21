#!/bin/bash
set -e
APP_DIR="${DOCROPPER_HOME:-$(cd "$(dirname "$0")/.." && pwd)}"
if [ ! -f "$APP_DIR/venv/bin/activate" ]; then
    echo "DocCropper not installed at $APP_DIR" >&2
    exit 1
fi
source "$APP_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/scanner_requirements.txt"
echo "Scanning support installed"
