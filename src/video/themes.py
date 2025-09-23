"""
Theme and color management for video generation.

Handles theme configurations, color schemes, and gradient generation.
"""
from typing import Dict, Tuple, Optional, Union
from PIL import Image, ImageDraw
import logging

logger = logging.getLogger("video.themes")

class ThemeManager:
    """Manages themes and color schemes for video generation."""
    
    # Default themes
    DEFAULT_THEMES = {
        "tech": {
            "bg_color": "#1e1e2e",
            "bg_color_2": "#3b3b5b",
            "text_color": "#cdd6f4",
            "accent_color": "#89b4fa",
            "highlight_color": "#f5c2e7"
        },
        "light": {
            "bg_color": "#f5f5f5",
            "bg_color_2": "#e0e0e0",
            "text_color": "#333333",
            "accent_color": "#1a73e8",
            "highlight_color": "#0d47a1"
        },
        "dark": {
            "bg_color": "#121212",
            "bg_color_2": "#1e1e1e",
            "text_color": "#e0e0e0",
            "accent_color": "#bb86fc",
            "highlight_color": "#03dac6"
        },
        "nature": {
            "bg_color": "#1b5e20",
            "bg_color_2": "#2e7d32",
            "text_color": "#e8f5e9",
            "accent_color": "#a5d6a7",
            "highlight_color": "#e8f5e9"
        }
    }
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the theme manager with optional configuration.
        
        Args:
            config: Configuration dictionary that may contain 'themes' and 'default_theme'
        """
        self.config = config or {}
        self.themes = self.DEFAULT_THEMES.copy()
        
        # Update with any custom themes from config
        if 'themes' in self.config and isinstance(self.config['themes'], dict):
            self.themes.update(self.config['themes'])
        
        self.default_theme = self.config.get('default_theme', 'tech')
    
    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get a theme by name, falling back to default if not found.
        
        Args:
            theme_name: Name of the theme to retrieve
            
        Returns:
            Dictionary of color values for the theme
        """
        theme_name = theme_name or self.default_theme
        return self.themes.get(theme_name, self.themes[self.default_theme])
    
    def get_color(self, theme_name: Optional[str], color_key: str, default: str) -> str:
        """Get a specific color from a theme with a fallback.
        
        Args:
            theme_name: Name of the theme
            color_key: Key of the color to retrieve
            default: Default value if the color is not found
            
        Returns:
            Color value as a hex string
        """
        theme = self.get_theme(theme_name)
        return theme.get(color_key, default)
    
    def apply_gradient(self, image: Image.Image, start_color: str, end_color: str) -> Image.Image:
        """Apply a gradient background to an image.
        
        Args:
            image: PIL Image to modify
            start_color: Starting color as hex string
            end_color: Ending color as hex string
            
        Returns:
            Modified image with gradient background
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Parse colors
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        
        # Draw gradient
        for y in range(height):
            ratio = y / max(1, height - 1)
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        return image
    
    @staticmethod
    def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
        """Convert a hex color string to RGB tuple.
        
        Args:
            hex_str: Color as hex string (with or without #)
            
        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
            
        try:
            return (
                int(hex_str[0:2], 16),
                int(hex_str[2:4], 16),
                int(hex_str[4:6], 16)
            )
        except (ValueError, IndexError):
            # Default to dark gray on error
            return (30, 30, 46)
    
    def get_contrast_color(self, hex_color: str) -> str:
        """Get a contrasting color (black or white) for the given color.
        
        Args:
            hex_color: Background color as hex string
            
        Returns:
            '#000000' for light backgrounds, '#ffffff' for dark backgrounds
        """
        r, g, b = self.hex_to_rgb(hex_color)
        # Calculate relative luminance (perceived brightness)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return '#000000' if luminance > 0.5 else '#ffffff'
