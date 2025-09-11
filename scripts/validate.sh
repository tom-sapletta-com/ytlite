#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "${YELLOW}🔍 Validating generated videos...${NC}"
python3 -c "
from src.validator import validate_all_videos
validate_all_videos()
"
echo "${GREEN}✅ Validation complete${NC}"
