#!/bin/bash

# Run RGS demonstration script
# This script runs the test scripts for the Resonance-Guided Search framework

# Set the current directory to the project root
cd "$(dirname "$0")"

# Create required directories
echo "Setting up directories..."
mkdir -p figures

# Run visualization tests
echo "Running adaptability landscape visualization tests..."
python tests/test_adaptability_landscape.py

# Run pathfinding tests
echo "Running pathfinding comparison tests..."
python tests/test_rgm_pathfinding.py

echo "All tests complete. Results are saved in the 'figures' directory."