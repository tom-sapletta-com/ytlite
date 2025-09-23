#!/usr/bin/env python3
"""
Simple script to test FFmpeg installation and basic video generation
"""
import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
    try:
        # Check if ffmpeg command is available
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ FFmpeg is installed:")
            print(result.stdout.split('\n')[0])
            return True
        else:
            print("❌ FFmpeg command failed:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed or not in PATH")
        return False

def test_video_generation():
    """Test basic video generation with FFmpeg."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "test_video.mp4"
    
    # Create a simple video with FFmpeg
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "testsrc=duration=5:size=640x480:rate=30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_file)
    ]
    
    print(f"\nGenerating test video at: {output_file}")
    print("Running command:", " ".join(cmd))
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Video generated successfully!")
            print(f"Output file size: {output_file.stat().st_size / 1024:.2f} KB")
            return True
        else:
            print("❌ Video generation failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FFmpeg Installation Test")
    print("=" * 50)
    
    if not check_ffmpeg():
        print("\nPlease install FFmpeg first:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)
    
    print("\nTesting video generation...")
    if test_video_generation():
        print("\n✅ FFmpeg is working correctly!")
    else:
        print("\n❌ FFmpeg test failed. Please check the error messages above.")
        sys.exit(1)
