#!/usr/bin/env python3
"""
Diagnostic script for YTLite video generation
"""
import os
import sys
import platform
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Colors for output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{YELLOW}=== {text} ==={NC}")

def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}✓ {text}{NC}")

def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}✗ {text}{NC}")

def check_ffmpeg() -> Tuple[bool, Dict[str, Any]]:
    """Check if FFmpeg is available and working."""
    print_header("Checking FFmpeg Installation")
    
    result = {
        "installed": False,
        "version": None,
        "path": None,
        "codecs": {},
        "error": None
    }
    
    # Try to find FFmpeg
    try:
        # Try imageio_ffmpeg first
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            result["path"] = ffmpeg_path
            print(f"Found FFmpeg via imageio_ffmpeg: {ffmpeg_path}")
        except (ImportError, AttributeError):
            # Fall back to system FFmpeg
            try:
                ffmpeg_path = "ffmpeg"
                subprocess.run(
                    [ffmpeg_path, "-version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                result["path"] = ffmpeg_path
                print(f"Found system FFmpeg: {ffmpeg_path}")
            except (subprocess.SubprocessError, FileNotFoundError):
                result["error"] = "FFmpeg not found in PATH and imageio_ffmpeg not available"
                print_error("FFmpeg not found in PATH and imageio_ffmpeg not available")
                return False, result
    except Exception as e:
        result["error"] = str(e)
        print_error(f"Error checking FFmpeg: {e}")
        return False, result
    
    # Get FFmpeg version
    try:
        version_output = subprocess.run(
            [ffmpeg_path, "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ).stdout
        
        version_line = version_output.split('\n')[0]
        result["version"] = version_line
        print(f"FFmpeg version: {version_line}")
        
        # Check codecs
        codecs = subprocess.run(
            [ffmpeg_path, "-codecs"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ).stdout
        
        result["codecs"]["h264"] = "libx264" in codecs
        result["codecs"]["aac"] = "aac" in codecs
        
        print("Required codecs:")
        print(f"- libx264: {'✓' if result['codecs']['h264'] else '✗'}")
        print(f"- aac: {'✓' if result['codecs']['aac'] else '✗'}")
        
        result["installed"] = True
        print_success("FFmpeg is properly installed and configured")
        return True, result
        
    except subprocess.CalledProcessError as e:
        result["error"] = f"FFmpeg command failed: {e.stderr}"
        print_error(f"FFmpeg command failed: {e.stderr}")
        return False, result
    except Exception as e:
        result["error"] = str(e)
        print_error(f"Error checking FFmpeg: {e}")
        return False, result

def check_python_environment() -> Dict[str, Any]:
    """Check Python environment and installed packages."""
    print_header("Checking Python Environment")
    
    result = {
        "python_version": platform.python_version(),
        "packages": {}
    }
    
    print(f"Python version: {result['python_version']}")
    
    # Check required packages
    required_packages = [
        "moviepy", "numpy", "Pillow", "imageio", "imageio_ffmpeg"
    ]
    
    print("\nChecking required packages:")
    for pkg in required_packages:
        try:
            module = importlib.import_module(pkg)
            version = getattr(module, "__version__", "unknown")
            result["packages"][pkg] = version
            print(f"- {pkg}: {version} (✓)")
        except ImportError:
            result["packages"][pkg] = "not installed"
            print(f"- {pkg}: {RED}not installed{NC}")
    
    return result

def test_video_generation() -> Tuple[bool, Dict[str, Any]]:
    """Test basic video generation functionality."""
    print_header("Testing Video Generation")
    
    result = {
        "success": False,
        "output_file": None,
        "file_size": 0,
        "error": None
    }
    
    try:
        import numpy as np
        from moviepy.editor import ImageClip
        
        # Create test output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple frame (blue)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]  # Blue frame
        
        # Create a 2-second clip
        clip = ImageClip(frame).set_duration(2)
        
        # Output file path
        output_file = output_dir / "test_video.mp4"
        if output_file.exists():
            output_file.unlink()
        
        # Write the video
        print(f"Creating test video: {output_file}")
        clip.write_videofile(
            str(output_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        
        # Verify the output file
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            result.update({
                "success": True,
                "output_file": str(output_file.absolute()),
                "file_size": file_size
            })
            print_success(f"Test video created successfully: {output_file} ({file_size:.2f} MB)")
        else:
            result["error"] = "Output file was not created"
            print_error("Output file was not created")
            
    except Exception as e:
        result["error"] = str(e)
        print_error(f"Error during video generation: {e}")
    
    return result["success"], result

def main() -> int:
    """Main function to run all diagnostics."""
    print(f"{YELLOW}=== YTLite Video Generation Diagnostics ==={NC}")
    
    # Check Python environment
    env_info = check_python_environment()
    
    # Check FFmpeg
    ffmpeg_ok, ffmpeg_info = check_ffmpeg()
    
    # Test video generation if FFmpeg is available
    video_ok = False
    video_info = {}
    
    if ffmpeg_ok:
        video_ok, video_info = test_video_generation()
    
    # Print summary
    print_header("Diagnostic Summary")
    
    # Python environment summary
    print("Python Environment:")
    print(f"- Python version: {env_info['python_version']}")
    
    # FFmpeg summary
    print("\nFFmpeg:")
    if ffmpeg_ok:
        print("- Status: ✓ Installed and working")
        print(f"- Version: {ffmpeg_info.get('version', 'unknown')}")
        print("- Codecs:")
        print(f"  - libx264: {'✓' if ffmpeg_info.get('codecs', {}).get('h264') else '✗'}")
        print(f"  - aac: {'✓' if ffmpeg_info.get('codecs', {}).get('aac') else '✗'}")
    else:
        print("- Status: ✗ Not working")
        if ffmpeg_info.get("error"):
            print(f"  Error: {ffmpeg_info['error']}")
    
    # Video generation summary
    print("\nVideo Generation Test:")
    if video_ok:
        print("- Status: ✓ Success")
        print(f"- Output file: {video_info.get('output_file')}")
        print(f"- File size: {video_info.get('file_size', 0):.2f} MB")
    else:
        print("- Status: ✗ Failed")
        if video_info.get("error"):
            print(f"  Error: {video_info['error']}")
    
    # Final verdict
    print("\nDiagnostic Result:")
    if ffmpeg_ok and video_ok:
        print_success("✓ Your system is properly configured for video generation!")
        return 0
    else:
        print_error("✗ There are issues with your video generation setup.")
        print("\nRecommended actions:")
        
        if not ffmpeg_ok:
            print("1. Install or fix FFmpeg:")
            print("   - Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("   - macOS: brew install ffmpeg")
            print("   - Windows: Download from https://ffmpeg.org/download.html")
            
        if not video_ok and ffmpeg_ok:
            print("1. There might be permission issues or missing codecs.")
            print("   - Check if you have write permissions in the output directory")
            print("   - Verify that FFmpeg has the required codecs (libx264, aac)")
        
        print("\nFor more information, check the detailed output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
