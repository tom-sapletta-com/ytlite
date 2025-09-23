#!/usr/bin/env python3
"""
Simple test of video generation with MoviePy
"""
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips
import os

def create_test_video():
    # Create a simple red frame
    frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]  # Red frame
    
    # Create a 2-second clip
    clip = ImageClip(frame).set_duration(2)
    
    # Write to file
    output_file = "test_output/simple_test.mp4"
    os.makedirs("test_output", exist_ok=True)
    
    print(f"Writing test video to: {output_file}")
    clip.write_videofile(
        output_file,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        verbose=True
    )
    
    print(f"Video created: {output_file}")
    return output_file

if __name__ == "__main__":
    output = create_test_video()
    print(f"Test complete. Video saved to: {output}")
    print(f"File exists: {os.path.exists(output)}")
    if os.path.exists(output):
        print(f"File size: {os.path.getsize(output) / 1024:.2f} KB")
