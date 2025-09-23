#!/usr/bin/env python3
"""
Test video generation using only Python's built-in libraries
"""
import os
import sys
import base64
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is available."""
    try:
        result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def create_test_video():
    """Create a test video using pure Python and FFmpeg."""
    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a simple video using FFmpeg's test pattern
    output_file = output_dir / "test_video.mp4"
    
    # Try different FFmpeg commands to see what works
    commands = [
        ["ffmpeg", "-version"],
        ["which", "ffmpeg"],
        ["ls", "-la", "/usr/bin/ffmpeg"],
        ["ls", "-la", "/usr/local/bin/ffmpeg"],
        ["find", "/", "-name", "ffmpeg", "-type", "f", "-executable", "2>/dev/null"],
    ]
    
    print("\n=== System Information ===")
    print(f"Python: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"FFmpeg available: {check_ffmpeg()}")
    
    print("\n=== Testing FFmpeg Commands ===")
    for cmd in commands:
        try:
            print(f"\nRunning: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n=== Test Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(create_test_video())
