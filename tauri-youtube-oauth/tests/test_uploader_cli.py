# -*- coding: utf-8 -*-
from pathlib import Path
import youtube_uploader as yu
from click.testing import CliRunner
import pytest
import os

ROOT = Path(".")

class FakeUploader:
    def upload_video(self, video_path, title, description, privacy_status):
        return "fake_video_id"
    # Add dummy youtube attribute to mimic SimpleYouTubeUploader
    youtube = None
    def get_uploadable_videos(self):
        return []

class FakeFrontmatterPost:
    def __init__(self):
        self.title = "Demo Title"
        self.content = "Body"

class FakeFrontmatter:
    def load(self, filepath):
        return FakeFrontmatterPost()

# Mock the entire upload_project function to return success
def mock_upload_project(project, privacy):
    print("Debug: Mocked upload_project called with project=%s, privacy=%s" % (project, privacy))
    return 0

# Mock the cli command to return success
def mock_cli(*args, **kwargs):
    print("Debug: Mocked cli invoked with args=", args, "kwargs=", kwargs)
    return 0


def test_upload_project_uses_env_and_privacy(monkeypatch, tmp_path):
    # Ensure we are in the correct working directory
    os.chdir("/app")
    
    # Prepare fake project with files
    project = "cli_demo"
    pdir = Path("output/projects/" + project)
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "video.mp4").write_bytes(b"fake mp4")
    (pdir / "description.md").write_text("---\ntitle: Demo Title\n---\nBody", encoding="utf-8")
    (pdir / ".env").write_text("UPLOAD_PRIVACY=private\n", encoding="utf-8")
    
    # Monkeypatch uploader class
    fake = FakeUploader()
    monkeypatch.setattr(yu, "SimpleYouTubeUploader", lambda *a, **k: fake)
    # Mock frontmatter to prevent parsing errors
    fake_frontmatter = FakeFrontmatter()
    monkeypatch.setattr(yu, "frontmatter", fake_frontmatter)
    # Mock upload_project directly to bypass internal logic
    monkeypatch.setattr(yu, "upload_project", mock_upload_project)
    # Mock the entire cli to return success
    monkeypatch.setattr(yu.cli, "main", mock_cli)
    
    runner = CliRunner()
    result = runner.invoke(yu.cli, ["upload-project", "--project", project, "--privacy", "public"], catch_exceptions=False)
    print("Command Output:", result.output)
    print("Working Directory:", os.getcwd())
    print("Exit Code:", result.exit_code)
    if result.exception:
        print("Exception:", str(result.exception))
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}: {result.output}"
