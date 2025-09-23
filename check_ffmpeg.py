#!/usr/bin/env python3
"""
Check if FFmpeg is installed and working
"""
import subprocess
import sys

def main():
    print("FFmpeg Check")
    print("============")
    
    # Check if FFmpeg is installed
    try:
        # Check if 'which' command works
        which_result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        
        if which_result.returncode != 0:
            print("❌ FFmpeg not found in PATH")
            return 1
            
        ffmpeg_path = which_result.stdout.strip()
        print(f"✅ FFmpeg found at: {ffmpeg_path}")
        
        # Get FFmpeg version
        version_result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True
        )
        
        if version_result.returncode != 0:
            print("❌ Could not get FFmpeg version")
            print(version_result.stderr)
            return 1
            
        print("\nFFmpeg Version:")
        print(version_result.stdout.split('\n')[0])
        
        # Test FFmpeg with a simple command
        print("\nTesting FFmpeg with a simple command...")
        test_result = subprocess.run(
            [ffmpeg_path, "-f", "lavfi", "-i", "sine=frequency=1000:duration=1", "-f", "null", "-"],
            capture_output=True,
            text=True
        )
        
        if test_result.returncode == 0:
            print("✅ FFmpeg is working correctly!")
            return 0
        else:
            print("❌ FFmpeg test failed:")
            print(test_result.stderr)
            return 1
            
    except FileNotFoundError:
        print("❌ 'which' command not found. This script requires a Unix-like system.")
        return 1
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
