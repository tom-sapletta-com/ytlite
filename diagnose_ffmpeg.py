#!/usr/bin/env python3
"""
Diagnostic script to test FFmpeg and video generation
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Colors for output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color

def print_section(title):
    """Print a section header."""
    print(f"\n{YELLOW}=== {title} ==={NC}")

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed with code {e.returncode}{NC}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        raise

def test_ffmpeg():
    """Test if FFmpeg is installed and working."""
    print_section("Testing FFmpeg Installation")
    
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print(f"{RED}✗ FFmpeg not found in PATH{NC}")
        return False
    
    print(f"FFmpeg found at: {ffmpeg_path}")
    
    # Get version
    try:
        version_result = run_command([ffmpeg_path, "-version"])
        version_line = version_result.stdout.split('\n')[0]
        print(f"FFmpeg version: {version_line}")
        return True
    except Exception as e:
        print(f"{RED}✗ Error checking FFmpeg version: {e}{NC}")
        return False

def create_test_video():
    """Create a simple test video using FFmpeg directly."""
    print_section("Creating Test Video with FFmpeg")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        print(f"Using temporary directory: {tmpdir}")
        
        # Create a simple red frame with FFmpeg
        output_file = tmpdir / "test_video.mp4"
        
        # FFmpeg command to create a test video
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-f", "lavfi",
            "-i", "color=c=red:s=640x480:d=2",  # 2 second red video
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            str(output_file)
        ]
        
        try:
            run_command(cmd)
            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"{GREEN}✓ Success! Video created: {output_file} ({size_mb:.2f} MB){NC}")
                return True
            else:
                print(f"{RED}✗ Error: Video file was not created{NC}")
                return False
                
        except Exception as e:
            print(f"{RED}✗ Error creating video: {e}{NC}")
            return False

def main():
    """Main function to run all tests."""
    print(f"{YELLOW}=== YTLite Video Generation Diagnostics ==={NC}")
    
    # Check FFmpeg
    ffmpeg_ok = test_ffmpeg()
    
    # Test video generation if FFmpeg is available
    video_ok = False
    if ffmpeg_ok:
        video_ok = create_test_video()
    
    # Print summary
    print_section("Test Summary")
    print(f"FFmpeg: {'✓' if ffmpeg_ok else '✗'}")
    print(f"Video Generation: {'✓' if video_ok else '✗'}")
    
    if ffmpeg_ok and video_ok:
        print(f"\n{GREEN}✓ Your system is properly configured for video generation!{NC}")
        return 0
    else:
        print(f"\n{RED}✗ There are issues with your video generation setup.{NC}")
        return 1

if __name__ == "__main__":
    import shutil  # Moved here to avoid shadowing the function
    sys.exit(main())
