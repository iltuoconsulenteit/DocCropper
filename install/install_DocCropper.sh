#!/bin/bash
set -e

# We'll log installer actions once we know the target directory


# Require root on Linux so we can install to system paths
if [ "$EUID" -ne 0 ]; then
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
# configuration file handling
CONFIG_FILE="settings.json"
BACKUP_FILE="settings.local.json.bak"

DEFAULT_DIR="/opt/DocCropper"
read -r -p "Installation directory [$DEFAULT_DIR]: " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}
mkdir -p "$TARGET_DIR" 2>/dev/null || { echo "Cannot create $TARGET_DIR. Use a writable path or run with sudo." >&2; exit 1; }
if ! touch "$TARGET_DIR/.write_test" >/dev/null 2>&1; then
  echo "Cannot write to $TARGET_DIR. Choose another directory or adjust permissions." >&2
  exit 1
else
  rm -f "$TARGET_DIR/.write_test"
fi
echo "Installing to: $TARGET_DIR"

# Start logging once the installation directory is known
LOG_FILE="${DOCROPPER_LOG_FILE:-$TARGET_DIR/install.log}"
if ! touch "$LOG_FILE" >/dev/null 2>&1; then
  LOG_FILE="/tmp/DocCropper_install.log"
  echo "Cannot write log to $TARGET_DIR. Using $LOG_FILE"
fi
echo "Logging to $LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

DEFAULT_KEY=""
if [ -f "$TARGET_DIR/$CONFIG_FILE" ]; then
  DEFAULT_KEY=$(python3 - "$TARGET_DIR/$CONFIG_FILE" <<'PY'
import json,sys
try:
    with open(sys.argv[1]) as fh:
        print(json.load(fh).get('license_key',''))
except Exception:
    pass
PY
  )
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

if [ -d "$TARGET_DIR/.git" ]; then
  echo "📁 Repository già presente in $TARGET_DIR"
  read -r -p "🔄 Vuoi aggiornare il repository da GitHub? [s/N] " ans
  if [[ "$ans" =~ ^[sS]$ ]]; then
    if [ -f "$TARGET_DIR/$CONFIG_FILE" ]; then
      echo "🗄  Backup $CONFIG_FILE in $BACKUP_FILE"
      cp "$TARGET_DIR/$CONFIG_FILE" "$TARGET_DIR/$BACKUP_FILE"
      git -C "$TARGET_DIR" restore "$CONFIG_FILE" >/dev/null 2>&1 || true
    fi
    echo "📥 Aggiornamento repository..."
    git -C "$TARGET_DIR" merge --abort >/dev/null 2>&1 || true
    git -C "$TARGET_DIR" rebase --abort >/dev/null 2>&1 || true
    git -C "$TARGET_DIR" fetch origin "$BRANCH"
    git -C "$TARGET_DIR" reset --hard "origin/$BRANCH"
    git -C "$TARGET_DIR" clean -fd
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
fi

echo "📜 Ultimi 10 commit:" | tee -a "$LOG_FILE"
git -C "$TARGET_DIR" log -n 10 --pretty=format:"%h | %ad | %s" --date=short | tee -a "$LOG_FILE"
read -r -p "Vuoi ripristinare un commit specifico? (lascia vuoto per continuare): " COMMIT_HASH
if [ -n "$COMMIT_HASH" ]; then
  echo "🔄 Checkout del commit $COMMIT_HASH..." | tee -a "$LOG_FILE"
  git -C "$TARGET_DIR" checkout "$COMMIT_HASH" >>"$LOG_FILE" 2>&1
fi

printf '\xE2\x9C\x85 Operazione completata.\n'

# merge backed-up settings if present
if [ -f "$TARGET_DIR/$BACKUP_FILE" ]; then
  echo "🔀 Merging saved settings..."
  python3 <<'PY' "$TARGET_DIR/$CONFIG_FILE" "$TARGET_DIR/$BACKUP_FILE"
import json,sys
dst,bak = sys.argv[1:3]
with open(dst) as f:
    data = json.load(f)
try:
    with open(bak) as f:
        prev = json.load(f)
    data.update(prev)
except Exception:
    pass
with open(dst, 'w') as f:
    json.dump(data, f, indent=2)
PY
  rm -f "$TARGET_DIR/$BACKUP_FILE"
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

# Ask for license key and name
SETTINGS_FILE="$TARGET_DIR/$CONFIG_FILE"
if [ ! -f "$SETTINGS_FILE" ]; then
  if ! cat <<'EOF' | tee "$SETTINGS_FILE" >/dev/null
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
  then
    echo "Cannot create $SETTINGS_FILE. Check permissions." >&2
    exit 1
  fi
fi

if [ -n "$LIC_KEY" ]; then
  UPPER_KEY="$(echo "$LIC_KEY" | tr '[:lower:]' '[:upper:]')"
  DEV_KEY="${DOCROPPER_DEV_LICENSE:-}"
  DEV_KEY_UPPER="$(echo "$DEV_KEY" | tr '[:lower:]' '[:upper:]')"
  if [ "$UPPER_KEY" = "VALID" ] || [ "$UPPER_KEY" = "$DEV_KEY_UPPER" ]; then
    read -r -p "👤 Licensed to: " LIC_NAME
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

read -r -p "🚀 Launch DocCropper with tray icon now? [Y/n] " RUN_APP
if [[ ! "$RUN_APP" =~ ^[Nn]$ ]]; then
  pushd "$TARGET_DIR" >/dev/null
  if command -v pythonw >/dev/null 2>&1; then
    (pythonw doccropper_tray.py --auto-start &)
  else
    (python3 doccropper_tray.py --auto-start &)
  fi
  popd >/dev/null
fi

