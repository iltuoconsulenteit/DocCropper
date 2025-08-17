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
echo "DOCROPPER_LICENSE_LEVEL=full" >> "$ENVFILE"
echo "DOCROPPER_DEV_PASSWORD=87654321" >> "$ENVFILE"

echo "Developer license saved to $ENVFILE"
