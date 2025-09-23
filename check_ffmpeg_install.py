#!/usr/bin/env python3
"""
Check FFmpeg installation and MoviePy configuration
"""
import os
import sys
import subprocess
from moviepy.config import get_setting

def check_ffmpeg():
    print("FFmpeg Check")
    print("============")
    
    # Check if FFmpeg is in PATH
    try:
        result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip()
            print(f"✅ FFmpeg found at: {ffmpeg_path}")
            
            # Get FFmpeg version
            version = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True
            )
            if version.returncode == 0:
                print("FFmpeg Version:")
                print(version.stdout.split('\n')[0])
                return True
            else:
                print("❌ Could not get FFmpeg version")
                print(version.stderr)
                return False
        else:
            print("❌ FFmpeg not found in PATH")
            return False
            
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def check_moviepy_ffmpeg():
    print("\nMoviePy FFmpeg Configuration")
    print("==========================")
    
    try:
        # Check MoviePy's FFmpeg configuration
        ffmpeg_binary = get_setting("FFMPEG_BINARY")
        print(f"MoviePy FFmpeg binary: {ffmpeg_binary}")
        
        if not ffmpeg_binary:
            print("❌ MoviePy could not find FFmpeg")
            return False
            
        # Check if the binary exists
        if isinstance(ffmpeg_binary, list):
            ffmpeg_path = ffmpeg_binary[0]
        else:
            ffmpeg_path = ffmpeg_binary
            
        if os.path.exists(ffmpeg_path):
            print(f"✅ FFmpeg binary exists at: {ffmpeg_path}")
            return True
        else:
            print(f"❌ FFmpeg binary not found at: {ffmpeg_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking MoviePy FFmpeg config: {e}")
        return False

def main():
    ffmpeg_ok = check_ffmpeg()
    moviepy_ok = check_moviepy_ffmpeg()
    
    print("\nSummary")
    print("=======")
    print(f"FFmpeg installed: {'✅' if ffmpeg_ok else '❌'}")
    print(f"MoviePy FFmpeg configured: {'✅' if moviepy_ok else '❌'}")
    
    if not ffmpeg_ok or not moviepy_ok:
        print("\nTroubleshooting:")
        print("1. Install FFmpeg:")
        print("   - Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        print("2. Add FFmpeg to your PATH")
        print("3. Restart your Python environment")
        print("4. If using a virtual environment, ensure it's activated")
        
        # Try to find FFmpeg in common locations
        print("\nCommon FFmpeg locations:")
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ Found FFmpeg at: {path}")
            
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
