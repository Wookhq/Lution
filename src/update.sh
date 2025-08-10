#!/bin/bash

# --- CONFIG ---
BRANCH_NAME="GTK-fr"  

echo "--- Starting Project Update ---"

# --- Step 1: Git Pull from branch ---
echo "--- Pulling latest changes from Git branch: $BRANCH_NAME ---"
git fetch origin "$BRANCH_NAME"
update_output=$(git checkout "$BRANCH_NAME" && git pull origin "$BRANCH_NAME")
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Error: Git pull failed for branch '$BRANCH_NAME'. Re-cloning repository..."
    cat > /tmp/lution_update_resolver.sh << EOL
#!/bin/bash
cd /home/chip/Documents/gh/
rm -rf Lution
git clone -b "$BRANCH_NAME" https://github.com/Wookhq/Lution.git
echo "--- Lution ($BRANCH_NAME) has been updated. Please re-run the application. ---"
EOL
    chmod +x /tmp/lution_update_resolver.sh
    /tmp/lution_update_resolver.sh
    exit 1
fi

echo "$update_output"
echo "Git pull from branch '$BRANCH_NAME' completed."

# --- Step 2: Handle Self-Update ---
if echo "$update_output" | grep -q "update.sh"; then
    echo ""
    echo "--- Updater script has been updated. Re-running... ---"
    exec "$0" "$@"
fi

echo ""
echo "--- Project Update Finished ---"
