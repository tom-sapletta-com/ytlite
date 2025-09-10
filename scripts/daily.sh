#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🤖 Generating daily content...${NC}"
python3 src/ytlite.py daily
echo "${GREEN}✅ Daily content ready${NC}"
