#!/usr/bin/env python3
"""
Simple test script to verify video generation with MoviePy
"""
import os
import sys
import logging
import subprocess
from pathlib import Path
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.config import get_setting

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_video_simple")

def check_ffmpeg():
    """Check if FFmpeg is available."""
    try:
        ffmpeg_binary = get_setting("FFMPEG_BINARY")
        if not ffmpeg_binary:
            logger.error("FFmpeg binary not found in MoviePy configuration")
            return False
        
        if isinstance(ffmpeg_binary, list):
            ffmpeg_path = ffmpeg_binary[0]
        else:
            ffmpeg_path = ffmpeg_binary
            
        if not os.path.exists(ffmpeg_path):
            logger.error(f"FFmpeg binary not found at: {ffmpeg_path}")
            return False
            
        logger.info(f"Using FFmpeg from: {ffmpeg_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking FFmpeg: {e}")
        return False

def create_test_video():
    """Create a simple test video with a colored frame and audio."""
    try:
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple colored frame
        from PIL import Image, ImageDraw
        img_path = output_dir / "test_frame.png"
        img = Image.new('RGB', (1280, 720), color=(70, 70, 70))
        d = ImageDraw.Draw(img)
        d.text((100, 300), "Test Video", fill=(255, 255, 255))
        img.save(img_path)
        logger.info(f"Created test frame at: {img_path}")
        
        # Create a simple audio clip (1 second of silence)
        import numpy as np
        from moviepy.audio.AudioClip import AudioArrayClip
        
        # 1 second of silence (44100 samples at 44100Hz)
        audio_array = np.zeros((44100, 2))  # Stereo silence
        audio_clip = AudioArrayClip(audio_array, fps=44100)
        audio_path = output_dir / "test_audio.wav"
        audio_clip.write_audiofile(str(audio_path), logger=None)
        logger.info(f"Created test audio at: {audio_path}")
        
        # Create a video clip from the image
        video_clip = ImageClip(str(img_path)).set_duration(5)  # 5 second clip
        
        # Set audio
        video_clip = video_clip.set_audio(AudioFileClip(str(audio_path)))
        
        # Write the video file
        output_path = output_dir / "test_output.mp4"
        video_clip.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            logger=None
        )
        
        if output_path.exists():
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Successfully created test video at: {output_path} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("Failed to create test video")
            return False
            
    except Exception as e:
        logger.error(f"Error in create_test_video: {e}", exc_info=True)
        return False

def main():
    # Check FFmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg check failed. Please install FFmpeg and ensure it's in your PATH.")
        print("\nTo install FFmpeg, try one of these commands:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return 1
    
    # Try to create a test video
    if create_test_video():
        logger.info("✅ Video generation test completed successfully!")
        return 0
    else:
        logger.error("❌ Video generation test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
