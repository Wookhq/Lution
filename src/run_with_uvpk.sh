#!/bin/bash
clear

banner() {
    local r1=0; local g1=170; local b1=255
    local r2=0; local g2=73;  local b2=230
    local lines_count=5
    local i=0

    while IFS= read -r line; do
        local r=$((r1 + (r2 - r1) * i / (lines_count - 1)))
        local g=$((g1 + (g2 - g1) * i / (lines_count - 1)))
        local b=$((b1 + (b2 - b1) * i / (lines_count - 1)))
        printf "\033[38;2;%s;%s;%sm%s\033[0m\n" "$r" "$g" "$b" "$line"
        ((i++))
    done <<'EOF'
 __         __  __     ______   __     ______     __   __
/\ \       /\ \/\ \   /\__  _\ /\ \   /\  __ \   /\ ".-. \
\ \ \____  \ \ \_\ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \
 \ \_____\  \ \_____\    \ \_\  \ \_\  \ \_____\  \ \_\"_\_\
  \/_____/   \/_____/     \/_/   \/_/   \/_____/   \/_/ \/_/
EOF
}

clear
echo "RUN LUTION"
banner

if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "uv already installed."
fi

cd .. || exit 1

export UV_VENV_CLEAR=1

uv venv
source .venv/bin/activate

cd "src/Lution" || exit 1
uv pip install -r requirements.txt

clear
banner

echo "It should open a window right now, if not click on the link"
echo "If you get an error or something like that, try pressing R to fix it"
echo "Also do you love my ASCII text? :3"

uv run python launch.py

echo "i got destroyed 😭"
