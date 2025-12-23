#!/usr/bin/env python3
"""Build script for LutionRT - generates resources and builds with PyInstaller"""

import subprocess
import sys
import os


def main():
    print("Generating resources_rc.py...")
    try:
        subprocess.run(
            ["pyside6-rcc", "src/resources.qrc", "-o", "src/resources_rc.py"],
            check=True,
            cwd=".",
        )
        print("✓ Resources generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate resources: {e}")
        return 1
    except FileNotFoundError:
        print("✗ pyside6-rcc not found. Make sure you're in the virtual environment.")
        return 1

    print("Building with PyInstaller...")
    try:
        subprocess.run(
            [
                "pyinstaller",
                "src/main.py",
                "--name",
                "LutionRT",
                "--onefile",
                "--windowed",
                "--add-data",
                "src/resources:resources",
            ],
            check=True,
            cwd=".",
        )
        print("✓ Build completed successfully!")
        print(f"Executable located at: {os.path.abspath('dist/LutionRT')}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
