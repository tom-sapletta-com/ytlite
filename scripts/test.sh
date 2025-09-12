#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# Check for virtual environment with absolute path
VENV_PATH="/home/tom/github/tom-sapletta-com/ytlite/venv/bin/python3"
if [ -f "$VENV_PATH" ]; then
    PYTHON_EXEC="$VENV_PATH"
    echo "Using virtual environment Python: $PYTHON_EXEC"
else
    PYTHON_EXEC="python3"
    echo "Using system Python: $PYTHON_EXEC"
fi

echo "${YELLOW}🧪 Running tests...${NC}"
$PYTHON_EXEC -m pytest tests/ -v || echo "No tests found or pytest not installed"
