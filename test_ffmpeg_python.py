#!/usr/bin/env python3
"""
Test FFmpeg functionality through Python
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

def main():
    print("FFmpeg Python Test")
    print("=================")
    
    # Check if FFmpeg is available
    try:
        result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ FFmpeg not found in PATH")
            return 1
            
        ffmpeg_path = result.stdout.strip()
        print(f"✅ Found FFmpeg at: {ffmpeg_path}")
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_video.mp4"
            
            print("\nGenerating test video...")
            cmd = [
                ffmpeg_path,
                "-f", "lavfi",
                "-i", "testsrc=duration=2:size=320x240:rate=30",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",  # Overwrite output file if it exists
                str(test_file)
            ]
            
            print("Running command:", " ".join(cmd))
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print("❌ FFmpeg command failed:")
                    print(result.stderr)
                    return 1
                
                if test_file.exists():
                    size_mb = test_file.stat().st_size / (1024 * 1024)
                    print(f"✅ Successfully generated test video: {test_file}")
                    print(f"    Size: {size_mb:.2f} MB")
                    return 0
                else:
                    print("❌ Test video was not created")
                    return 1
                    
            except Exception as e:
                print(f"❌ Error running FFmpeg: {e}")
                return 1
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
