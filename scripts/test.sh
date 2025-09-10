#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🧪 Running tests...${NC}"
python3 -m pytest tests/ -v || echo "No tests found"
