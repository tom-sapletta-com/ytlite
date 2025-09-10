#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🐳 Starting Docker services...${NC}"
docker-compose up --build -d
echo "${GREEN}✅ Docker services started${NC}"
