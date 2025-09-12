from pathlib import Path
import json
import os
import io
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import the Flask app from the correct location
from src.ytlite_web_gui import create_production_app

# Create the app instance for testing
app = create_production_app()


def _client():
    app.testing = True
    return app.test_client()


def test_generate_valid_markdown_e2e(tmp_path):
    client = _client()
    project = "e2e_valid"
    md = "Pierwszy akapit testu E2E"
    resp = client.post(
        "/api/generate",
        data={"project": project, "markdown": md},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data["project"] == project
    # Files exist
    root = Path(__file__).resolve().parents[1]
    pdir = root / "output" / "projects" / project
    assert (pdir / "video.mp4").exists()
    assert (pdir / "audio.mp3").exists()
    assert (pdir / "thumbnail.jpg").exists()
    assert any(pdir.glob('*.svg'))
    # Files served
    vresp = client.get(data["urls"]["video"])  # /files/projects/<proj>/video.mp4
    assert vresp.status_code in (200, 206)
    tresp = client.get(data["urls"]["thumb"])  # /files/projects/<proj>/thumbnail.jpg
    assert tresp.status_code == 200


def test_generate_invalid_frontmatter_e2e(tmp_path):
    client = _client()
    project = "e2e_badfm"
    bad_md = """---
this: is: not: valid: yaml: [
---
Treść po złym froncie
"""
    # Send as-is (starts with '---') to trigger frontmatter parse path
    resp = client.post(
        "/api/generate",
        data={"project": project, "markdown": bad_md},
        content_type="multipart/form-data",
    )
    # Should not crash; fallback should engage
    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data["project"] == project
    root = Path(__file__).resolve().parents[1]
    pdir = root / "output" / "projects" / project
    assert (pdir / "video.mp4").exists()
    assert (pdir / "thumbnail.jpg").exists()
    assert any(pdir.glob('*.svg'))
    # Access project index via files route
    iresp = client.get(data["urls"]["index"])
    assert iresp.status_code == 200
