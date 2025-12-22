#!/bin/bash

# --- Lution Updater ---
# This script updates the project from Git and handles self-updates gracefully.

echo "--- Starting Project Update ---"

# --- Step 1: Git Pull ---
echo "--- Pulling latest changes from Git... ---"

# We store the output of git pull to check if this script was updated.
update_output=$(git pull)
exit_code=$?

# Check if git pull was successful
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Error: 'git pull' failed. This could be due to local changes or merge conflicts."
    echo "Attempting to resolve by re-cloning the repository."

    # Create a temporary script to delete and re-clone
    cat > /tmp/lution_update_resolver.sh << 'EOL'
#!/bin/bash
echo "--- Force-updating Lution ---"
# Go to the parent directory
cd /home/chip/Documents/gh/
# Remove the old directory
echo "Removing old Lution directory..."
rm -rf Lution
# Clone the repository again
echo "Cloning fresh copy of Lution..."
git clone https://github.com/Wookhq/Lution.git
echo "--- Lution has been updated. Please re-run the application. ---"
EOL

    # Make the temporary script executable
    chmod +x /tmp/lution_update_resolver.sh

    # Execute the temporary script and exit
    echo "Running update resolver script..."
    /tmp/lution_update_resolver.sh
    exit 1
fi

echo "$update_output"
echo "Git pull completed."

# --- Step 2: Handle Self-Update ---
# Check if this script's filename is in the git pull output.
if echo "$update_output" | grep -q "update.sh"; then
    echo ""
    echo "--- Updater script has been updated. Re-running the new version... ---"
    # Execute the new version of the script and exit the current one.
    # "$0" is the path to the current script. "$@" passes along any arguments.
    exec "$0" "$@"
fi

# --- Step 3: Install/Update Python Dependencies ---
echo ""
echo "--- Updating Python packages... ---"
pip install -r Lution/requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Pip install failed. Please check the requirements.txt file and your Python environment."
    exit 1
fi

echo "Python packages updated successfully."
echo ""
echo "--- Project Update Finished ---"