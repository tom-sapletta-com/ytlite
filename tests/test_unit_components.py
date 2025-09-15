#!/usr/bin/env python3
"""Unit tests for individual YTLite components."""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def test_web_gui_import():
    """Test that web_gui module can be imported."""
    from web_gui import create_app
    assert create_app is not None

def test_create_app_basic():
    """Test that create_app returns a Flask application."""
    from web_gui import create_app
    app = create_app()
    assert app is not None
    assert hasattr(app, 'run')

def test_ytlite_main_import():
    """Test that YTLite main class can be imported."""
    from ytlite_main import YTLite
    assert YTLite is not None

def test_ytlite_config_overrides():
    """Test YTLite configuration override functionality."""
    from ytlite_main import YTLite
    
    # Test with config overrides
    overrides = {
        'theme': 'test_theme',
        'voice': 'test_voice'
    }
    
    # This should not fail during initialization
    ytlite = YTLite(config_overrides=overrides)
    assert ytlite.config['theme'] == 'test_theme'
    assert ytlite.config['voice'] == 'test_voice'

def test_svg_packager_import():
    """Test that SVG packager can be imported."""
    from svg_packager import parse_svg_meta, build_svg
    assert parse_svg_meta is not None
    assert build_svg is not None

def test_helpers_import():
    """Test that web GUI helpers can be imported."""
    from web_gui.helpers import generate_media_for_project
    assert generate_media_for_project is not None

def test_routes_setup():
    """Test that routes can be set up without errors."""
    from web_gui import create_app
    from web_gui.routes import setup_routes
    
    app = create_app()
    
    # This should complete without errors
    with app.app_context():
        base_dir = Path(__file__).parent.parent
        output_dir = base_dir / 'tests' / 'output'
        output_dir.mkdir(exist_ok=True)
        
        setup_routes(app, base_dir, output_dir)
    
    # Check that some expected routes exist
    route_names = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert 'api_projects' in route_names
    assert 'api_generate' in route_names

def test_content_parser():
    """Test content parser functionality."""
    from content_parser import ContentParser
    
    parser = ContentParser()
    
    # Test basic markdown parsing
    test_content = """---
title: Test Project
theme: tech
---

# Test Title

This is test content."""
    
    metadata, paragraphs = parser.parse_content(test_content)
    
    assert metadata['title'] == 'Test Project'
    assert metadata['theme'] == 'tech'
    assert len(paragraphs) > 0
    assert 'Test Title' in paragraphs[0]

def test_audio_generator_import():
    """Test that audio generator can be imported."""
    from audio_generator import AudioGenerator
    assert AudioGenerator is not None

def test_video_generator_import():
    """Test that video generator can be imported."""
    from video_generator import VideoGenerator
    assert VideoGenerator is not None
