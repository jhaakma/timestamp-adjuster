#!/bin/bash

# Start script for Timestamp Adjuster
# This script activates the virtual environment and runs the main application

echo "Starting Timestamp Adjuster..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Running application..."
python main.py

echo "Application finished."
