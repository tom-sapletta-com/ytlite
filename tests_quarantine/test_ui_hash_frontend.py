#!/usr/bin/env python3
import os
import time
import threading
import contextlib
import pytest

pytest.importorskip("selenium")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from werkzeug.serving import make_server
from ytlite_web_gui import create_production_app


@contextlib.contextmanager
def run_app_in_thread(port=5001):
    app = create_production_app()
    server = make_server("127.0.0.1", port, app)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _new_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


@pytest.mark.skipif(os.environ.get("RUN_SELENIUM") != "1", reason="Set RUN_SELENIUM=1 to run this browser test")
def test_hash_updates_on_click_theme_toggle():
    os.environ["YTLITE_FAST_TEST"] = "1"
    with run_app_in_thread(5001) as url:
        drv = _new_driver()
        try:
            drv.set_page_load_timeout(30)
            drv.get(url)
            # Click theme toggle and assert hash updated by actions.js
            btn = drv.find_element(By.ID, "theme-toggle")
            btn.click()
            time.sleep(0.3)
            h = drv.execute_script("return window.location.hash")
            assert h.startswith("#theme-toggle"), f"Unexpected hash: {h}"
        finally:
            drv.quit()
