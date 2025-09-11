#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🐳 Building base Docker image...${NC}"
if docker images | grep -q "ytlite:base"; then \
    echo "${YELLOW}Base image already exists. Skipping rebuild. Use 'docker rmi ytlite:base' to force rebuild.${NC}"; \
else \
    docker build -f Dockerfile.base -t ytlite:base .; \
fi
echo "${GREEN}✅ Base Docker image built (cached for future builds)${NC}"
