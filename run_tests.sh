#!/bin/bash

# Test runner script for Timestamp Adjuster
# Activates virtual environment and runs all unit tests

echo "🧪 Running Timestamp Adjuster Unit Tests..."
echo "============================================"

# Function to clean up test-generated files
cleanup_test_files() {
    echo "🧹 Cleaning up test-generated files..."
    
    # Remove any temporary files from outputs directory (but keep .gitkeep and non-temp files)
    find outputs/ -name "tmp*" -type f -delete 2>/dev/null || true
    
    # Remove any files with patterns indicating they were test-generated
    find outputs/ -name "*_plus*s.txt" -mmin -10 -type f -delete 2>/dev/null || true
    find outputs/ -name "*_minus*s.txt" -mmin -10 -type f -delete 2>/dev/null || true
}

# Clean up any leftover files from previous test runs
cleanup_test_files

# Activate virtual environment
source venv/bin/activate

# Run tests with unittest discovery from tests directory
python -m unittest discover -s tests -p "test_*.py" -v

# Store test exit code
test_exit_code=$?

# Clean up any files generated during tests
cleanup_test_files

# Check exit code
if [ $test_exit_code -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi
