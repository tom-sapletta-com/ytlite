#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🔍 Checking YTLite dependencies...${NC}"
cd "$(dirname "$0")/.."
python3 src/ytlite_main.py check
echo "${GREEN}✅ Dependency check complete${NC}"
