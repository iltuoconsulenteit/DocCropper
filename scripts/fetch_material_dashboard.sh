#!/bin/bash
# Download Material Dashboard Flask template into templates directory
set -euo pipefail

command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v unzip >/dev/null || { echo "unzip is required" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"
ZIP_URL="https://github.com/creativetimofficial/material-dashboard-flask/archive/refs/heads/main.zip"
DEST="$REPO_ROOT/templates/material-dashboard"

trap 'rm -rf "$TMP"' EXIT

echo "Fetching Material Dashboard Flask template..."
if ! curl -fL "$ZIP_URL" -o "$TMP/md.zip"; then
  echo "Download failed" >&2
  exit 1
fi

echo "Extracting..."
unzip -q "$TMP/md.zip" -d "$TMP"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$TMP/material-dashboard-flask-main"/* "$DEST"/

echo "Material Dashboard template installed to $DEST"
