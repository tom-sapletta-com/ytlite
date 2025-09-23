#!/usr/bin/env python3
"""
Debug script to capture detailed output from video generation
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the output and error."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result

def main():
    # Create a temporary directory
    with tempfile.TemporaryDirectory(prefix="ytlite_debug_") as temp_dir:
        temp_dir = Path(temp_dir)
        print(f"Using temporary directory: {temp_dir}")
        
        # Create a simple Python script to generate a video
        test_script = temp_dir / "test_video.py"
        with open(test_script, "w") as f:
            f.write('''
import numpy as np
from moviepy.editor import ImageClip
import sys

# Create a simple blue frame
frame = np.ones((480, 640, 3), dtype=np.uint8) * [0, 0, 255]

# Create a 2-second clip
clip = ImageClip(frame).set_duration(2)

# Save the video
output_file = "test_output.mp4"
print(f"Creating video: {output_file}")

# Write with verbose output
clip.write_videofile(
    output_file,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    verbose=True,
    logger=None
)

print(f"Video created: {output_file}")
''')
        
        # Run the test script
        print("\nRunning test script...")
        result = run_command([sys.executable, str(test_script)], cwd=temp_dir)
        
        # Print the output
        print("\n=== STDOUT ===")
        print(result.stdout)
        
        print("\n=== STDERR ===")
        print(result.stderr)
        
        # Check if the output file was created
        output_file = temp_dir / "test_output.mp4"
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"\n✅ Success! Video file created: {output_file} ({size_mb:.2f} MB)")
        else:
            print(f"\n❌ Error: Video file was not created")

if __name__ == "__main__":
    main()
