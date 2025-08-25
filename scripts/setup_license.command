#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
else
  APP_DIR="$SCRIPT_DIR/.."
fi
cd "$APP_DIR" || exit 1

mkdir -p env
read -p "Enter license key: " KEY
read -p "Enter license name: " NAME

ENVFILE="env/developer.env"
echo "DOCROPPER_LICENSE_KEY=$KEY" > "$ENVFILE"
echo "DOCROPPER_LICENSE_NAME=$NAME" >> "$ENVFILE"
echo "DOCROPPER_DEV_LICENSE=$KEY" >> "$ENVFILE"
echo "DOCROPPER_LICENSE_LEVEL=developer" >> "$ENVFILE"
echo "DOCROPPER_DEV_PASSWORD=87654321" >> "$ENVFILE"
echo "DOCROPPER_SETTINGS_PASSWORD=12345678" >> "$ENVFILE"
python3 - <<PY
import json, sys
path = 'settings.json'
try:
    with open(path) as f:
        data = json.load(f)
except Exception:
    data = {}
data['license_key'] = '$KEY'
data['license_name'] = '$NAME'
data['license_level'] = 'developer'
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
PY
rm -f license_overrides.json

echo "Developer license saved to $ENVFILE and settings.json"
