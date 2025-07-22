#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/.."
cd "$APP_DIR"
if [ ! -f scanner_requirements.txt ]; then
  echo "scanner_requirements.txt not found"
  exit 1
fi
if [ ! -d venv ]; then
  echo "Run install_DocCropper.sh first to create the environment.";
  exit 1
fi
source venv/bin/activate
pip install -r scanner_requirements.txt
echo "Scanner add-on installed"

