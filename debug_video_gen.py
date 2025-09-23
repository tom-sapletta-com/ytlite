#!/usr/bin/env python3
"""
Comprehensive video generation test with detailed error handling
"""
import os
import sys
import logging
import traceback
import subprocess
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

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
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
    """Create a test video with detailed error handling."""
    try:
        logger.info("Starting video creation test...")
        
        # Import required modules with error handling
        try:
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            from moviepy.editor import ImageClip, concatenate_videoclips
            import imageio_ffmpeg
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            logger.info("Try installing requirements with: pip install numpy pillow moviepy imageio-ffmpeg")
            return False
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple frame with text
        def create_frame(text, size=(1280, 720), bg_color=(70, 70, 70), text_color=(255, 255, 255)):
            """Create a frame with text."""
            img = Image.new('RGB', size, color=bg_color)
            try:
                font = ImageFont.truetype("Arial", 60)
            except:
                font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(img)
            # Calculate text position (centered)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
            
            draw.text(position, text, font=font, fill=text_color)
            return np.array(img)
        
        # Create frames
        logger.info("Creating test frames...")
        frames = [
            create_frame("Test Frame 1", bg_color=(70, 70, 200)),
            create_frame("Test Frame 2", bg_color=(70, 200, 70)),
            create_frame("Test Frame 3", bg_color=(200, 70, 70))
        ]
        
        # Create clips from frames
        logger.info("Creating video clips...")
        clips = [ImageClip(frame).set_duration(2) for frame in frames]  # 2 seconds per frame
        
        # Concatenate clips
        logger.info("Concatenating clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Output file path
        output_file = output_dir / "test_output.mp4"
        
        # Write the video file
        logger.info(f"Writing video to: {output_file}")
        final_clip.write_videofile(
            str(output_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(output_dir / "temp-audio.m4a"),
            remove_temp=True,
            verbose=True,
            logger=None
        )
        
        # Verify the file was created
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Success! Video created: {output_file} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("❌ Error: Video file was not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during video generation: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function to run the test."""
    print("=" * 60)
    print("YTLite Video Generation Test")
    print("=" * 60)
    
    # Check FFmpeg first
    if not check_ffmpeg():
        print("\n❌ FFmpeg is required but not found or not working.")
        print("Please install FFmpeg and ensure it's in your PATH.")
        print("On Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("On macOS: brew install ffmpeg")
        return 1
    
    # Run the test
    print("\nStarting video generation test...")
    success = create_test_video()
    
    if success:
        print("\n✅ Video generation test completed successfully!")
        return 0
    else:
        print("\n❌ Video generation test failed.")
        print("Check the logs above for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
