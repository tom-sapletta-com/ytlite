#!/usr/bin/env python3
"""
Minimal check for video generation
"""
import os
import sys
import numpy as np
from moviepy.editor import ImageClip

def main():
    print("Testing video generation...")
    
    # Create output directory
    os.makedirs("test_output", exist_ok=True)
    output_file = "test_output/minimal_test.mp4"
    
    try:
        # Create a simple frame (red)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]
        
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
            logger=None
        )
        
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ Success! Video created: {output_file} ({size_mb:.2f} MB)")
            return 0
        else:
            print("❌ Error: Video file was not created")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
