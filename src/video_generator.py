#!/usr/bin/env python3
"""
YTLite Video Generator Module (Legacy)

This module is maintained for backward compatibility.
New code should import from the video package directly.
"""

import os
import warnings
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# Import from the new modular structure
from video.generator import VideoGenerator as NewVideoGenerator
from video.slides import SlideGenerator
from video.themes import ThemeManager
from video.fonts import FontManager
from video.utils import ensure_directory, validate_resolution

# For backward compatibility
__all__ = ['VideoGenerator']

# Show deprecation warning
warnings.warn(
    "The video_generator module is deprecated. Import from the video package instead.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy VideoGenerator class that wraps the new implementation
class VideoGenerator(NewVideoGenerator):
    """Legacy VideoGenerator class for backward compatibility.
    
    This class is a thin wrapper around the new VideoGenerator implementation
    from the video package. It's maintained for backward compatibility with
    existing code.
    
    New code should import from video.generator.VideoGenerator directly.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the legacy VideoGenerator.
        
        Args:
            config: Configuration dictionary
        """
        # Ensure required keys exist in config
        config = config or {}
        if 'resolution' in config:
            try:
                config['resolution'] = validate_resolution(config['resolution'])
            except ValueError as e:
                raise ValueError(f"Invalid resolution in config: {e}")
        
        # Initialize the new VideoGenerator
        super().__init__(config)
        
    # Legacy methods are now handled by the new implementation
    # The following methods are maintained for backward compatibility
    
    def create_slide(self, *args, **kwargs):
        """Legacy method to create a slide.
        
        This is now handled by the SlideGenerator class.
        """
        warnings.warn(
            "VideoGenerator.create_slide() is deprecated. " 
            "Use video.slides.SlideGenerator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Create a temporary SlideGenerator instance
        slide_gen = SlideGenerator(self.config)
        return slide_gen.create_slide(*args, **kwargs)
    
    def generate_video(self, *args, **kwargs):
        """Legacy method to generate a video.
        
        This is now handled by the VideoGenerator.create_video() method.
        """
        warnings.warn(
            "VideoGenerator.generate_video() is deprecated. "
            "Use VideoGenerator.create_video() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Map old parameters to new ones
        if args and isinstance(args[0], list):
            # Old signature: generate_video(slides, audio_path, output_path, duration)
            slides = args[0]
            audio_path = args[1] if len(args) > 1 else kwargs.get('audio_path')
            output_path = args[2] if len(args) > 2 else kwargs.get('output_path', 'output.mp4')
            duration = args[3] if len(args) > 3 else kwargs.get('duration', 5.0)
            
            # Convert slide paths to the new format
            slide_defs = [
                {'image_path': slide_path, 'duration': duration}
                for slide_path in slides
            ]
            
            # Create the video
            return self.create_video(
                output_path=output_path,
                slides=slide_defs,
                audio_path=audio_path
            )
        
        # For other cases, pass through to the new method
        return self.create_video(*args, **kwargs)
        
    def create_video_from_slides(self, slides: List[Union[str, dict]], audio_path: str, output_path: str):
        """Legacy method to create a video from slide images and audio.
        
        This is now handled by the VideoGenerator.create_video() method.
        """
        warnings.warn(
            "VideoGenerator.create_video_from_slides() is deprecated. "
            "Use VideoGenerator.create_video() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Convert slides to the new format
        slide_defs = []
        for slide in slides:
            if isinstance(slide, dict):
                # If it's already a dict, use it as is
                slide_defs.append(slide)
            else:
                # If it's a string, convert to dict with image_path
                slide_defs.append({'image_path': str(slide)})
        
        # Create the video using the new method
        return self.create_video(
            output_path=output_path,
            slides=slide_defs,
            audio_path=audio_path
        )
        
    def create_shorts(self, video_path: str, output_path: str):
        """Legacy method to create YouTube Shorts from a video.
        
        This is now handled by the VideoGenerator.create_video() method with appropriate parameters.
        """
        warnings.warn(
            "VideoGenerator.create_shorts() is deprecated. "
            "Use VideoGenerator.create_video() with appropriate parameters instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Create a video with default settings for Shorts
        return self.create_video(
            output_path=output_path,
            slides=[{'image_path': video_path}],
            resolution=(1080, 1920)  # Portrait mode for Shorts
        )
        # The actual implementation has been moved to the new VideoGenerator class

    def create_thumbnail(self, video_path: str, output_path: str, audio_path: Optional[str] = None):
        """Legacy method to create a thumbnail from a video with optional audio waveform.
        
        This is now handled by the VideoGenerator.create_thumbnail() method.
        """
        warnings.warn(
            "VideoGenerator.create_thumbnail() is deprecated. "
            "Use VideoGenerator.create_thumbnail() from the video package instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Delegate to the new implementation
        return super().create_thumbnail(
            video_path=video_path,
            output_path=output_path,
            audio_path=audio_path
        )
