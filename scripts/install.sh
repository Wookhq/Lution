#!/usr/bin/env bash
set -e

echo "starting download..."

TMP_BIN="/tmp/TheChroma"
APP_NAME="Chroma"
BIN_DEST="$HOME/.local/bin/$APP_NAME"

curl -fL# https://github.com/Wookhq/Lution/releases/download/beta-v0.3.1/TheChroma -o "$TMP_BIN"

mkdir -p "$HOME/.local/bin"
chmod +x "$TMP_BIN"
mv "$TMP_BIN" "$BIN_DEST"

echo "installed $APP_NAME to ~/.local/bin"
echo "make sure ~/.local/bin is in your PATH"
