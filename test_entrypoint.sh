#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Backend Tests ---
echo "--- Running Backend Tests ---"
# It's good practice to ensure all dependencies are installed.
# This command assumes requirements.txt includes test dependencies like pytest.
pip install -r requirements.txt

# Run backend tests using pytest
pytest tests/

# --- Frontend Tests ---
# The frontend tests are in a separate project, so we navigate there
if [ -d "tauri-youtube-oauth" ]; then
  echo "--- Running Frontend Tests ---"
  cd tauri-youtube-oauth
  
  # Install frontend dependencies
  # Using npm ci is recommended for CI environments as it's faster and more reliable
  npm ci
  
  # Run frontend unit tests
  # The 'test:unit' script from package.json is used here
  npm run test:unit
  
  # Go back to the root directory
  cd ..
else
  echo "Frontend test directory 'tauri-youtube-oauth' not found, skipping frontend tests."
fi

# If all tests pass, execute the main command passed to this script
exec "$@"
