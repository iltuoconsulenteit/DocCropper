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

echo "Manual license saved to $ENVFILE"
