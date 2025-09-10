#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}📤 Starting upload service...${NC}"
docker-compose --profile upload up uploader -d
echo "${GREEN}✅ Upload service started${NC}"
