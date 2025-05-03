#!/bin/bash

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate your virtual environment first"
    exit 1
fi

# Install dev dependencies if not already installed
echo "Installing development dependencies..."
uv pip install -e ".[dev]"

# Create the binary
echo "Building binary..."
pyinstaller --name apnea-trainer \
            --onefile \
            --windowed \
            --add-data "src/apnea_trainer/templates:apnea_trainer/templates" \
            --hidden-import apnea_trainer.timer \
            --hidden-import apnea_trainer.gui \
            src/apnea_trainer/gui.py

echo "Binary created in dist/apnea-trainer" 