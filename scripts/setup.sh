#!/usr/bin/env bash

echo "SHELL SCRIPT INSTALL"
echo
echo "================="
echo "1) Update/Install Chroma"
echo "2) Uninstall Chroma"
echo "3) Exit"
echo "================="
echo "PLEASE PICK ONE"

read -r action
clear

case "$action" in
  1)
    echo "fetching installer script..."
    ./install.sh # pretent that this is a curl command and its will exc a script yay
    ;;
  2)
    echo "uninstalling chroma..."
    ;;
  3)
    echo "bye 👋"
    exit 0
    ;;
  *)
    echo "that ain't an option"
    ;;
esac
