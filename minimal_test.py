#!/usr/bin/env python3
"""
Minimal test script for video generation
"""
import os
import numpy as np
from moviepy.editor import ImageClip

# Create a simple red frame (480p)
frame = np.ones((480, 640, 3), dtype=np.uint8) * [255, 0, 0]

# Create a 2-second clip
clip = ImageClip(frame).set_duration(2)

# Save the video
output_file = "minimal_test.mp4"
print(f"Creating test video: {output_file}")

clip.write_videofile(
    output_file,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    verbose=True
)

print(f"Test video created: {os.path.abspath(output_file)}")
print("You can play it with: xdg-open", output_file)
