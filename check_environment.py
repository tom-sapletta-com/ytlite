#!/usr/bin/env python3
"""
Check the Python environment and dependencies for YTLite
"""
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

def check_python():
    """Check Python version and environment."""
    print_header("PYTHON ENVIRONMENT")
    
    # Python version
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Directory: {Path.cwd()}")
    
    # Virtual environment
    print("\nVirtual Environment:")
    print(f"  In Virtual Environment: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
    print(f"  Prefix: {sys.prefix}")
    if hasattr(sys, 'base_prefix'):
        print(f"  Base Prefix: {sys.base_prefix}")

def check_dependencies():
    """Check required dependencies."""
    print_header("DEPENDENCIES")
    
    required = [
        'yaml', 'markdown', 'python_frontmatter',
        'edge_tts', 'moviepy', 'PIL', 'imageio_ffmpeg',
        'googleapiclient', 'google_auth_oauthlib',
        'click', 'rich', 'requests', 'schedule', 'python_dotenv',
        'flask', 'uvicorn', 'pytest', 'playwright'
    ]
    
    for package in required:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown version')
                print(f"✅ {package}: {version}")
            except Exception as e:
                print(f"❌ {package}: Error loading - {str(e)}")
        else:
            print(f"❌ {package}: Not installed")

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
    print_header("FFMPEG CHECK")
    
    try:
        # Try to get FFmpeg version
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

def check_environment():
    """Check the entire environment."""
    check_python()
    check_dependencies()
    ffmpeg_ok = check_ffmpeg()
    
    print_header("ENVIRONMENT CHECK SUMMARY")
    if ffmpeg_ok:
        print("✅ FFmpeg is properly installed")
    else:
        print("❌ FFmpeg is not installed or not working")
        print("\nTo install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("\nOr install with conda:")
        print("  conda install -c conda-forge ffmpeg")

if __name__ == "__main__":
    check_environment()
