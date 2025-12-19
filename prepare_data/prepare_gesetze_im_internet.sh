#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

REPO_URL="https://github.com/bundestag/gesetze-tools"
DIR_NAME="gesetze-tools"

# Clone the repository
if [ -d "$DIR_NAME" ]; then
    echo "Directory '$DIR_NAME' already exists. Entering directory..."
else
    echo "Cloning repository from $REPO_URL..."
    git clone "$REPO_URL"
fi

cd "$DIR_NAME"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r ../requirements.txt
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Run the python commands
echo "Running lawde.py loadall..."
python lawde.py loadall

echo "Running lawdown.py convert laws laws_md..."
python lawdown.py convert laws laws_md

echo "Script execution completed successfully."
