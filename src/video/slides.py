"""
Slide generation for video creation.

Handles the creation of individual slides with text and styling.
"""
from typing import Dict, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging
import os

from .fonts import FontManager
from .themes import ThemeManager

logger = logging.getLogger("video.slides")

class SlideGenerator:
    """Generates slides with styled text and backgrounds."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the slide generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.resolution = tuple(self.config.get("resolution", [1280, 720]))
        self.font_manager = FontManager(config)
        self.theme_manager = ThemeManager(config)
        
        # Font size mapping with more options
        self.font_size_map = {
            'xxs': 12,
            'xs': 16,
            'small': 24,
            'medium': 36,
            'large': 48,
            'xl': 64,
            'xxl': 72,
            'xxxl': 96,
            'extra small': 16,
            'extra large': 72,
            'extra-large': 72,
            'extra_large': 72,
            'huge': 96,
            'giant': 120
        }
        
        # Set default font size from config or use medium (36) as default
        self.default_font_size = max(12, min(120, int(self.config.get("font_size", 36))))
        logger.debug(f"Initialized SlideGenerator with default font size: {self.default_font_size}")
        
        # Log available font sizes for debugging
        logger.debug(f"Available font sizes: {self.font_size_map}")
    
    def create_slide(
        self,
        text: str = "",
        theme: str = "tech",
        lang: Optional[str] = None,
        template: str = "classic",
        font_size: Optional[Union[int, str]] = None,
        colors: Optional[Dict[str, str]] = None,
        image_path: Optional[Union[str, Path]] = None,
        **kwargs  # Accept any additional kwargs to be forward-compatible
    ) -> Image.Image:
        """Create a slide image with the given text and styling.
        
        Args:
            text: Text content for the slide
            theme: Theme name (e.g., 'tech', 'light', 'dark')
            lang: Language code for font selection
            template: Slide template ('classic', 'gradient', etc.)
            font_size: Font size as int or string ('small', 'medium', 'large')
            colors: Optional color overrides for the theme
            
        Returns:
            PIL Image containing the rendered slide
        """
        logger.debug(
            f"Creating slide - Theme: {theme}, Template: {template}, "
            f"Font size: {font_size}, Language: {lang}, Has text: {bool(text)}"
        )
        # Get theme colors with any overrides
        theme_colors = self.theme_manager.get_theme(theme).copy()
        if colors:
            theme_colors.update(colors)
        logger.debug(f"Using theme colors: {theme_colors}")
            
        # Extract image_path from kwargs if not provided directly
        if image_path is None:
            image_path = kwargs.get('image_path')
        
        # Create base image with background or load from image_path
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path).convert("RGB")
                # Resize if needed to match resolution
                if image.size != self.resolution:
                    image = image.resize(self.resolution, Image.Resampling.LANCZOS)
            except Exception as e:
                logger.warning(f"Failed to load image from {image_path}: {e}")
                image = Image.new("RGB", self.resolution, theme_colors["bg_color"])
        else:
            # Create a new image with background color
            image = Image.new("RGB", self.resolution, theme_colors["bg_color"])
            
            # Apply template-specific styling
            if template == "gradient":
                self._apply_gradient_background(image, theme_colors)
        
        # Prepare text rendering
        draw = ImageDraw.Draw(image)
        
        # Determine font size
        fsize = self._get_font_size(font_size)
        logger.debug(f"Using font size: {fsize}, Type: {type(fsize).__name__}")
        
        # Get appropriate font
        font = self.font_manager.get_font(fsize, lang)
        logger.debug(f"Loaded font: {font.getname() if hasattr(font, 'getname') else 'default'}")
        
        # Calculate text position and wrap text
        margin = 100
        max_width = self.resolution[0] - 2 * margin
        max_height = self.resolution[1] - 2 * margin
        
        # Wrap and render text
        wrapped_text = self._wrap_text(draw, text, font, max_width)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (self.resolution[0] - text_width) // 2
        y = (self.resolution[1] - text_height) // 2
        
        # Draw text with shadow for better readability
        shadow_color = self.theme_manager.get_contrast_color(theme_colors["bg_color"])
        if shadow_color == "#ffffff":
            shadow_color = "#00000020"  # Semi-transparent black shadow
        else:
            shadow_color = "#ffffff20"   # Semi-transparent white shadow
            
        # Draw shadow
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), wrapped_text, 
                 font=font, fill=shadow_color)
        
        # Draw main text
        text_color = theme_colors.get("text_color", "#ffffff")
        draw.text((x, y), wrapped_text, font=font, fill=text_color)
        
        return image
    
    def _get_font_size(self, size_spec: Optional[Union[int, str, float]]) -> int:
        """Convert font size specification to integer size.
        
        Args:
            size_spec: Either an integer size, a string key from font_size_map,
                     a numeric string (e.g., '48'), or None to use default.
                     Can also handle float values or float strings.
                     
        Returns:
            int: The resolved font size, guaranteed to be between 12 and 120
        """
        # Log the input for debugging
        input_type = type(size_spec).__name__
        logger.debug(f"_get_font_size called with: {size_spec} (type: {input_type})")
        
        # Handle None case first
        if size_spec is None:
            logger.debug(f"No font size specified, using default: {self.default_font_size}")
            return max(12, min(120, self.default_font_size))
        
        try:
            # Handle string inputs
            if isinstance(size_spec, str):
                # Clean the string
                clean_size = size_spec.strip().lower()
                logger.debug(f"Processing string font size: '{clean_size}'")
                
                # Check for named sizes first
                if clean_size in self.font_size_map:
                    size = self.font_size_map[clean_size]
                    logger.debug(f"Mapped named size '{clean_size}' to: {size}")
                    return max(12, min(120, size))
                
                # Handle 'extra large' variations
                if 'extra' in clean_size and 'large' in clean_size:
                    logger.debug("Detected 'extra large' font size, using 96")
                    return 96
                
                # Try to convert to number
                try:
                    # Handle decimal points and commas
                    num_str = clean_size.replace(',', '.')
                    size = float(num_str)
                    logger.debug(f"Converted string '{clean_size}' to number: {size}")
                    return max(12, min(120, int(round(size))))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert '{clean_size}' to number: {e}")
            
            # Handle numeric types (int, float)
            elif isinstance(size_spec, (int, float)):
                size = int(round(float(size_spec)))
                logger.debug(f"Using numeric font size: {size}")
                return max(12, min(120, size))
            
            # Handle other types that might be converted to string
            else:
                logger.warning(f"Unexpected font size type: {input_type}, attempting conversion")
                return self._get_font_size(str(size_spec))
                
        except Exception as e:
            logger.error(f"Error processing font size '{size_spec}': {e}", exc_info=True)
            
        # Fallback to default if anything goes wrong
        fallback = max(12, min(120, self.default_font_size))
        logger.warning(f"Using fallback font size: {fallback}")
        return fallback
    
    def _apply_gradient_background(self, image: Image.Image, colors: Dict[str, str]) -> None:
        """Apply a gradient background to the image.
        
        Args:
            image: Image to modify
            colors: Color dictionary with 'bg_color' and 'bg_color_2' keys
        """
        try:
            self.theme_manager.apply_gradient(
                image,
                colors.get("bg_color", "#1e1e2e"),
                colors.get("bg_color_2", "#3b3b5b")
            )
        except Exception as e:
            logger.warning(f"Failed to apply gradient: {e}")
    
    @staticmethod
    def _wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
                  max_width: int) -> str:
        """Wrap text to fit within the specified width.
        
        Args:
            draw: ImageDraw instance
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels
            
        Returns:
            Wrapped text with newlines
        """
        lines = []
        
        # Split into paragraphs
        paragraphs = text.split('\n')
        
        for para in paragraphs:
            if not para.strip():
                lines.append('')
                continue
                
            words = para.split()
            if not words:
                continue
                
            current_line = words[0]
            
            for word in words[1:]:
                # Test if adding the next word would exceed the width
                test_line = f"{current_line} {word}"
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                
                if width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            lines.append(current_line)
        
        return '\n'.join(lines)
