#!/usr/bin/env python3
"""
Verify the video generation environment
"""
import os
import sys
import platform
import subprocess
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
logger = logging.getLogger("env_check")

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f" {text}")
    print("=" * 50)

def check_python():
    """Check Python environment."""
    print_header("PYTHON ENVIRONMENT")
    print(f"Python Version: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Default Encoding: {sys.getdefaultencoding()}")

def check_ffmpeg():
    """Check FFmpeg installation."""
    print_header("FFMPEG CHECK")
    
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("❌ FFmpeg not found in PATH")
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
        print(f"❌ Error running FFmpeg: {e.stderr}")
        return False

def check_packages():
    """Check required Python packages."""
    print_header("PYTHON PACKAGES")
    
    packages = ["numpy", "Pillow", "moviepy", "imageio", "imageio_ffmpeg"]
    missing = []
    
    for pkg in packages:
        try:
            module = __import__(pkg)
            print(f"✓ {pkg}: {getattr(module, '__version__', 'unknown version')}")
        except ImportError:
            print(f"❌ {pkg}: not installed")
            missing.append(pkg)
    
    if missing:
        print("\nMissing packages. Install with:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def test_video_generation():
    """Test video generation with MoviePy."""
    print_header("VIDEO GENERATION TEST")
    
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
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]
        
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
        
        # Verify the output file
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Success! Video created: {output_file} ({file_size:.2f} MB)")
            return True
        else:
            print("❌ Error: Video file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during video generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all checks."""
    print("\n=== YTLite Environment Check ===\n")
    
    # Run all checks
    check_python()
    ffmpeg_ok = check_ffmpeg()
    packages_ok = check_packages()
    
    if ffmpeg_ok and packages_ok:
        print_header("RUNNING VIDEO GENERATION TEST")
        test_video_generation()
    else:
        print("\n❌ Skipping video generation test due to missing dependencies.")
    
    print("\nCheck complete!")

if __name__ == "__main__":
    import shutil  # Moved here to avoid shadowing the function
    sys.exit(main() if 'main' in locals() else 0)
