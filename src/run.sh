#!/bin/bash
./update.sh
clear

banner() {
    local r1=0
    local g1=170
    local b1=255
    local r2=0
    local g2=73
    local b2=230

    # banner text
    local banner_text=' __         __  __     ______   __     ______     __   __
/\ \       /\ \/\ \   /\__  _\ /\ \   /\  __ \   /\ ".-. \
\ \ \____  \ \ \_\ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \
 \ \_____\  \ \_____\    \ \_\  \ \_\  \ \_____\  \ \_\"_\_\
  \/_____/   \/_____/     \/_/   \/_/   \/_____/   \/_/ \/_/'

    local lines_count=$(echo "$banner_text" | wc -l)
    local i=0

    echo "$banner_text" | while IFS= read -r line; do
        local r=$(( r1 + (r2 - r1) * i / (lines_count - 1) ))
        local g=$(( g1 + (g2 - g1) * i / (lines_count - 1) ))
        local b=$(( b1 + (b2 - b1) * i / (lines_count - 1) ))
        printf "\033[38;2;%s;%s;%sm%s\033[0m\n" "$r" "$g" "$b" "$line"
        ((i++))
    done
}

clear
echo "RUN LUTION"
banner

if grep -qi 'ubuntu\|debian' /etc/os-release; then
    if ! dpkg -s python3-venv >/dev/null 2>&1; then
        echo "Installing python3-venv..."
        sudo apt update && sudo apt install -y python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-dev libcairo2-dev libgirepository1.0-dev
        sudo apt update
    fi
elif grep -qi 'arch\|manjaro' /etc/os-release; then
    if ! pacman -Qi python-virtualenv >/dev/null 2>&1; then
        echo "Installing python-virtualenv..."
        sudo pacman -Sy --noconfirm python-virtualenv python-gobject gtk3
    fi
elif grep -qi 'fedora' /etc/os-release; then
    if ! rpm -q python3-virtualenv >/dev/null 2>&1; then
        echo "Installing python3-virtualenv..."
        sudo dnf install -y python3-virtualenv python3-gobject gtk3
    fi
else
    exit 1
fi

cd ..


python3 -m venv ".venv"
source .venv/bin/activate

cd "src/Lution" || exit 1
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pygobject

clear
banner
echo "GTK IS HERE YAYYY! 🎉"
echo "Took a while, but now lution is a GTK app! 🐧"
echo "Also do you love my ASCII text? :3"

python3 gurt.py
echo "i got destroyed 😭"
