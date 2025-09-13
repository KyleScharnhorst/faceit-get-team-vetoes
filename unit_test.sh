#!/bin/bash

# Load environment variables for testing
source ./helper_scripts/set_test_env_vars.sh

# Ensure coverage.py is installed
if ! command -v coverage &> /dev/null
then
    echo "coverage.py is not installed. Installing it now..."
    pip install coverage
fi

# Run tests with coverage
echo "Running tests and measuring code coverage..."
coverage run --source=get_vetoes -m unittest discover -s . -p "test_get_vetoes.py"

# Generate coverage report
echo "Generating coverage report..."
coverage report -m

# Optional: Generate an HTML report
echo "Generating HTML coverage report..."
coverage html
echo "HTML report generated in the 'htmlcov' directory. Open 'htmlcov/index.html' in your browser to view it."