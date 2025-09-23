#!/usr/bin/env python3
"""
Comprehensive video generation test with detailed error handling and logging
"""
import os
import sys
import logging
import subprocess
import tempfile
import shutil
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

class VideoTest:
    def __init__(self):
        self.temp_dir = None
        self.output_dir = Path("test_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="ytlite_test_")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir:
            self.temp_dir.cleanup()
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed and working."""
        logger.info("Checking FFmpeg installation...")
        try:
            # Try to get FFmpeg version
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
    
    def create_test_video_ffmpeg(self):
        """Create a test video using FFmpeg directly."""
        output_file = self.output_dir / "ffmpeg_test.mp4"
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=2:size=640x480:rate=24",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_file)
        ]
        
        try:
            logger.info(f"Creating test video with FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"FFmpeg video created: {output_file} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("FFmpeg video file was not created")
                if result.stderr:
                    logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg command failed with code {e.returncode}")
            if e.stdout:
                logger.error(f"FFmpeg stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"FFmpeg stderr: {e.stderr}")
            return False
    
    def create_test_video_moviepy(self):
        """Create a test video using MoviePy."""
        try:
            import numpy as np
            from moviepy.editor import ImageClip
            
            output_file = self.output_dir / "moviepy_test.mp4"
            
            # Create a simple blue frame
            frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]
            
            # Create a 2-second clip
            clip = ImageClip(frame).set_duration(2)
            
            # Write the video file
            logger.info(f"Creating test video with MoviePy: {output_file}")
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
                logger.info(f"MoviePy video created: {output_file} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("MoviePy video file was not created")
                return False
                
        except Exception as e:
            logger.error(f"Error in MoviePy video creation: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

def main():
    """Run all video generation tests."""
    print("\n" + "="*60)
    print("YTLite Video Generation Test")
    print("="*60 + "\n")
    
    with VideoTest() as tester:
        # Test 1: Check FFmpeg
        print("\n[1/3] Testing FFmpeg installation...")
        ffmpeg_ok = tester.check_ffmpeg()
        
        # Test 2: Test FFmpeg directly
        print("\n[2/3] Testing FFmpeg video generation...")
        ffmpeg_video_ok = False
        if ffmpeg_ok:
            ffmpeg_video_ok = tester.create_test_video_ffmpeg()
        
        # Test 3: Test MoviePy
        print("\n[3/3] Testing MoviePy video generation...")
        moviepy_ok = False
        if ffmpeg_ok:  # Only try MoviePy if FFmpeg is working
            moviepy_ok = tester.create_test_video_moviepy()
        
        # Print summary
        print("\n" + "="*60)
        print("Test Results:")
        print("-"*60)
        print(f"FFmpeg installed: {'✓' if ffmpeg_ok else '✗'}")
        print(f"FFmpeg video generation: {'✓' if ffmpeg_video_ok else '✗'}")
        print(f"MoviePy video generation: {'✓' if moviepy_ok else '✗'}")
        print("="*60 + "\n")
        
        if ffmpeg_ok and ffmpeg_video_ok and moviepy_ok:
            print("✅ All tests passed! Video generation is working correctly.")
            return 0
        else:
            print("❌ Some tests failed. Check the logs above for details.")
            return 1

if __name__ == "__main__":
    sys.exit(main())
