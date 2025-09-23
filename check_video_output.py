#!/usr/bin/env python3
"""
Check video generation with detailed error reporting and output redirection
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging to both file and console
log_file = Path("video_test.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_test")

def run_command(cmd, cwd=None):
    """Run a command and return the output and error."""
    logger.info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        logger.debug(f"Command output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with code {e.returncode}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        raise

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
    logger.info("Checking FFmpeg installation...")
    try:
        result = run_command(["ffmpeg", "-version"])
        version_line = result.stdout.split('\n')[0]
        logger.info(f"FFmpeg found: {version_line}")
        return True
    except Exception as e:
        logger.error("FFmpeg check failed")
        return False

def create_test_video():
    """Create a test video using FFmpeg directly."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "direct_ffmpeg_test.mp4"
    
    # Clean up any existing file
    if output_file.exists():
        output_file.unlink()
    
    # Create a test video using FFmpeg's test pattern
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-f", "lavfi",
        "-i", "testsrc=duration=2:size=640x480:rate=24",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_file)
    ]
    
    try:
        run_command(cmd)
        
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Video created successfully: {output_file} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("❌ Video file was not created")
            return False
    except Exception as e:
        logger.error(f"❌ Error creating video: {e}")
        return False

def main():
    """Run all checks."""
    logger.info("=== Starting Video Generation Test ===")
    
    # Check FFmpeg first
    if not check_ffmpeg():
        logger.error("❌ FFmpeg is required but not found or not working.")
        logger.error("Please install FFmpeg and ensure it's in your PATH.")
        logger.error("On Ubuntu/Debian: sudo apt-get install ffmpeg")
        logger.error("On macOS: brew install ffmpeg")
        return 1
    
    # Test video generation
    logger.info("\nTesting video generation with FFmpeg...")
    if create_test_video():
        logger.info("✅ Video generation test completed successfully!")
        return 0
    else:
        logger.error("❌ Video generation test failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
