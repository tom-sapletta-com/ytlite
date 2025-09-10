#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}⚡ Fast Docker build (app only)...${NC}"
docker build -f Dockerfile.app -t ytlite:app .
echo "${GREEN}✅ Fast build complete${NC}"
