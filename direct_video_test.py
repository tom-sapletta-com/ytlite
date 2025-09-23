#!/usr/bin/env python3
"""
Direct test of video generation functionality
"""
import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_test")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_video_generation():
    """Test video generation with direct MoviePy calls."""
    try:
        logger.info("Starting direct video generation test...")
        
        # Import required modules
        import numpy as np
        from moviepy.editor import ImageClip, concatenate_videoclips
        import tempfile
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            logger.info(f"Using temporary directory: {temp_dir}")
            
            # Create a simple red frame
            frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]  # Red frame
            
            # Create a clip
            clip = ImageClip(frame).set_duration(2)  # 2 seconds
            
            # Output file path
            output_file = temp_dir / "test_output.mp4"
            
            logger.info(f"Writing video to: {output_file}")
            
            # Write to file with various codecs
            clip.write_videofile(
                str(output_file),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(temp_dir / "temp-audio.m4a"),
                remove_temp=True,
                verbose=True,
                logger=None,
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart'
                ]
            )
            
            # Check if file was created
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"Successfully created test video: {output_file} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("Test video file was not created")
                return False
                
    except Exception as e:
        logger.error(f"Error in direct video generation test: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_video_generation()
    sys.exit(0 if success else 1)
