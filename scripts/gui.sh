#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}🌐 Starting YTLite Web GUI at http://localhost:5000${NC}"
python3 -u src/web_gui.py
