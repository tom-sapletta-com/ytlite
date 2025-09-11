"""
Module for managing fonts in ytlite to support multiple languages.
Matches fonts to languages for proper character rendering, supports UTF-8.
"""

import os

class FontManager:
    def __init__(self, fonts_dir):
        self.fonts_dir = fonts_dir
        os.makedirs(fonts_dir, exist_ok=True)
        self.fonts = {
            'Arial': {'path': os.path.join(fonts_dir, 'Arial.ttf'), 'languages': ['en', 'pl', 'de'], 'description': 'Arial - Supports Latin characters'},
            'NotoSans': {'path': os.path.join(fonts_dir, 'NotoSans-Regular.ttf'), 'languages': ['en', 'pl', 'de', 'zh', 'ja', 'ko'], 'description': 'Noto Sans - Broad language support including Asian scripts'},
            'NotoSerif': {'path': os.path.join(fonts_dir, 'NotoSerif-Regular.ttf'), 'languages': ['en', 'pl', 'de', 'zh', 'ja', 'ko'], 'description': 'Noto Serif - Broad language support with serif style'},
            # Add more fonts as needed
        }
        self.language_font_map = self._build_language_font_map()

    def _build_language_font_map(self):
        """Build a mapping of languages to preferred fonts."""
        language_font_map = {}
        for font, details in self.fonts.items():
            for lang in details['languages']:
                if lang not in language_font_map:
                    language_font_map[lang] = font
        return language_font_map

    def get_font_for_language(self, language_code):
        """Get the appropriate font for a given language code."""
        # Extract the base language code (e.g., 'en' from 'en-US')
        base_lang = language_code.split('-')[0] if '-' in language_code else language_code
        return self.language_font_map.get(base_lang, 'Arial')  # Default to Arial if language not found

    def get_font_path(self, font_name):
        """Get the file path for a given font."""
        return self.fonts.get(font_name, self.fonts['Arial'])['path']

    def get_available_fonts(self):
        """Return the list of available fonts with their details."""
        return self.fonts

if __name__ == "__main__":
    fm = FontManager('/home/tom/github/tom-sapletta-com/ytlite/fonts')
    print("Available fonts:", fm.get_available_fonts())
    print("Font for Polish (pl):", fm.get_font_for_language('pl'))
    print("Font for Chinese (zh-CN):", fm.get_font_for_language('zh-CN'))
    print("Font path for Arial:", fm.get_font_path('Arial'))
