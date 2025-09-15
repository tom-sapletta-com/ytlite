import pytest
import requests
import time
import json

@pytest.mark.api
def test_server_health(live_server: str):
    """Test that the server responds to health checks."""
    response = requests.get(f"{live_server}/health")
    assert response.status_code == 204

@pytest.mark.api
def test_projects_api(live_server: str):
    """Test the projects API endpoint."""
    response = requests.get(f"{live_server}/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert isinstance(data["projects"], list)

@pytest.mark.api
def test_create_project_api(live_server: str):
    """Test creating a project via API."""
    project_name = f"api_test_{int(time.time())}"
    
    data = {
        'project': project_name,
        'markdown': '# API Test\n\nThis is a test project created via API.',
        'theme': 'tech',
        'voice': 'en-US-AriaNeural'
    }
    
    response = requests.post(f"{live_server}/api/generate", data=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert project_name in result["message"]

@pytest.mark.api
def test_project_metadata_api(live_server: str):
    """Test retrieving project metadata via API."""
    # First create a project
    project_name = f"meta_test_{int(time.time())}"
    
    data = {
        'project': project_name,
        'markdown': '# Metadata Test\n\nTesting metadata retrieval.',
        'theme': 'philosophy',
        'voice': 'pl-PL-MarekNeural'
    }
    
    create_response = requests.post(f"{live_server}/api/generate", data=data)
    assert create_response.status_code == 200
    
    # Wait a moment for project to be created
    time.sleep(2)
    
    # Try to get metadata
    meta_response = requests.get(f"{live_server}/api/svg_meta", params={'project': project_name})
    
    # The response might be 404 if SVG isn't created yet, which is acceptable
    assert meta_response.status_code in [200, 404]
    
    if meta_response.status_code == 200:
        metadata = meta_response.json()
        assert isinstance(metadata, dict)

@pytest.mark.api
def test_invalid_project_creation(live_server: str):
    """Test that invalid project data returns appropriate errors."""
    # Test with empty project name
    data = {
        'project': '',
        'markdown': 'Some content'
    }
    
    response = requests.post(f"{live_server}/api/generate", data=data)
    # Should return an error status
    assert response.status_code >= 400
    
    # Test with empty content
    data = {
        'project': 'valid-name',
        'markdown': ''
    }
    
    response = requests.post(f"{live_server}/api/generate", data=data)
    # Should return an error status
    assert response.status_code >= 400
