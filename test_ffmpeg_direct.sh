#!/bin/bash
# Test FFmpeg video generation directly

echo "=== FFmpeg Video Generation Test ==="

# Create output directory
OUTPUT_DIR="test_output"
mkdir -p "$OUTPUT_DIR"

# Output file
OUTPUT_FILE="$OUTPUT_DIR/test_video.mp4"

# Clean up any existing file
rm -f "$OUTPUT_FILE"

# Run FFmpeg to create a simple test video
echo "Creating test video with FFmpeg..."
ffmpeg -y \
  -f lavfi \
  -i testsrc=duration=2:size=640x480:rate=24 \
  -c:v libx264 \
  -pix_fmt yuv420p \
  "$OUTPUT_FILE"

# Check if the video was created
if [ -f "$OUTPUT_FILE" ]; then
  SIZE_MB=$(du -m "$OUTPUT_FILE" | cut -f1)
  echo "✅ Video created successfully: $OUTPUT_FILE (${SIZE_MB}MB)"
  echo "You can play it with: xdg-open \"$OUTPUT_FILE\""
  exit 0
else
  echo "❌ Failed to create video"
  exit 1
fi
