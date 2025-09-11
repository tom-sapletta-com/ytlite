from pathlib import Path
import sys
from click.testing import CliRunner

# Add src to path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import web_gui  # type: ignore


class FakePublisher:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def publish_project(self, project_dir: str, publish_status: str = "draft"):
        # emulate minimal successful response from WP
        return {"id": 123, "link": "https://example.com/?p=123"}


def test_publish_wordpress_endpoint(monkeypatch):
    # prepare project dir with required files
    project = "e2e_wp"
    pdir = ROOT / "output" / "projects" / project
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "description.md").write_text("---\ntitle: Post\n---\nBody", encoding="utf-8")
    (pdir / "thumbnail.jpg").write_bytes(b"fakejpg")
    (pdir / "video.mp4").write_bytes(b"fakemp4")
    (pdir / "audio.mp3").write_bytes(b"fakemp3")

    # monkeypatch publisher
    monkeypatch.setattr(web_gui, "WordPressPublisher", FakePublisher)

    app = web_gui.app
    app.testing = True
    client = app.test_client()

    res = client.post(
        "/api/publish_wordpress",
        json={"project": project, "base_url": "https://example.com", "username": "u", "app_password": "p"},
    )
    assert res.status_code == 200, res.data
    data = res.get_json()
    assert data.get("id") == 123
    assert "link" in data
