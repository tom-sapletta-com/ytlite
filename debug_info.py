#!/usr/bin/env python3
"""
Debug information collection script
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def collect_system_info():
    """Collect basic system information."""
    print_section("SYSTEM INFORMATION")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Current directory: {Path.cwd()}")

def collect_python_info():
    """Collect Python environment information."""
    print_section("PYTHON ENVIRONMENT")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    
    # Check virtual environment
    print("\nVirtual environment:")
    print(f"  In virtualenv: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
    print(f"  Prefix: {sys.prefix}")
    if hasattr(sys, 'base_prefix'):
        print(f"  Base prefix: {sys.base_prefix}")

def check_ffmpeg():
    """Check FFmpeg installation."""
    print_section("FFMPEG CHECK")
    
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
                print("FFmpeg version:")
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

def check_imports():
    """Check if required Python packages can be imported."""
    print_section("PYTHON IMPORTS")
    
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
            print(f"✅ {pkg}: Import successful")
        except ImportError as e:
            print(f"❌ {pkg}: {e}")
            all_ok = False
    
    return all_ok

def check_file_permissions():
    """Check file system permissions."""
    print_section("FILE PERMISSIONS")
    
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
    print("YTLite Debug Information")
    print("=======================")
    
    collect_system_info()
    collect_python_info()
    ffmpeg_ok = check_ffmpeg()
    imports_ok = check_imports()
    file_perms_ok = check_file_permissions()
    
    print_section("SUMMARY")
    print(f"FFmpeg: {'✅' if ffmpeg_ok else '❌'}")
    print(f"Python Imports: {'✅' if imports_ok else '❌'}")
    print(f"File Permissions: {'✅' if file_perms_ok else '❌'}")
    
    if not ffmpeg_ok:
        print("\nFFmpeg is required for video processing. Please install it:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
    
    if not imports_ok:
        print("\nSome Python packages are missing. Install them with:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
