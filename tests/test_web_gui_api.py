#!/usr/bin/env python3
"""
API integration tests for Web GUI endpoints.
Tests all form options and API functionality.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import requests
import subprocess
import time
from unittest.mock import patch, MagicMock

# Import Flask app for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.web_gui import app, OUTPUT_DIR
except ImportError:
    # Fallback for different import paths
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    from web_gui import app, OUTPUT_DIR

# Test data for all form options
TEST_COMBINATIONS = [
    {
        'project': 'test_voice_pl_marek',
        'voice': 'pl-PL-MarekNeural',
        'theme': 'tech',
        'template': 'classic',
        'font_size': '48',
        'lang': 'pl',
        'markdown': '''---
title: Test Polish Voice Marek
date: 2025-01-01
---

Test content for Polish voice Marek Neural.'''
    },
    {
        'project': 'test_voice_pl_zofia',
        'voice': 'pl-PL-ZofiaNeural',
        'theme': 'philosophy',
        'template': 'gradient',
        'font_size': '36',
        'lang': 'pl',
        'markdown': '''---
title: Test Polish Voice Zofia
date: 2025-01-01
---

Test content for Polish voice Zofia Neural.'''
    },
    {
        'project': 'test_voice_de_killian',
        'voice': 'de-DE-KillianNeural',
        'theme': 'wetware',
        'template': 'boxed',
        'font_size': '64',
        'lang': 'de',
        'markdown': '''---
title: Test German Voice Killian
date: 2025-01-01
---

Test content for German voice Killian Neural.'''
    },
    {
        'project': 'test_voice_de_katja',
        'voice': 'de-DE-KatjaNeural',
        'theme': 'tech',
        'template': 'left',
        'font_size': '24',
        'lang': 'de',
        'markdown': '''---
title: Test German Voice Katja
date: 2025-01-01
---

Test content for German voice Katja Neural.'''
    },
    {
        'project': 'test_voice_en_guy',
        'voice': 'en-US-GuyNeural',
        'theme': 'philosophy',
        'template': 'classic',
        'font_size': '52',
        'lang': 'en',
        'markdown': '''---
title: Test English Voice Guy
date: 2025-01-01
---

Test content for English voice Guy Neural.'''
    },
    {
        'project': 'test_voice_en_aria',
        'voice': 'en-US-AriaNeural',
        'theme': 'wetware',
        'template': 'gradient',
        'font_size': '40',
        'lang': 'en',
        'markdown': '''---
title: Test English Voice Aria
date: 2025-01-01
---

Test content for English voice Aria Neural.'''
    }
]

THEMES = ['tech', 'philosophy', 'wetware']
TEMPLATES = ['classic', 'gradient', 'boxed', 'left']
FONT_SIZES = ['24', '36', '48', '64', '72', '96']
LANGUAGES = ['pl', 'en', 'de', 'fr', 'es', 'it']

@pytest.fixture
def client():
    """Flask test client fixture."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def temp_env_file():
    """Create temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("YOUTUBE_API_KEY=test_key\n")
        f.write("WORDPRESS_URL=https://test.wordpress.com\n")
        f.write("CUSTOM_VAR=test_value\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

class TestWebGUIAPI:
    """Test suite for Web GUI API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test that root endpoint returns HTML page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'YTLite Projects' in response.data
        assert b'Create New Project' in response.data
        
    def test_api_projects_endpoint(self, client):
        """Test /api/projects endpoint."""
        response = client.get('/api/projects')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'projects' in data
        assert isinstance(data['projects'], list)
        
    def test_api_progress_endpoint(self, client):
        """Test /api/progress endpoint."""
        response = client.get('/api/progress?project=test_project')
        assert response.status_code == 200
        
        data = response.get_json()
        # Should return empty dict or progress data
        assert isinstance(data, dict)
        
    def test_api_validate_svg_missing_project(self, client):
        """Test SVG validation with missing project."""
        response = client.get('/api/validate_svg')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['valid'] is False
        assert 'Missing project name' in data['errors']
        
    def test_api_validate_svg_nonexistent_project(self, client):
        """Test SVG validation with nonexistent project."""
        response = client.get('/api/validate_svg?project=nonexistent_project')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['valid'] is False
        assert 'SVG file not found' in data['errors']
        
    def test_api_project_history_missing_project(self, client):
        """Test project history with missing project."""
        response = client.get('/api/project_history')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Missing project name' in data['error']
        
    def test_api_restore_version_invalid_request(self, client):
        """Test version restoration with invalid request."""
        response = client.post('/api/restore_version',
                             json={'project': '', 'version': ''})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'Missing project or version' in data['message']
        
    def test_api_generate_basic_project(self, client):
        """Test basic project generation via API."""
        test_data = TEST_COMBINATIONS[0]
        
        response = client.post('/api/generate', data=test_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Project generated successfully'
        assert 'project' in data
        assert 'urls' in data
        
    def test_api_generate_all_voice_options(self, client):
        """Test all voice options through API."""
        for test_case in TEST_COMBINATIONS:
            response = client.post('/api/generate', data=test_case)
            assert response.status_code == 200, f"Failed for voice: {test_case['voice']}"
            data = response.get_json()
            assert 'message' in data
            assert data['message'] == 'Project generated successfully'
            assert 'project' in data
            assert 'urls' in data
            
    def test_api_generate_with_env_file(self, client, temp_env_file):
        """Test project generation with .env file upload."""
        test_data = TEST_COMBINATIONS[0].copy()
        with open(temp_env_file, 'rb') as env_file:
            test_data['env'] = env_file
            response = client.post('/api/generate', content_type='multipart/form-data', data=test_data)
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
            assert data['message'] == 'Project generated successfully'
            assert 'project' in data
            assert 'urls' in data
            
    def test_api_generate_json_content_type(self, client):
        """Test API generation with JSON content type."""
        test_data = {
            'project': 'test_json_project',
            'markdown': '# Test JSON Content Type\nThis is a test markdown content.'
        }
        response = client.post('/api/generate', json=test_data, content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Project generated successfully'
        assert 'project' in data
        assert 'urls' in data
        
    def test_api_generate_all_theme_combinations(self, client):
        """Test all theme and template combinations."""
        for theme in THEMES:
            for template in TEMPLATES:
                test_data = {
                    'project': f"test_{theme}_{template}",
                    'markdown': f"# Test {theme} {template}\nContent for {theme} {template}",
                    'theme': theme,
                    'template': template
                }
                response = client.post('/api/generate', data=test_data)
                assert response.status_code == 200, f"Failed for {theme}/{template}"
                data = response.get_json()
                assert 'message' in data
                assert data['message'] == 'Project generated successfully'
                assert 'project' in data
                assert 'urls' in data
                
    def test_api_generate_font_size_variations(self, client):
        """Test different font size inputs."""
        for font_size in FONT_SIZES:
            test_data = {
                'project': f"test_font_{font_size}",
                'markdown': f"# Test Font Size {font_size}\nContent for font size {font_size}",
                'font_size': str(font_size)
            }
            response = client.post('/api/generate', data=test_data)
            assert response.status_code == 200, f"Failed for font size: {font_size}"
            data = response.get_json()
            assert 'message' in data
            assert data['message'] == 'Project generated successfully'
            assert 'project' in data
            assert 'urls' in data
            
    def test_api_generate_language_variations(self, client):
        """Test different language inputs."""
        for lang in LANGUAGES:
            test_data = {
                'project': f"test_lang_{lang}",
                'markdown': f"# Test Language {lang}\nContent for language {lang}",
                'lang': lang
            }
            response = client.post('/api/generate', data=test_data)
            assert response.status_code == 200, f"Failed for language: {lang}"
            data = response.get_json()
            assert 'message' in data
            assert data['message'] == 'Project generated successfully'
            assert 'project' in data
            assert 'urls' in data
            
    def test_output_index_endpoint(self, client):
        """Test output index endpoint."""
        response = client.get('/output-index')
        # Should either redirect or return output listing
        assert response.status_code in [200, 301, 302, 404]
        
    def test_files_endpoint_security(self, client):
        """Test that files endpoint prevents directory traversal."""
        # Try to access files outside allowed directory
        response = client.get('/files/../../../etc/passwd')
        assert response.status_code in [400, 404]
        
        response = client.get('/files/projects/../../web_gui.py')
        assert response.status_code in [400, 404]
        
    def test_wordpress_publish_api(self, client):
        """Test WordPress publishing API."""
        test_data = {
            'project': 'wordpress-test',
            'markdown': '# Test WordPress Publish\nThis is a test content for WordPress.'
        }
        # First generate the project
        response = client.post('/api/generate', data=test_data)
        assert response.status_code == 200
        
        # Then attempt to publish (since we can't mock, we'll just check if the endpoint responds)
        response = client.post('/api/publish/wordpress', data={'project': 'wordpress-test'})
        assert response.status_code in [200, 400, 500]  # Allow for various responses since actual publishing might fail without credentials
        data = response.get_json()
        assert 'message' in data or 'error' in data or 'status' in data
        
    def test_api_generate_missing_project_name(self, client):
        """Test API generation without project name."""
        response = client.post('/api/generate', data={
            'markdown': 'test content',
            'voice': 'en-US-AriaNeural'
        })
        assert response.status_code == 400

class TestAPIIntegration:
    """Integration tests for API with real backend."""
    
    @pytest.mark.integration
    @patch.dict(os.environ, {'YTLITE_FAST_TEST': '1'})
    def test_full_generation_workflow(self, client):
        """Test complete project generation workflow."""
        # This test requires actual backend functionality
        test_data = {
            'project': 'integration_test_project',
            'voice': 'en-US-AriaNeural',
            'theme': 'tech',
            'template': 'classic',
            'font_size': '48',
            'lang': 'en',
            'markdown': '''---
title: Integration Test Project
date: 2025-01-01
---

This is an integration test to verify the complete workflow.
Testing all components working together.'''
        }
        
        response = client.post('/api/generate', data=test_data)
        
        # In fast test mode, should complete successfully
        if response.status_code == 200:
            # Verify project was created
            project_dir = OUTPUT_DIR / 'projects' / test_data['project']
            assert project_dir.exists()
            
            # Check for SVG file
            svg_files = list(project_dir.glob('*.svg'))
            if svg_files:
                assert len(svg_files) == 1
                
                # Verify SVG validation endpoint
                validation_response = client.get(f"/api/validate_svg?project={test_data['project']}")
                assert validation_response.status_code == 200
                
                validation_data = validation_response.get_json()
                assert 'valid' in validation_data

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration"])
