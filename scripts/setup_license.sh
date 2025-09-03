#!/bin/sh
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/main.py" ]; then
  APP_DIR="$SCRIPT_DIR"
else
  APP_DIR="$SCRIPT_DIR/.."
fi
cd "$APP_DIR" || exit 1

mkdir -p env
printf "Enter manual license key: "
read KEY
printf "Enter license name: "
read NAME

ENVFILE="env/license.env"
{ 
  echo "DOCROPPER_MANUAL_LICENSE=$KEY"
  echo "DOCROPPER_LICENSE_KEY=$KEY"
  echo "DOCROPPER_LICENSE_NAME=$NAME"
  echo "LICENSE_CHECK=false"
} > "$ENVFILE"

# Update settings.json so the application immediately recognises the key
python3 - "$KEY" "$NAME" <<'PY'
import json,sys,urllib.request,shutil,pathlib,time
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
for p in pathlib.Path('.').rglob('__pycache__'):
    shutil.rmtree(p, ignore_errors=True)
try:
    req=urllib.request.Request('http://localhost:8765/restart/', data=b'', method='POST')
    urllib.request.urlopen(req, timeout=2)
    time.sleep(1)
except Exception:
    pass
PY

echo "Manual license saved to $ENVFILE and settings.json updated"
