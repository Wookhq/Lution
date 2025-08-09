#!/bin/bash
./update.sh
clear

banner() {
cat << "EOF"
 __         __  __     ______   __     ______     __   __
/\ \       /\ \/\ \   /\__  _\ /\ \   /\  __ \   /\ ".-. \
\ \ \____  \ \ \_\ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \
 \ \_____\  \ \_____\    \ \_\  \ \_\  \ \_____\  \ \_\\"_\/
  \/_____/   \/_____/     \/_/   \/_/   \/_____/   \/_/ \/_/
EOF
}

clear
echo "RUN LUTION"
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

python3 launch.py

echo "i got destroyed 😭"
