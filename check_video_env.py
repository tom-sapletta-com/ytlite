#!/usr/bin/env python3
"""
Check video generation environment and test basic functionality
"""
import os
import sys
import platform
import subprocess
import shutil
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_env_check")

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}")

def check_python_version():
    """Check Python version and environment."""
    print_section("Python Environment")
    print(f"Python version: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Default encoding: {sys.getdefaultencoding()}")

def check_ffmpeg():
    """Check if FFmpeg is installed and working."""
    print_section("FFmpeg Check")
    
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print(f"{Colors.FAIL}✗ FFmpeg not found in PATH{Colors.ENDC}")
        return False
    
    print(f"FFmpeg found at: {ffmpeg_path}")
    
    # Get version
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_line = result.stdout.split('\n')[0]
        print(f"FFmpeg version: {version_line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}✗ Error running FFmpeg: {e.stderr}{Colors.ENDC}")
        return False

def check_packages():
    """Check required Python packages."""
    print_section("Python Packages")
    
    packages = ["numpy", "Pillow", "moviepy", "imageio", "imageio_ffmpeg"]
    missing = []
    
    for pkg in packages:
        try:
            module = __import__(pkg)
            print(f"✓ {pkg}: {getattr(module, '__version__', 'unknown version')}")
        except ImportError:
            print(f"{Colors.FAIL}✗ {pkg}: not installed{Colors.ENDC}")
            missing.append(pkg)
    
    if missing:
        print(f"\n{Colors.WARNING}Missing packages. Install with:{Colors.ENDC}")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def test_video_generation():
    """Test basic video generation."""
    print_section("Video Generation Test")
    
    try:
        import numpy as np
        from moviepy.editor import ImageClip
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "test_video.mp4"
        
        # Clean up any existing file
        if output_file.exists():
            output_file.unlink()
        
        # Create a simple blue frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]  # Blue
        
        # Create a 2-second clip
        clip = ImageClip(frame).set_duration(2)
        
        # Write the video
        print(f"Creating test video: {output_file}")
        clip.write_videofile(
            str(output_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=True,
            logger=None
        )
        
        # Verify the file was created
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"{Colors.OKGREEN}✓ Success! Video created: {output_file} ({file_size:.2f} MB){Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}✗ Error: Video file was not created{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error during video generation: {str(e)}{Colors.ENDC}")
        logger.exception("Video generation failed")
        return False

def main():
    """Run all checks."""
    print(f"{Colors.HEADER}{Colors.BOLD}=== YTLite Video Environment Check ==={Colors.ENDC}")
    
    # Run all checks
    check_python_version()
    ffmpeg_ok = check_ffmpeg()
    packages_ok = check_packages()
    
    if ffmpeg_ok and packages_ok:
        print_section("Running Video Generation Test")
        test_video_generation()
    else:
        print(f"\n{Colors.WARNING}Skipping video generation test due to missing dependencies.{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}Check complete!{Colors.ENDC}")

if __name__ == "__main__":
    main()
