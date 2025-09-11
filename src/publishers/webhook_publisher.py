#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

console = Console()


class WebhookPublisher:
    """
    Minimal webhook publisher that POSTs project metadata and links/media to a configured URL.
    Configure via env or parameters:
    - WEBHOOK_URL (required)
    Optional headers: WEBHOOK_AUTH (e.g., Bearer token)
    """

    def __init__(self, url: Optional[str] = None, auth: Optional[str] = None):
        self.url = url or os.getenv("WEBHOOK_URL", "").strip()
        self.auth = auth or os.getenv("WEBHOOK_AUTH", "").strip()
        if not self.url:
            console.print("[yellow]Webhook URL not configured[/]")

    def publish_project(self, project_dir: str, publish_status: str = "draft") -> Optional[dict]:
        p = Path(project_dir)
        if not p.exists():
            return None
        payload = {
            "project": p.name,
            "status": publish_status,
            "files": {
                "video": f"{p / 'video.mp4'}",
                "audio": f"{p / 'audio.mp3'}",
                "thumbnail": f"{p / 'thumbnail.jpg'}",
                "description": f"{p / 'description.md'}",
                "svg": next((str(x) for x in p.glob('*.svg')), None),
            },
        }
        headers = {"Content-Type": "application/json"}
        if self.auth:
            headers["Authorization"] = self.auth
        try:
            r = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            if r.status_code not in (200, 201, 202):
                console.print(f"[yellow]Webhook publish failed: {r.status_code} {r.text[:200]}")
                return None
            return r.json() if 'application/json' in (r.headers.get('Content-Type') or '') else {"status": r.status_code}
        except Exception as e:
            console.print(f"[yellow]Webhook error: {e}")
            return None
