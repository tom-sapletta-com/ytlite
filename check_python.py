#!/usr/bin/env python3
# Simple script to verify Python environment and FFmpeg
import os
import sys
import subprocess

def main():
    print("Python Environment Check")
    print("======================")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check FFmpeg
    print("\nChecking FFmpeg...")
    try:
        result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ FFmpeg found at: {result.stdout.strip()}")
            
            # Get FFmpeg version
            version = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True
            )
            if version.returncode == 0:
                print("FFmpeg Version:")
                print(version.stdout.split('\n')[0])
            else:
                print("❌ Could not get FFmpeg version")
        else:
            print("❌ FFmpeg not found in PATH")
            
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
    
    # Check Python packages
    print("\nChecking Python packages...")
    packages = [
        'yaml', 'markdown', 'frontmatter',
        'edge_tts', 'moviepy', 'PIL',
        'imageio_ffmpeg', 'googleapiclient',
        'flask', 'pytest'
    ]
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}: Installed")
        except ImportError:
            print(f"❌ {pkg}: Not installed")
    
    print("\nEnvironment check complete!")

if __name__ == "__main__":
    main()
