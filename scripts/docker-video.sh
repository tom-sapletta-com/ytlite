#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🎬 Starting video generation service...${NC}"
docker-compose --profile video up video-generator -d
echo "${GREEN}✅ Video generation service started${NC}"
