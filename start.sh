#!/bin/bash

# Timestamp Adjuster Start Script
# Activates the virtual environment and runs the application

# Change to the script's directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Run the application in interactive mode
echo "🚀 Starting Timestamp Adjuster..."
echo ""
python main.py "$@"
