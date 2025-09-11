#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🧹 Cleaning...${NC}"
rm -rf output/videos/*.mp4 output/shorts/*.mp4 output/thumbnails/*.jpg
echo "${GREEN}✅ Cleaned${NC}"
