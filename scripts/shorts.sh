#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}📱 Creating Shorts...${NC}"
python3 src/ytlite.py shorts output/videos/*.mp4
echo "${GREEN}✅ Shorts created${NC}"
