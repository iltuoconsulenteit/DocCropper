#!/bin/bash
# Download Material Dashboard Flask template
set -e
TMP=$(mktemp -d)
ZIP_URL="https://github.com/creativetimofficial/material-dashboard-flask/archive/refs/heads/main.zip"
DEST="templates/material-dashboard"
mkdir -p "$DEST"
echo "Downloading Material Dashboard Flask template..."
curl -L "$ZIP_URL" -o "$TMP/md.zip"
echo "Extracting..."
unzip -q "$TMP/md.zip" -d "$TMP"
cp -R "$TMP"/material-dashboard-flask-main/* "$DEST"/
echo "Material Dashboard template installed to $DEST"
