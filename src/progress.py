#!/usr/bin/env python3
"""
Progress reporter utilities for per-project progress feedback.
Writes JSON snapshots to output/projects/<project>/progress.json and appends to progress.log.jsonl.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

class ProgressReporter:
    def __init__(self, project: str, output_root: Path):
        self.project = project
        self.project_dir = output_root / "projects" / project
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_path = self.project_dir / "progress.json"
        self.log_path = self.project_dir / "progress.log.jsonl"
        self.started_at = time.time()
        self.update("init", "Starting", 0)

    def update(self, step: str, message: str, percent: int, extra: Optional[dict] = None):
        ts = int(time.time())
        data = {
            "project": self.project,
            "step": step,
            "message": message,
            "percent": int(percent),
            "ts": ts,
            "elapsed": int(ts - self.started_at),
        }
        if extra:
            data.update(extra)
        # Write snapshot
        self.snapshot_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # Append log line
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def done(self, message: str = "Done"):
        self.update("done", message, 100)


def load_progress(project: str, output_root: Path) -> Optional[dict]:
    p = output_root / "projects" / project / "progress.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None
