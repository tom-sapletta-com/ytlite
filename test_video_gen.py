#!/usr/bin/env python3
"""
Test script to verify video generation with the updated VideoGenerator
"""
import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_video_gen")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_video_generation():
    """Test video generation with the updated VideoGenerator."""
    try:
        from video_generator import VideoGenerator
        from PIL import Image, ImageDraw
        import tempfile
        import numpy as np
        
        # Create a test output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a test config
        config = {
            "resolution": [1280, 720],
            "fps": 30,
            "font_size": 48
        }
        
        # Initialize video generator
        vg = VideoGenerator(config)
        
        # Create a test slide
        def create_test_slide(text, output_path):
            """Create a test slide with some text."""
            img = Image.new('RGB', (1280, 720), color=(70, 70, 70))
            d = ImageDraw.Draw(img)
            d.text((100, 300), text, fill=(255, 255, 255), font_size=72)
            img.save(output_path)
            return output_path
        
        # Create test slides
        slides = []
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Create 3 test slides
            for i in range(1, 4):
                slide_path = temp_dir / f"slide_{i}.png"
                create_test_slide(f"Test Slide {i}", slide_path)
                slides.append(str(slide_path))
                logger.info(f"Created test slide: {slide_path}")
            
            # Create a test audio file (5 seconds of silence)
            from scipy.io import wavfile
            sample_rate = 44100
            t = np.linspace(0, 5, int(sample_rate * 5), False)
            audio_data = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
            audio_path = temp_dir / "test_audio.wav"
            wavfile.write(audio_path, sample_rate, audio_data)
            logger.info(f"Created test audio: {audio_path}")
            
            # Generate video
            output_path = output_dir / "test_output.mp4"
            logger.info(f"Generating video to: {output_path}")
            
            vg.create_video_from_slides(
                slides=slides,
                audio_path=str(audio_path),
                output_path=str(output_path)
            )
            
            # Verify output
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Video generated successfully: {output_path} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("✗ Video file was not created")
                return False
                
    except Exception as e:
        logger.error(f"Error in test_video_generation: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_video_generation()
    sys.exit(0 if success else 1)
