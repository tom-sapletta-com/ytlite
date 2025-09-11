#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}⏰ Starting automation...${NC}"
docker-compose --profile automation up scheduler
