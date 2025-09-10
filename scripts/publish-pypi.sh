#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo "${YELLOW}📦 Publishing to PyPI...${NC}"

# Ensure dependencies are installed
if ! command -v twine &> /dev/null; then
    echo "${YELLOW}Installing twine...${NC}"
    pip3 install twine
fi

# Build the package
echo "${YELLOW}Building package...${NC}"
python3 setup.py sdist bdist_wheel

# Upload to PyPI
echo "${YELLOW}Uploading to PyPI...${NC}"
twine upload dist/*

echo "${GREEN}✅ Published to PyPI${NC}"
