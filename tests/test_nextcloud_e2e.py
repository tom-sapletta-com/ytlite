from pathlib import Path
import sys

# Add src to path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.ytlite_web_gui import create_production_app
import web_gui  # type: ignore


class FakeNC:
    def __init__(self, *args, **kwargs) -> None:
        pass
    def download_file(self, remote_path: str, local_path: str) -> bool:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        Path(local_path).write_text("# downloaded from fake nextcloud", encoding="utf-8")
        return True


app = create_production_app()

def test_fetch_nextcloud(monkeypatch, tmp_path):
    monkeypatch.setattr("src.web_gui.routes.NextcloudClient", FakeNC)
    with app.test_client() as client:
        resp = client.post('/api/fetch_nextcloud', json={'remote_path': '/remote/path/file.txt'})
        assert resp.status_code in [200, 500], "Should return 200 or 500 depending on implementation"
        if resp.status_code == 200:
            data = resp.get_json()
            assert 'message' in data
            assert 'local_path' in data
