#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}🌐 Starting YTLite Web GUI at http://localhost:5000${NC}"

# Start the web GUI
cd "$(dirname "$0")/.." || exit 1
source venv/bin/activate || exit 1

# Use the new path to ytlite_web_gui.py
python src/ytlite_web_gui.py || {
    echo "Failed to start using source path, trying build path"
    python build/lib/src/ytlite_web_gui.py || {
        echo "Failed to start Web GUI. Check if the path is correct and dependencies are installed."
        # Try starting on a different port if 5000 is in use
        echo "Trying to start on port 5001..."
        FLASK_PORT=5001 python src/ytlite_web_gui.py || {
            echo "Failed to start on port 5001. Check if the port is in use."
            # Try starting on port 5002 if 5001 is in use
            echo "Trying to start on port 5002..."
            FLASK_PORT=5002 python src/ytlite_web_gui.py || {
                echo "Failed to start on port 5002. Check if the port is in use."
                # Try starting on port 5003 if 5002 is in use
                echo "Trying to start on port 5003..."
                FLASK_PORT=5003 python src/ytlite_web_gui.py || {
                    echo "Failed to start on port 5003. Check if the port is in use."
                    exit 1
                }
            }
        }
    }
}
