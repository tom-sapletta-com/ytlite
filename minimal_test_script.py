#!/usr/bin/env python3
"""
Minimal test script for video generation
"""
import os
import sys
import numpy as np
from moviepy.editor import ImageClip

def main():
    print("Starting minimal video generation test...")
    
    try:
        # Create output directory
        os.makedirs("test_output", exist_ok=True)
        output_file = "test_output/minimal_test.mp4"
        
        # Create a simple frame (blue)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]  # Blue frame
        
        # Create a 2-second clip
        clip = ImageClip(frame).set_duration(2)
        
        # Write the video file
        print(f"Writing video to: {output_file}")
        clip.write_videofile(
            output_file,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=True,
            logger=None,
            threads=1
        )
        
        # Verify the file was created
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ Success! Video created: {output_file} ({size_mb:.2f} MB)")
            return True
        else:
            print("❌ Error: Video file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
