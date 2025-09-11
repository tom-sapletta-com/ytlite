#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}⚡ Quick content creation...${NC}"
timestamp=$(date +%Y%m%d_%H%M%S)
echo "---" > content/episodes/quick_$timestamp.md
echo "title: 'Quick thought $timestamp'" >> content/episodes/quick_$timestamp.md
echo "date: $(date +%Y-%m-%d)" >> content/episodes/quick_$timestamp.md
echo "theme: philosophy" >> content/episodes/quick_$timestamp.md
echo "---" >> content/episodes/quick_$timestamp.md
echo "" >> content/episodes/quick_$timestamp.md
cat >> content/episodes/quick_$timestamp.md
make generate
echo "${GREEN}✅ Quick content generated${NC}"
