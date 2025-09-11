#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}📤 Uploading to YouTube...${NC}"
python3 src/youtube_uploader.py --batch output/
echo "${GREEN}✅ Upload complete${NC}"
