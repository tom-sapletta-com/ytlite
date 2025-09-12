#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}🌐 Starting YTLite Web GUI at http://localhost:5000${NC}"

# Start the web GUI
cd "$(dirname "$0")/.." || exit 1
source venv/bin/activate || exit 1

# Use the correct path to web_gui.py
python build/lib/src/web_gui.py || {
    echo "Failed to start using build path, trying source path"
    python src/web_gui.py || {
        echo "Failed to start Web GUI. Check if the path is correct and dependencies are installed."
        exit 1
    }
}
