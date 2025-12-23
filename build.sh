#!/bin/bash
set -e

echo "Building LutionRT..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv sync
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Generate resources
echo "Generating resources..."
pyside6-rcc src/resources.qrc -o src/resources_rc.py

# Build with PyInstaller
echo "Building executable..."
pyinstaller src/main.py --name LutionRT --onefile --windowed --add-data "src/resources:resources"

echo "Build complete! Executable: $(pwd)/dist/LutionRT"
