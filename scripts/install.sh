#!/usr/bin/env bash
set -e

echo "starting download..."

APP_NAME="chroma"
TMP_BIN="/tmp/TheChroma"
BIN_DEST="$HOME/.local/bin/$APP_NAME"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

curl -fL# https://github.com/Wookhq/Lution/releases/download/beta-v0.3.1/TheChroma -o "$TMP_BIN"

mkdir -p "$HOME/.local/bin"
chmod +x "$TMP_BIN"
mv "$TMP_BIN" "$BIN_DEST"

ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$ICON_DIR"
cp "$SCRIPT_DIR/logo.png" "$ICON_DIR/chroma.png"

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cp "$SCRIPT_DIR/chroma.desktop" "$DESKTOP_DIR/"
cp "$SCRIPT_DIR/chroma-quick-launch.desktop" "$DESKTOP_DIR/"

echo "installed $APP_NAME successfully"
