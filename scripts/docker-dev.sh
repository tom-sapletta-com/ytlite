#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🔧 Starting development environment...${NC}"
docker-compose up ytlite-dev nginx -d
echo "${GREEN}✅ Development environment started${NC}"
