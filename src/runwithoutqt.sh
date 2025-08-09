#!/bin/bash
./update.sh
clear
echo "RUN LUTION"


banner() {
    # start color: 0,170,255  (#00AAFF)
    local r1=0
    local g1=170
    local b1=255

    # end color: 0,73,230  (#0049E6)
    local r2=0
    local g2=73
    local b2=230

    # total steps = number of lines in banner
    local lines_count=5
    local i=0

    while IFS= read -r line; do
        # interpolate colors
        local r=$(( r1 + (r2 - r1) * i / (lines_count - 1) ))
        local g=$(( g1 + (g2 - g1) * i / (lines_count - 1) ))
        local b=$(( b1 + (b2 - b1) * i / (lines_count - 1) ))

        printf "\033[38;2;%s;%s;%sm%s\033[0m\n" "$r" "$g" "$b" "$line"
        ((i++))
    done << 'EOF'
 __         __  __     ______   __     ______     __   __
/\ \       /\ \/\ \   /\__  _\ /\ \   /\  __ \   /\ ".-. \
\ \ \____  \ \ \_\ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \
 \ \_____\  \ \_____\    \ \_\  \ \_\  \ \_____\  \ \_\"_\_\
  \/_____/   \/_____/     \/_/   \/_/   \/_____/   \/_/ \/_/
EOF
}

banner

if grep -qi 'ubuntu\|debian' /etc/os-release; then
    if ! dpkg -s python3-venv >/dev/null 2>&1; then
        echo "Installing python3-venv..."
        sudo apt update && sudo apt install -y python3-venv
    else
        echo "python3-venv is already installed."
    fi

elif grep -qi 'arch\|manjaro' /etc/os-release; then
    if ! pacman -Qi python-virtualenv >/dev/null 2>&1; then
        echo "Installing python-virtualenv..."
        sudo pacman -Sy --noconfirm python-virtualenv
    else
        echo "python-virtualenv is already installed."
    fi

elif grep -qi 'fedora' /etc/os-release; then
    if ! rpm -q python3-virtualenv >/dev/null 2>&1; then
        echo "Installing python3-virtualenv..."
        sudo dnf install -y python3-virtualenv
    else
        echo "python3-virtualenv is already installed."
    fi

else
    exit 1
fi

cd ..
python3 -m venv ".venv"
source .venv/bin/activate

cd "src/Lution" || exit 1
pip install -r requirements.txt

clear
banner

echo "It should open a window right now, if not click on the link"
echo "If you get a error or something like that, try pressing R to fix it"
echo "Also do you love my ASCII text? :3"

streamlit run main.py || python3 -m streamlit run main.py

echo "i got destroyed 😭"
