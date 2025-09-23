#!/bin/bash
# Simple FFmpeg test script

echo "Testing FFmpeg installation..."

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed"
    exit 1
fi

# Get FFmpeg version
echo -n "FFmpeg version: "
ffmpeg -version | head -n 1

# Create a test directory
TEST_DIR="ffmpeg_test"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR" || exit 1

# Create a simple video with FFmpeg
echo -e "\nGenerating test video..."
ffmpeg -f lavfi -i testsrc=duration=2:size=640x480:rate=30 -c:v libx264 -pix_fmt yuv420p test_video.mp4 -y 2>&1

# Check if video was created
if [ -f "test_video.mp4" ]; then
    echo -e "\n✅ Test video created successfully!"
    echo "File size: $(du -h test_video.mp4 | cut -f1)"
    echo "You can play the video with: mpv $(pwd)/test_video.mp4"
    exit 0
else
    echo -e "\n❌ Failed to create test video"
    exit 1
fi
