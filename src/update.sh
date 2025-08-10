#!/bin/bash

echo "--- Starting Project Update ---"

echo "--- Pulling latest changes from Git... ---"
update_output=$(git pull)
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Error: 'git pull' failed. Re-cloning repository..."
    cat > /tmp/lution_update_resolver.sh << 'EOL'
#!/bin/bash
cd /home/chip/Documents/gh/
rm -rf Lution
git clone https://github.com/Wookhq/Lution.git
echo "--- Lution has been updated. Please re-run the application. ---"
EOL
    chmod +x /tmp/lution_update_resolver.sh
    /tmp/lution_update_resolver.sh
    exit 1
fi

echo "$update_output"
echo "Git pull completed."

if echo "$update_output" | grep -q "update.sh"; then
    echo ""
    echo "--- Updater script has been updated. Re-running... ---"
    exec "$0" "$@"
fi

echo ""
echo "--- Ensuring Python venv exists... ---"
cd Lution || exit 1
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo ""
echo "--- Updating Python packages inside venv... ---"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Pip install failed inside venv."
    exit 1
fi

echo "Python packages updated successfully."
echo ""
echo "--- Project Update Finished ---"
