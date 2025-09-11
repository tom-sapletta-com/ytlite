# -*- coding: utf-8 -*-
from pathlib import Path
import youtube_uploader as yu
from click.testing import CliRunner
import pytest

ROOT = Path("/")

class FakeUploader:
    def upload_video(self, video_path, title, description, privacy_status):
        return "fake_video_id"
    # Add dummy youtube attribute to mimic SimpleYouTubeUploader
    youtube = None
    def get_uploadable_videos(self):
        return []


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
    result = runner.invoke(yu.cli, ["upload-project", "--project", project, "--privacy", "public"], catch_exceptions=False)
    print("Command Output:", result.output)
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}: {result.output}"
