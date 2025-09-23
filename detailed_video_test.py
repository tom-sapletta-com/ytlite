#!/usr/bin/env python3
"""
Detailed test of video generation with explicit error handling and logging
"""
import sys
import os
import logging
import subprocess
import numpy as np
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_test")

def check_ffmpeg():
    """Check if FFmpeg is available."""
    try:
        logger.info("Checking FFmpeg installation...")
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
    """Create a simple test video."""
    try:
        logger.info("Starting video creation test...")
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple red frame
        logger.info("Creating test frame...")
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]  # Red frame
        
        # Import MoviePy
        try:
            logger.info("Importing MoviePy...")
            from moviepy.editor import ImageClip
            logger.info("Successfully imported MoviePy")
        except ImportError as e:
            logger.error(f"Failed to import MoviePy: {e}")
            return False
            
        # Create a 2-second clip
        logger.info("Creating video clip...")
        clip = ImageClip(frame).set_duration(2)
        
        # Write to file
        output_file = output_dir / "simple_test.mp4"
        logger.info(f"Writing video to: {output_file}")
        
        try:
            clip.write_videofile(
                str(output_file),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(output_dir / "temp_audio.m4a"),
                remove_temp=True,
                verbose=True,
                logger=logger
            )
            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Video created successfully: {output_file} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("✗ Video file was not created")
                return False
                
        except Exception as e:
            logger.error(f"Error writing video file: {e}", exc_info=True)
            return False
            
    except Exception as e:
        logger.error(f"Error in create_test_video: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("=== Starting Video Generation Test ===")
    
    # Check FFmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg is required but not found. Please install FFmpeg and try again.")
        sys.exit(1)
    
    # Run the test
    success = create_test_video()
    
    if success:
        logger.info("=== Video Generation Test PASSED ===")
        sys.exit(0)
    else:
        logger.error("=== Video Generation Test FAILED ===")
        sys.exit(1)
