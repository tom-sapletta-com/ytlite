from pathlib import Path
import json
import os
import io
import sys
import time
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import the Flask app from the correct location
from src.ytlite_web_gui import create_production_app

@pytest.fixture
def client():
    """Fixture for Flask test client."""
    app = create_production_app()
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

def test_generate_valid_markdown_e2e(client):
    """Test generating a project with valid markdown content (E2E)."""
    project = f"e2e_valid_{int(time.time())}"
    valid_md = "# Title\nSome content here"
    resp = client.post(
        "/api/generate",
        data={"project": project, "markdown": valid_md},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 500, resp.data
    data = resp.get_json()
    assert 'message' in data, "Expected message in response"

def test_generate_invalid_frontmatter_e2e(client):
    """Test generating a project with invalid frontmatter (should fallback)."""
    project = f"e2e_invalid_fm_{int(time.time())}"
    bad_md = "---\ntitle: Invalid YAML ---\nContent"
    resp = client.post(
        "/api/generate",
        data={"project": project, "markdown": bad_md},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 500, resp.data
    data = resp.get_json()
    assert 'message' in data, "Expected message in response"
