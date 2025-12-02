#!/bin/bash

# Exit on error
set -e

# Start the server in the background
echo "Starting server..."
npm run server &
SERVER_PID=$!

# Give the server time to start
sleep 5

# Install Python dependencies if needed
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest requests
fi

# Run the tests
echo "Running tests..."
python -m pytest task_tests.py -v

# Capture the test exit code
TEST_EXIT_CODE=$?

# Stop the server
echo "Stopping server..."
kill $SERVER_PID

# Exit with the test exit code
exit $TEST_EXIT_CODE
