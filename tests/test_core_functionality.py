#!/usr/bin/env python3
"""Core functionality tests that work without complex fixtures."""
import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def test_ytlite_initialization():
    """Test YTLite class initialization with config overrides."""
    from ytlite_main import YTLite
    
    # Test basic initialization
    ytlite = YTLite()
    assert ytlite is not None
    assert hasattr(ytlite, 'config')
    
    # Test with overrides (the key functionality we fixed)
    overrides = {
        'theme': 'philosophy',
        'voice': 'pl-PL-MarekNeural',
        'font_size': 'large'
    }
    
    ytlite_with_overrides = YTLite(config_overrides=overrides)
    assert ytlite_with_overrides.config['theme'] == 'philosophy'
    assert ytlite_with_overrides.config['voice'] == 'pl-PL-MarekNeural'
    assert ytlite_with_overrides.config['font_size'] == 'large'

def test_web_gui_creation():
    """Test Flask app creation."""
    from web_gui import create_app
    
    app = create_app()
    assert app is not None
    
    # Test with config overrides
    config_overrides = {'TESTING': True}
    test_app = create_app(config_overrides)
    assert test_app.config['TESTING'] is True

def test_content_parser():
    """Test markdown content parsing."""
    from content_parser import ContentParser
    
    parser = ContentParser()
    
    test_markdown = """---
title: Test Project
theme: tech
voice: en-US-AriaNeural
---

# Main Title

This is the first paragraph with **bold** text.

## Subtitle

Second paragraph with *italic* text.
"""
    
    metadata, paragraphs = parser.parse_content(test_markdown)
    
    # Verify metadata extraction
    assert metadata['title'] == 'Test Project'
    assert metadata['theme'] == 'tech'
    assert metadata['voice'] == 'en-US-AriaNeural'
    
    # Verify content parsing
    assert len(paragraphs) >= 2
    assert 'Main Title' in paragraphs[0]
    assert 'first paragraph' in paragraphs[0]

def test_svg_packager_functions():
    """Test SVG packager utility functions."""
    from svg_packager import parse_svg_meta
    
    # Test that function exists and is callable
    assert callable(parse_svg_meta)
    
    # Test with None (should return None gracefully)
    result = parse_svg_meta(Path('/nonexistent/file.svg'))
    assert result is None

def test_web_gui_helpers():
    """Test web GUI helper functions."""
    from web_gui.helpers import generate_media_for_project
    
    # Test that function exists
    assert callable(generate_media_for_project)

def test_routes_import():
    """Test that routes can be imported without errors."""
    from web_gui.routes import setup_routes
    assert callable(setup_routes)

if __name__ == '__main__':
    # Run tests directly if executed as script
    import traceback
    
    tests = [
        test_ytlite_initialization,
        test_web_gui_creation,
        test_content_parser,
        test_svg_packager_functions,
        test_web_gui_helpers,
        test_routes_import
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
