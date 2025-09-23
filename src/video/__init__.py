"""
Video generation module for YTLite.

This package contains components for generating videos from text and images.
"""

__version__ = "0.1.0"

# Import main components to make them available at the package level
from .generator import VideoGenerator
from .fonts import FontManager
from .themes import ThemeManager
from .slides import SlideGenerator

__all__ = [
    'VideoGenerator',
    'FontManager',
    'ThemeManager',
    'SlideGenerator',
]
