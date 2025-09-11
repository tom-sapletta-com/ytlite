#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🐳 Building app Docker image...${NC}"
if docker images | grep -q "ytlite:app"; then \
    echo "${YELLOW}App image already exists. Skipping rebuild. Use 'docker rmi ytlite:app' to force rebuild.${NC}"; \
else \
    docker build -f Dockerfile.app -t ytlite:app .; \
fi
echo "${GREEN}✅ App Docker image built${NC}"
