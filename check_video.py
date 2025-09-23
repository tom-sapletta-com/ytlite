#!/usr/bin/env python3
"""
Check video generation with detailed error reporting
"""
import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_check")

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
    logger.info("Checking FFmpeg installation...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"FFmpeg found: {version_line}")
            return True
        else:
            logger.error(f"FFmpeg check failed: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.error("FFmpeg not found in PATH")
        return False

def create_test_video():
    """Create a test video using MoviePy."""
    try:
        import numpy as np
        from moviepy.editor import ImageClip
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "test_output.mp4"
        
        # Create a simple blue frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]  # Blue
        
        # Create a 2-second clip
        clip = ImageClip(frame).set_duration(2)
        
        # Write the video file
        logger.info(f"Creating test video: {output_file}")
        clip.write_videofile(
            str(output_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=True,
            logger=None,
            threads=1
        )
        
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Video created successfully: {output_file} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("❌ Video file was not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during video generation: {str(e)}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all checks."""
    print("\n=== Video Generation Test ===\n")
    
    # Check FFmpeg first
    if not check_ffmpeg():
        print("\n❌ FFmpeg is required but not found or not working.")
        print("Please install FFmpeg and ensure it's in your PATH.")
        print("On Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("On macOS: brew install ffmpeg")
        return 1
    
    # Test video generation
    print("\nTesting video generation...")
    if create_test_video():
        print("\n✅ Video generation test completed successfully!")
        return 0
    else:
        print("\n❌ Video generation test failed.")
        print("Check the logs above for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
