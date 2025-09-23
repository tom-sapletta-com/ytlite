"""
Font management for video generation.

Handles font loading, caching, and fallback mechanisms.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Tuple, Union
from PIL import ImageFont
from rich.console import Console
import logging

logger = logging.getLogger("video.fonts")
console = Console()

class FontManager:
    """Manages font loading and caching for video generation.
    
    Handles font path resolution, size management, and provides fallback fonts
    when the requested font is not available.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the font manager with optional configuration.
        
        Args:
            config: Configuration dictionary that may contain 'font_path' and 'font_size'
        """
        self.config = config or {}
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._font_warning_emitted = False
        
    def get_font(self, size: int, lang: Optional[str] = None) -> ImageFont.FreeTypeFont:
        """Get a font with the specified size, optionally considering language.
        
        Args:
            size: Font size in points
            lang: Optional language code to influence font selection
            
        Returns:
            A PIL ImageFont object
        """
        try:
            # Ensure size is an integer
            size = int(size)
            logger.debug(f"Requested font - Size: {size}, Language: {lang}")
            
            # Try to find the best font for the language
            font_path = self._find_font_path(lang)
            cache_key = (font_path, size)
            
            # Return cached font if available
            if cache_key in self._font_cache:
                logger.debug(f"Using cached font: {font_path} at size {size}")
                return self._font_cache[cache_key]
                
            # Try to load the font
            try:
                if font_path and os.path.isfile(font_path):
                    logger.debug(f"Attempting to load font from: {font_path}")
                    font = ImageFont.truetype(font_path, size)
                    self._font_cache[cache_key] = font
                    logger.info(f"Successfully loaded font from {font_path} at size {size}")
                    return font
                else:
                    logger.warning(f"Font file not found at {font_path}")
                    self._warn_fallback()
                    
                # Try to load a default font
                try:
                    logger.debug("Attempting to load system default font")
                    font = ImageFont.load_default()
                    logger.info("Using system default font")
                    return font
                except Exception as e:
                    logger.error(f"Failed to load default font: {e}")
                    # As a last resort, create a basic font
                    font = ImageFont.load_default()
                    logger.warning("Using fallback basic font")
                    return font
                    
            except Exception as e:
                logger.error(f"Error loading font from {font_path} at size {size}: {e}", exc_info=True)
                self._warn_fallback()
                return ImageFont.load_default()
                
        except Exception as e:
            logger.critical(f"Critical error in get_font: {e}", exc_info=True)
            return ImageFont.load_default()
    
    def _find_font_path(self, lang: Optional[str] = None) -> str:
        """Find the most appropriate font path based on configuration and language.
        
        Args:
            lang: Optional language code to influence font selection
            
        Returns:
            Path to a font file
        """
        logger.debug(f"Finding font path for language: {lang}")
        
        # Check config and environment for font path overrides
        font_path = self.config.get("font_path")
        if font_path:
            logger.debug(f"Checking configured font path: {font_path}")
            if os.path.isfile(font_path):
                logger.info(f"Using font from config: {font_path}")
                return font_path
            else:
                logger.warning(f"Configured font not found: {font_path}")
        
        # Check environment variables
        for env_var in ["YTLITE_FONT_PATH", "FONT_PATH"]:
            env_font = os.getenv(env_var)
            if env_font:
                logger.debug(f"Checking environment variable {env_var}: {env_font}")
                if os.path.isfile(env_font):
                    logger.info(f"Using font from {env_var}: {env_font}")
                    return env_font
                else:
                    logger.warning(f"Font from {env_var} not found: {env_font}")
        
        # Language-specific font selection
        if lang:
            lang_font = self._get_language_specific_font(lang)
            if lang_font and os.path.isfile(lang_font):
                logger.debug(f"Using language-specific font for {lang}: {lang_font}")
                return lang_font
        
        # Common system font locations - expanded list
        common_fonts = [
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            
            # macOS
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial.ttf",
            
            # Windows
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\ArialUni.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            
            # Common fallbacks
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSans-Regular.otf",
        ]
        
        # Check for any available font
        available_fonts = []
        for font in common_fonts:
            if os.path.isfile(font):
                available_fonts.append(font)
        
        if available_fonts:
            logger.debug(f"Found available system fonts: {available_fonts}")
            return available_fonts[0]
        
        # Try to find any .ttf or .otf file in common font directories
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/.local/share/fonts"),
            os.path.expanduser("~/.fonts"),
        ]
        
        for font_dir in font_dirs:
            if os.path.isdir(font_dir):
                for root, _, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(root, file)
                            logger.debug(f"Found font file: {font_path}")
                            return font_path
        
        logger.warning("No suitable font files found in common locations")
        return ""
    
    def _warn_fallback(self) -> None:
        """Log a warning about falling back to default font.
        
        Only logs the warning once per FontManager instance to avoid log spam.
        """
        if not self._font_warning_emitted:
            logger.warning(
                "Falling back to default font. To use custom fonts, set the 'font_path' in config "
                "or the 'YTLITE_FONT_PATH' environment variable to point to a valid font file."
            )
            self._font_warning_emitted = True
    
    def _get_language_specific_font(self, lang: str) -> Optional[str]:
        """Get a font that supports the specified language.
        
        Args:
            lang: Language code (e.g., 'en', 'ja', 'zh')
            
        Returns:
            Path to a font file that supports the language, or None
        """
        # Map of language codes to font paths
        lang_fonts = {
            # East Asian fonts
            'ja': [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                'C:\\Windows\\Fonts\\msgothic.ttc',
            ],
            'ko': [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                'C:\\Windows\\Fonts\\malgun.ttf',
            ],
            'zh': [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                'C:\\Windows\\Fonts\\msyh.ttc',
            ],
            # Other languages
            'ar': [
                '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
                '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf',
            ],
            'he': [
                '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
                '/usr/share/fonts/truetype/culmus/DejaVuSans-Bold.ttf',
            ],
            'th': [
                '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
                '/usr/share/fonts/truetype/tlwg/Garuda.ttf',
            ],
            'hi': [
                '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
                '/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf',
            ],
            'bn': [
                '/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf',
                '/usr/share/fonts/truetype/lohit-bengali/Lohit-Bengali.ttf',
            ],
        }
        
        # Get the language family (first part of language code)
        lang_family = lang.split('_')[0].lower()
        
        # Return the first available font for this language
        if lang_family in lang_fonts:
            for font_path in lang_fonts[lang_family]:
                if os.path.isfile(font_path):
                    logger.debug(f"Found language-specific font for {lang}: {font_path}")
                    return font_path
        
        # Default to None if no suitable font found
        return None

# Default instance for convenience
default_font_manager = FontManager()
