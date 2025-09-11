import os
from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def fast_test_env(monkeypatch, tmp_path):
    # Enable fast test mode
    monkeypatch.setenv("YTLITE_FAST_TEST", "1")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    # Ensure MoviePy uses bundled ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        monkeypatch.setenv("IMAGEIO_FFMPEG_EXE", ffmpeg)
    except Exception:
        pass
    # Ensure output and content directories exist per test run
    base_dir = Path(__file__).resolve().parents[1]
    (base_dir / "output").mkdir(exist_ok=True)
    (base_dir / "content" / "episodes").mkdir(parents=True, exist_ok=True)
    yield
    # Do not clean output to allow debugging artifacts; could be toggled via env
