#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  exec sudo "$0" "$@"
fi

SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
else
  APP_DIR="$SCRIPT_DIR/.."
fi
cd "$APP_DIR" || exit 1

mkdir -p env temp
LOGFILE="temp/license_setup.log"
log(){ echo "$(date -u) $1" >> "$LOGFILE"; }

log "License setup started"
read -p "Enter license key: " KEY
read -p "Enter license name: " NAME
log "Key entered"

ENVFILE="env/developer.env"
{
echo "DOCROPPER_LICENSE_KEY=$KEY"
echo "DOCROPPER_LICENSE_NAME=$NAME"
echo "DOCROPPER_DEV_LICENSE=$KEY"
echo "DOCROPPER_LICENSE_LEVEL=developer"
echo "DOCROPPER_DEV_PASSWORD=87654321"
echo "DOCROPPER_SETTINGS_PASSWORD=12345678"
} > "$ENVFILE" && log "Wrote $ENVFILE"

python3 - <<PY && log("Updated settings.json")
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
echo "Log written to $LOGFILE"
log "License setup completed"
