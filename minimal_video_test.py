#!/usr/bin/env python3
"""
Minimal video generation test with direct FFmpeg call
"""
import os
import subprocess
import tempfile
import base64

# Create a temporary directory for test files
temp_dir = tempfile.mkdtemp(prefix="ytlite_test_")
print(f"Using temporary directory: {temp_dir}")

def create_test_frame(output_path):
    """Create a simple test frame using ImageMagick."""
    try:
        # Use ImageMagick to create a simple test image
        cmd = [
            "convert",
            "-size", "640x480", "xc:blue",
            "-pointsize", "72",
            "-fill", "white",
            "-gravity", "center",
            "-draw", "text 0,0 'YTLite Test'",
            output_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error creating test frame: {e}")
        return False

def create_video_ffmpeg(image_path, output_path):
    """Create a video from a single image using FFmpeg directly."""
    try:
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-loop", "1",  # Loop the single image
            "-i", image_path,  # Input image
            "-c:v", "libx264",  # Video codec
            "-t", "3",  # 3 second duration
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            "-vf", "fps=24",  # Framerate
            output_path
        ]
        print("Running FFmpeg command:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("FFmpeg error:")
            print(result.stderr)
            return False
            
        print("FFmpeg output:")
        print(result.stdout)
        return True
        
    except Exception as e:
        print(f"Error running FFmpeg: {e}")
        return False

def main():
    # Paths for test files
    test_image = os.path.join(temp_dir, "test_frame.png")
    test_video = os.path.join(temp_dir, "test_video.mp4")
    
    print("1. Creating test frame...")
    if not create_test_frame(test_image):
        print("Failed to create test frame")
        return
    
    print(f"Test frame created: {test_image}")
    
    print("\n2. Creating test video...")
    if not create_video_ffmpeg(test_image, test_video):
        print("Failed to create test video")
        return
    
    print(f"\nTest video created: {test_video}")
    
    # Check if the video file was created
    if os.path.exists(test_video):
        size_mb = os.path.getsize(test_video) / (1024 * 1024)
        print(f"\n✅ Success! Video file size: {size_mb:.2f} MB")
        print(f"You can play the video with: xdg-open {test_video}")
    else:
        print("\n❌ Error: Video file was not created")

if __name__ == "__main__":
    main()
