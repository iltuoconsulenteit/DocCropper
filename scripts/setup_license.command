#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
else
  APP_DIR="$SCRIPT_DIR/.."
fi
cd "$APP_DIR" || exit 1

mkdir -p env
read -p "Enter manual license key: " KEY
read -p "Enter license name: " NAME

ENVFILE="env/license.env"
{ 
  echo "DOCROPPER_MANUAL_LICENSE=$KEY"
  echo "DOCROPPER_LICENSE_KEY=$KEY"
  echo "DOCROPPER_LICENSE_NAME=$NAME"
  echo "LICENSE_CHECK=false"
} > "$ENVFILE"

# Update settings.json for immediate use
python3 - "$KEY" "$NAME" <<'PY'
import json,sys
key,name=sys.argv[1],sys.argv[2]
path="settings.json"
try:
    with open(path) as f:
        data=json.load(f)
except Exception:
    data={}
data["license_key"]=key
data["license_name"]=name
data["license_check"]=False
with open(path,"w") as f:
    json.dump(data,f)
PY

echo "Manual license saved to $ENVFILE and settings.json updated"
