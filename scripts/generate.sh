#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🎬 Generating videos...${NC}"
for file in content/episodes/*.md; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        python3 src/ytlite.py generate "$file"
    fi
done
echo "${GREEN}✅ Videos generated${NC}"
