#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🔊 Starting TTS service...${NC}"
docker-compose --profile tts up tts-service -d
echo "${GREEN}✅ TTS service started${NC}"
