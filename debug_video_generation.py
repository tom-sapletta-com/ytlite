#!/usr/bin/env python3
"""
Debug script for video generation issues
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_debug")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_ffmpeg():
    """Check if FFmpeg is available and working."""
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        logger.info(f"FFmpeg path: {ffmpeg_path}")
        
        # Check FFmpeg version
        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("FFmpeg version check successful")
                logger.debug(f"FFmpeg output: {result.stdout.strip().split('\n')[0]}")
                return True
            else:
                logger.error(f"FFmpeg version check failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error running FFmpeg: {e}")
            return False
    except ImportError:
        logger.error("imageio-ffmpeg not installed")
        return False

def test_moviepy():
    """Test MoviePy video generation."""
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips
        import numpy as np
        
        # Create a test output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple red frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]  # Red frame
        
        # Create a clip
        clip = ImageClip(frame).set_duration(2)  # 2 seconds
        
        # Write to file
        output_file = output_dir / "test_output.mp4"
        clip.write_videofile(
            str(output_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(output_dir / "temp-audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Successfully created test video: {output_file} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("Test video file was not created")
            return False
            
    except Exception as e:
        logger.error(f"Error in MoviePy test: {e}", exc_info=True)
        return False

def main():
    """Run all tests."""
    logger.info("Starting video generation debug...")
    
    # Check FFmpeg
    logger.info("=== Checking FFmpeg ===")
    ffmpeg_ok = check_ffmpeg()
    
    # Test MoviePy
    logger.info("\n=== Testing MoviePy ===")
    moviepy_ok = test_moviepy()
    
    # Print summary
    logger.info("\n=== Summary ===")
    logger.info(f"FFmpeg: {'OK' if ffmpeg_ok else 'FAILED'}")
    logger.info(f"MoviePy: {'OK' if moviepy_ok else 'FAILED'}")
    
    if ffmpeg_ok and moviepy_ok:
        logger.info("\nBasic video generation components appear to be working.")
        logger.info("The issue might be in the YTLite code or environment.")
    else:
        logger.error("\nThere are issues with the video generation setup.")
        if not ffmpeg_ok:
            logger.error("- FFmpeg is not properly installed or configured.")
        if not moviepy_ok:
            logger.error("- MoviePy encountered an error during video generation.")
    
    return 0 if (ffmpeg_ok and moviepy_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
