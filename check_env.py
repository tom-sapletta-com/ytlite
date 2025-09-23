#!/usr/bin/env python3
"""
Comprehensive environment check for YTLite
"""
import os
import sys
import platform
import subprocess
import importlib.util
from pathlib import Path

def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def check_system():
    """Check system information."""
    print_header("SYSTEM INFORMATION")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")

def check_python():
    """Check Python environment."""
    print_header("PYTHON ENVIRONMENT")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Directory: {Path.cwd()}")
    print(f"Python Path: {sys.path}")

def check_ffmpeg():
    """Check FFmpeg installation."""
    print_header("FFMPEG CHECK")
    
    # Check if ffmpeg is in PATH
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

def check_packages():
    """Check required Python packages."""
    print_header("PYTHON PACKAGES")
    
    packages = [
        'yaml', 'markdown', 'frontmatter',
        'edge_tts', 'moviepy', 'PIL',
        'imageio_ffmpeg', 'googleapiclient',
        'flask', 'pytest'
    ]
    
    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}: Installed")
        except ImportError:
            print(f"❌ {pkg}: Not installed")
            all_ok = False
    
    return all_ok

def check_file_permissions():
    """Check file permissions."""
    print_header("FILE PERMISSIONS")
    
    test_file = Path("test_permission.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        test_file.unlink()
        print("✅ Can write to current directory")
        return True
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")
        return False

def main():
    """Main function to run all checks."""
    print("YTLite Environment Check")
    print("=======================")
    
    check_system()
    check_python()
    ffmpeg_ok = check_ffmpeg()
    packages_ok = check_packages()
    file_perms_ok = check_file_permissions()
    
    print_header("SUMMARY")
    print(f"FFmpeg: {'✅' if ffmpeg_ok else '❌'}")
    print(f"Python Packages: {'✅' if packages_ok else '❌'}")
    print(f"File Permissions: {'✅' if file_perms_ok else '❌'}")
    
    if not ffmpeg_ok:
        print("\nFFmpeg is required for video processing. Please install it:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
    
    if not packages_ok:
        print("\nSome Python packages are missing. Install them with:")
        print("  pip install -r requirements.txt")
    
    if not file_perms_ok:
        print("\nCannot write to current directory. Check permissions.")

if __name__ == "__main__":
    main()
