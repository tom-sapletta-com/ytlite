#!/usr/bin/env python3
"""
Minimal Nextcloud storage integration using WebDAV (remote.php/dav/files/...)
Supports downloading a remote file into local workspace using Basic Auth.

Per-project credentials can be provided via .env (loaded beforehand):
- NEXTCLOUD_URL (e.g., https://cloud.example.com)
- NEXTCLOUD_USERNAME
- NEXTCLOUD_PASSWORD (App Password recommended)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import os
import requests
from rich.console import Console

console = Console()

class NextcloudClient:
    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = (base_url or os.getenv("NEXTCLOUD_URL", "")).rstrip("/")
        self.username = username or os.getenv("NEXTCLOUD_USERNAME", "")
        self.password = password or os.getenv("NEXTCLOUD_PASSWORD", "")
        if not (self.base_url and self.username and self.password):
            console.print("[yellow]Nextcloud credentials not fully configured[/]")

    def file_url(self, remote_path: str) -> str:
        remote_path = remote_path.lstrip("/")
        return f"{self.base_url}/remote.php/dav/files/{self.username}/{remote_path}"

    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            url = self.file_url(remote_path)
            r = requests.get(url, auth=(self.username, self.password), stream=True, timeout=120)
            if r.status_code != 200:
                console.print(f"[yellow]Nextcloud download failed: {r.status_code} {r.text[:200]}[/]")
                return False
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            console.print(f"[green]✓ Downloaded from Nextcloud: {remote_path} -> {local_path}[/]")
            return True
        except Exception as e:
            console.print(f"[yellow]Nextcloud error: {e}[/]")
            return False
