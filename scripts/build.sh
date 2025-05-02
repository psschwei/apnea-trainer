#!/bin/bash

# Generate requirements.txt
echo "Generating requirements.txt from pyproject.toml..."
uv pip compile pyproject.toml -o requirements.txt

echo "Building Docker image..."
docker build -t apnea-trainer .

echo "Done! requirements.txt has been generated and Docker image has been built." 