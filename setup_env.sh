#!/usr/bin/env bash
# Create and activate a Python virtual environment for the project
set -e
if [ -d ".venv" ]; then
    echo ".venv already exists, skipping creation."
else
    python3 -m venv .venv
    echo "Virtual environment created at ./.venv"
fi

echo "To activate, run: source .venv/bin/activate"
echo "Ensure your system has Tk support installed (e.g. on Debian/Ubuntu: sudo apt-get install python3-tk)"

# Activate the venv and upgrade pip
source .venv/bin/activate
pip install --upgrade pip

echo "Setup complete. Your virtual environment is active."
echo "Install any further Python dependencies with: pip install <package>"
echo "To correct malformed date entries in the DB, run:"
echo "    python fix_dates.py"