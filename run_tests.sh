#!/bin/bash

# Test runner script for Timestamp Adjuster
# Activates virtual environment and runs all unit tests

echo "🧪 Running Timestamp Adjuster Unit Tests..."
echo "============================================"

# Activate virtual environment
source venv/bin/activate

# Run tests with unittest discovery from tests directory
python -m unittest discover -s tests -p "test_*.py" -v

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi
