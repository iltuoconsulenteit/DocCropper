#!/bin/bash
set -e

# Require root so we can install under /Applications
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    echo "⚠️  This installer needs administrative privileges. Re-running with sudo..."
    exec sudo "$0" "$@"
  else
    echo "❌ Please run this installer as root." >&2
    exit 1
  fi
fi

REPO_URL="https://github.com/iltuoconsulenteit/DocCropper"
DEV_KEY="${DOCROPPER_DEV_LICENSE:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH_FILE="$SCRIPT_DIR/dev_branch"
if [ -n "$DOCROPPER_DEV_BRANCH" ]; then
  DEV_BRANCH="$DOCROPPER_DEV_BRANCH"
elif [ -f "$BRANCH_FILE" ]; then
  DEV_BRANCH="$(cat "$BRANCH_FILE")"
else
  DEV_BRANCH="work"
fi
echo "$DEV_BRANCH" > "$BRANCH_FILE"

DEFAULT_DIR="/Applications/DocCropper"
read -r -p "Installation directory [$DEFAULT_DIR]: " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}
mkdir -p "$TARGET_DIR"
echo "Installing to: $TARGET_DIR"

# Start logging after we know the target directory
LOG_FILE="${DOCROPPER_LOG_FILE:-$TARGET_DIR/install.log}"
if ! touch "$LOG_FILE" >/dev/null 2>&1; then
  LOG_FILE="/tmp/DocCropper_install.log"
  echo "Cannot write log to $TARGET_DIR. Using $LOG_FILE"
fi
echo "Logging to $LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

LAST_FILE="$TARGET_DIR/last_commit"
PREV_FILE="$TARGET_DIR/previous_commit"


DEFAULT_KEY=""
if [ -f "$TARGET_DIR/settings.json" ]; then
  DEFAULT_KEY=$(python3 - <<PY
import json,sys
try:
    print(json.load(open(sys.argv[1])).get('license_key',''))
except Exception:
    pass
PY
 "$TARGET_DIR/settings.json")
fi
read -r -p "🔑 Enter license key (leave blank for demo) [${DEFAULT_KEY}]: " LIC_KEY
[ -z "$LIC_KEY" ] && LIC_KEY="$DEFAULT_KEY"
UPPER_KEY=$(echo "$LIC_KEY" | tr '[:lower:]' '[:upper:]')
DEV_UPPER=$(echo "$DEV_KEY" | tr '[:lower:]' '[:upper:]')
BRANCH="${DOCROPPER_BRANCH}"
if [ -z "$BRANCH" ]; then
  echo "Choose branch to install:"
  echo " 1) main"
  echo " 2) $DEV_BRANCH"
  read -r -p "Selection [1]: " BSEL
  if [ "$BSEL" = "2" ]; then
    BRANCH="$DEV_BRANCH"
  else
    BRANCH="main"
  fi
fi
echo "Using branch: $BRANCH"


printf '\xF0\x9F\x94\xA7 Verifica pacchetti richiesti...\n'
for cmd in git python3 pip3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ $cmd non trovato" >&2
    exit 1
  fi
done

if [ -f "$TARGET_DIR/scripts/stop_DocCropper.command" ]; then
  echo "🛑 Stopping running DocCropper..."
  bash "$TARGET_DIR/scripts/stop_DocCropper.command" >/dev/null 2>&1 || true
fi

if [ -d "$TARGET_DIR/.git" ]; then
  echo "📁 Repository già presente in $TARGET_DIR"
  read -r -p "🔄 Vuoi aggiornare il repository da GitHub? [s/N] " ans
  if [[ "$ans" =~ ^[sS]$ ]]; then
    if [ -f "$LAST_FILE" ]; then
      cp "$LAST_FILE" "$PREV_FILE"
    else
      git -C "$TARGET_DIR" rev-parse HEAD > "$PREV_FILE" 2>/dev/null || true
    fi
    echo "📥 Aggiornamento repository..."
    git -C "$TARGET_DIR" merge --abort >/dev/null 2>&1 || true
    git -C "$TARGET_DIR" rebase --abort >/dev/null 2>&1 || true
    git -C "$TARGET_DIR" fetch origin "$BRANCH"
    git -C "$TARGET_DIR" reset --hard "origin/$BRANCH"
    git -C "$TARGET_DIR" clean -fd
    git -C "$TARGET_DIR" rev-parse HEAD > "$LAST_FILE" 2>/dev/null || true
  fi
else
  if [ "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]; then
    read -r -p "Directory $TARGET_DIR not empty. Delete contents and continue? [y/N] " wipe
    if [[ "$wipe" =~ ^[yY]$ ]]; then
      rm -rf "$TARGET_DIR"
      mkdir -p "$TARGET_DIR"
    else
      echo "Please choose another directory." >&2
      exit 1
    fi
  fi
  echo "📥 Clonazione repository in $TARGET_DIR..."
  git clone --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
  git -C "$TARGET_DIR" rev-parse HEAD > "$LAST_FILE" 2>/dev/null || true
fi

echo "📜 Ultimi 10 commit:" | tee -a "$LOG_FILE"
git -C "$TARGET_DIR" log -n 10 --pretty=format:"%h | %ad | %s" --date=short | tee -a "$LOG_FILE"
read -r -p "Vuoi ripristinare un commit specifico? (lascia vuoto per continuare): " COMMIT_HASH
if [ -n "$COMMIT_HASH" ]; then
  echo "🔄 Checkout del commit $COMMIT_HASH..." | tee -a "$LOG_FILE"
  git -C "$TARGET_DIR" checkout "$COMMIT_HASH" >>"$LOG_FILE" 2>&1
  git -C "$TARGET_DIR" rev-parse HEAD > "$LAST_FILE" 2>/dev/null || true
fi

printf '\xE2\x9C\x85 Operazione completata.\n'

# Ensure default environment files
if [ ! -f "$TARGET_DIR/.env" ] && [ -f "$TARGET_DIR/.env.example" ]; then
  cp "$TARGET_DIR/.env.example" "$TARGET_DIR/.env"
fi
if [ ! -f "$TARGET_DIR/env/auth.env" ] && [ -f "$TARGET_DIR/env/auth.env.example" ]; then
  mkdir -p "$TARGET_DIR/env"
  cp "$TARGET_DIR/env/auth.env.example" "$TARGET_DIR/env/auth.env"
fi

# Set up virtual environment and install dependencies
cd "$TARGET_DIR"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd - >/dev/null

SETTINGS_FILE="$TARGET_DIR/settings.json"
if [ ! -f "$SETTINGS_FILE" ]; then
  cat > "$SETTINGS_FILE" <<'EOF'
{
  "language": "en",
  "layout": 1,
  "orientation": "portrait",
  "arrangement": "auto",
  "scale_mode": "fit",
  "scale_percent": 100,
  "port": 8765,
  "license_key": "",
  "license_name": ""
}
EOF
fi

if [ -n "$LIC_KEY" ]; then
  UPPER_KEY="$(echo "$LIC_KEY" | tr '[:lower:]' '[:upper:]')"
  DEV_KEY="${DOCROPPER_DEV_LICENSE:-}"
  DEV_KEY_UPPER="$(echo "$DEV_KEY" | tr '[:lower:]' '[:upper:]')"
  VALID=0
  if [ "$UPPER_KEY" = "VALID" ] || [ "$UPPER_KEY" = "$DEV_KEY_UPPER" ]; then
    VALID=1
  elif [[ "$UPPER_KEY" == *-DEV ]]; then
    VALID=1
    DEV_KEY="$LIC_KEY"
    DEV_KEY_UPPER="$UPPER_KEY"
    export DOCROPPER_DEV_LICENSE="$LIC_KEY"
  fi
  if [ $VALID -eq 1 ]; then
    read -r -p "👤 Licensed to: " LIC_NAME
    if [[ "$UPPER_KEY" == *-DEV ]] && [ ! -f "$TARGET_DIR/env/developer.env" ]; then
      mkdir -p "$TARGET_DIR/env"
      cat > "$TARGET_DIR/env/developer.env" <<EOF
DOCROPPER_LICENSE_KEY=$LIC_KEY
DOCROPPER_LICENSE_NAME=$LIC_NAME
DOCROPPER_DEV_LICENSE=$LIC_KEY
DOCROPPER_LICENSE_LEVEL=full
EOF
    fi
    python3 - "$SETTINGS_FILE" "$LIC_KEY" "$LIC_NAME" <<'PY'
import json, sys
f, key, name = sys.argv[1:]
with open(f) as fh:
    data = json.load(fh)
data['license_key'] = key
data['license_name'] = name
with open(f, 'w') as fh:
    json.dump(data, fh)
PY
    echo "✅ License saved"
    DEV_UP=$(echo "$DEV_KEY" | tr '[:lower:]' '[:upper:]')
    if [ "$UPPER_KEY" = "$DEV_UP" ]; then
      echo "🔀 Switching to developer branch $DEV_BRANCH"
      git -C "$TARGET_DIR" fetch origin "$DEV_BRANCH"
      git -C "$TARGET_DIR" checkout "$DEV_BRANCH"
      git -C "$TARGET_DIR" merge --abort >/dev/null 2>&1 || true
      git -C "$TARGET_DIR" rebase --abort >/dev/null 2>&1 || true
      git -C "$TARGET_DIR" reset --hard
      git -C "$TARGET_DIR" clean -fd
      git -C "$TARGET_DIR" pull --rebase --autostash origin "$DEV_BRANCH"
    fi
  else
    echo "❌ License key invalid. Continuing in demo mode."
  fi
else
  echo "ℹ️  Demo mode enabled"
fi

read -r -p "🚀 Launch DocCropper with tray icon now? [y/N] " RUN_APP
if [[ "$RUN_APP" =~ ^[yY]$ ]]; then
  pushd "$TARGET_DIR" >/dev/null
  if command -v pythonw >/dev/null 2>&1; then
    (pythonw doccropper_tray.py --auto-start &)
  else
    (python3 doccropper_tray.py --auto-start &)
  fi
  popd >/dev/null
fi

