#!/bin/bash
# setup_ytlite.sh - Automate YTLite video generation setup and testing

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 YTLite Video Generation Setup${NC}"
echo "===================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install packages
install_packages() {
    echo -e "${YELLOW}Installing required system packages...${NC}"
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg python3-pip python3-venv
    elif command_exists yum; then
        sudo yum install -y ffmpeg python3-pip
    elif command_exists brew; then
        brew install ffmpeg python
    else
        echo -e "${RED}⚠️  Could not detect package manager. Please install FFmpeg manually.${NC}"
        exit 1
    fi
}

# Function to setup Python environment
setup_python_env() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install moviepy imageio-ffmpeg numpy Pillow
}

# Function to run video generation test
run_test() {
    echo -e "${YELLOW}Running video generation test...${NC}"
    TEST_SCRIPT="test_video_gen.py"
    
    cat > "$TEST_SCRIPT" << 'EOL'
from moviepy.editor import ImageClip
import numpy as np
import os

# Create output directory
os.makedirs("test_output", exist_ok=True)

try:
    # Create a simple red frame with text
    frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]  # Red frame
    
    # Add text
    from PIL import Image, ImageDraw, ImageFont
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("Arial", 40)
    except:
        font = ImageFont.load_default()
    
    text = "YTLite Test Video"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((640 - text_width) // 2, (480 - text_height) // 2)
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    # Create and save video
    clip = ImageClip(np.array(img)).set_duration(3)  # 3 second clip
    output_file = "test_output/test_output.mp4"
    clip.write_videofile(
        output_file,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )
    
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"\n✅ ${GREEN}Success! Test video created: {output_file} ({file_size:.2f} MB)${NC}")
        print(f"   You can play it with: xdg-open {output_file}")
    else:
        print(f"\n❌ ${RED}Error: Test video was not created${NC}")
        
except Exception as e:
    print(f"\n❌ ${RED}Error during video generation: {str(e)}${NC}")
    raise
EOL

    python3 "$TEST_SCRIPT"
    rm -f "$TEST_SCRIPT"
}

# Main execution
main() {
    # Check if running as root
    if [ "$(id -u)" -eq 0 ]; then
        echo -e "${RED}Error: Do not run this script as root.${NC}"
        exit 1
    fi

    # Check for required commands
    for cmd in python3 pip3; do
        if ! command_exists "$cmd"; then
            echo -e "${RED}Error: $cmd is not installed.${NC}"
            install_packages
            break
        fi
    done

    # Check FFmpeg
    if ! command_exists ffmpeg; then
        echo -e "${YELLOW}FFmpeg not found. Installing...${NC}"
        install_packages
    fi

    # Setup Python environment
    if [ ! -d "venv" ]; then
        setup_python_env
    else
        source venv/bin/activate
    fi

    # Run test
    run_test

    echo -e "\n${GREEN}✅ Setup and test completed successfully!${NC}"
    echo -e "To activate this environment in the future, run: source venv/bin/activate"
}

main "$@"
