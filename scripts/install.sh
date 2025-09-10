#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}📦 Installing dependencies...${NC}"
pip3 install -r requirements.txt
mkdir -p {content/episodes,output/{videos,shorts,thumbnails},credentials,config}
echo "${GREEN}✅ Dependencies installed${NC}"
