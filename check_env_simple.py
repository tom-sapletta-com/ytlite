#!/usr/bin/env python3
# Simple environment check script

import os
import sys
import platform

def main():
    print("Environment Check")
    print("================")
    
    # Basic system info
    print("\nSystem Information:")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    
    # Python info
    print("\nPython Information:")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check FFmpeg
    print("\nChecking for FFmpeg:")
    try:
        import subprocess
        result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ FFmpeg found at: {result.stdout.strip()}")
            
            # Try to get version
            version = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True
            )
            if version.returncode == 0:
                print(f"FFmpeg version: {version.stdout.split('\n')[0]}")
            else:
                print("❌ Could not get FFmpeg version")
                print(version.stderr)
        else:
            print("❌ FFmpeg not found in PATH")
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
    
    # Check Python packages
    print("\nChecking Python packages:")
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
    
    # Check file permissions
    print("\nChecking file permissions:")
    try:
        with open("test_permission.txt", "w") as f:
            f.write("test")
        os.remove("test_permission.txt")
        print("✅ Can write to current directory")
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")

if __name__ == "__main__":
    main()
