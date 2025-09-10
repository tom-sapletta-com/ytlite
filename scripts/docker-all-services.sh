#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🌐 Starting all specialized services...${NC}"
docker-compose --profile tts --profile video --profile upload up tts-service video-generator uploader -d
echo "${GREEN}✅ All specialized services started${NC}"
