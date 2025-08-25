#!/bin/sh
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
else
  APP_DIR="$SCRIPT_DIR/.."
fi
cd "$APP_DIR" || exit 1

mkdir -p env
printf "Enter license key: "
read KEY
printf "Enter license name: "
read NAME

ENVFILE="env/developer.env"
echo "DOCROPPER_LICENSE_KEY=$KEY" > "$ENVFILE"
echo "DOCROPPER_LICENSE_NAME=$NAME" >> "$ENVFILE"
echo "DOCROPPER_DEV_LICENSE=$KEY" >> "$ENVFILE"
echo "DOCROPPER_LICENSE_LEVEL=developer" >> "$ENVFILE"
echo "DOCROPPER_DEV_PASSWORD=87654321" >> "$ENVFILE"
echo "DOCROPPER_SETTINGS_PASSWORD=12345678" >> "$ENVFILE"

SETTINGS_FILE="settings.json"
python3 - "$SETTINGS_FILE" "$KEY" "$NAME" <<'PY'
import json, sys, os
settings_file, key, name = sys.argv[1:4]
data = {}
if os.path.exists(settings_file):
    try:
        with open(settings_file) as f:
            data = json.load(f)
    except Exception:
        pass
data["license_key"] = key
data["license_name"] = name
data["license_level"] = "developer"
with open(settings_file, "w") as f:
    json.dump(data, f, indent=2)
PY

echo "Developer license saved to $ENVFILE and $SETTINGS_FILE updated"
