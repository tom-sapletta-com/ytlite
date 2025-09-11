from pathlib import Path
import sys
from click.testing import CliRunner

# Add src to path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import youtube_uploader as yu  # type: ignore


class FakeUploader:
    def __init__(self, *args, **kwargs):
        self.youtube = True
        self.last = {}

    def upload_video(self, video, title, description="", tags=None, privacy=None):
        # Record call for assertions in tests
        self.last = {
            "video": str(video),
            "title": title,
            "description": description,
            "tags": tags or [],
            "privacy": privacy,
        }
        return "https://youtu.be/fake123"


def test_upload_project_uses_env_and_privacy(monkeypatch, tmp_path):
    # Prepare fake project with files
    project = "cli_demo"
    pdir = ROOT / "output" / "projects" / project
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "video.mp4").write_bytes(b"fake mp4")
    (pdir / "description.md").write_text("---\ntitle: Demo Title\n---\nBody", encoding="utf-8")
    (pdir / ".env").write_text("UPLOAD_PRIVACY=private\n", encoding="utf-8")

    # Monkeypatch uploader class
    fake = FakeUploader()
    monkeypatch.setattr(yu, "SimpleYouTubeUploader", lambda *a, **k: fake)

    runner = CliRunner()
    result = runner.invoke(yu.cli, ["upload-project", "--project", project, "--privacy", "public"])
    assert result.exit_code == 0, result.output
    # The fake captured call arguments
    assert fake.last["video"].endswith("/video.mp4")
    assert fake.last["title"] == "Demo Title"
    assert fake.last["privacy"] == "public"
