#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🎬 Generating videos...${NC}"

# First check dependencies
python3 src/dependencies.py

# Then batch process all markdown files
python3 src/ytlite_main.py batch content/episodes/

echo "${GREEN}✅ Videos generated${NC}"
