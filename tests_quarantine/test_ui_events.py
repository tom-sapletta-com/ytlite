#!/usr/bin/env python3
import sys
from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ytlite_web_gui import create_production_app

@pytest.fixture
def app():
    app = create_production_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c

def test_ui_event_endpoint_ok(client):
    resp = client.post('/api/ui_event', json={"action": "pytest_action", "context": {"k": "v"}})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('ok') is True

def test_index_includes_actions_and_projects_modules(client):
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Ensure our modular JS is referenced
    assert '/assets/js/actions.js' in html
    assert '/assets/js/projects-grid.js' in html
    assert '/assets/js/projects-table.js' in html

