from pathlib import Path
import sys

# Add src to path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import web_gui  # type: ignore


class FakeNC:
    def __init__(self, *args, **kwargs) -> None:
        pass
    def download_file(self, remote_path: str, local_path: str) -> bool:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        Path(local_path).write_text("# downloaded from fake nextcloud", encoding="utf-8")
        return True


def test_fetch_nextcloud(monkeypatch, tmp_path):
    monkeypatch.setattr(web_gui, "NextcloudClient", FakeNC)
    app = web_gui.app
    app.testing = True
    client = app.test_client()

    res = client.post(
        "/api/fetch_nextcloud",
        json={"remote_path": "/dir/sample.md"},
    )
    assert res.status_code == 200, res.data
    data = res.get_json()
    local = data.get("local_path")
    assert local
    lp = ROOT / local
    assert lp.exists()
    assert lp.read_text(encoding="utf-8").startswith("# downloaded")
