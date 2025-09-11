#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🎬 Generating videos...${NC}"

python3 -u src/ytlite_main.py batch content/episodes/

echo "${GREEN}✅ Videos generated${NC}"
