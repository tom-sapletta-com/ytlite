#!/usr/bin/env python3
"""
YTLite Data Validator
Scans output/projects/ for per-project integrity and reports missing files.
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.table import Table

REQUIRED_FILES = [
    "video.mp4",
    "audio.mp3",
    "thumbnail.jpg",
    "description.md",
    "index.md",
]

console = Console()

def scan_projects(projects_root: str = "output/projects") -> List[Dict]:
    root = Path(projects_root)
    projects = []
    if not root.exists():
        return projects
    for p in sorted(root.glob("*/")):
        item = {
            "name": p.name,
            "path": str(p),
            "files": {},
            "missing": [],
        }
        for fname in REQUIRED_FILES:
            fpath = p / fname
            exists = fpath.exists()
            item["files"][fname] = exists
            if not exists:
                item["missing"].append(fname)
        projects.append(item)
    return projects

def validate_projects(projects_root: str = "output/projects", report_path: str | None = None) -> Dict:
    projects = scan_projects(projects_root)
    total = len(projects)
    missing_any = [p for p in projects if p["missing"]]
    ok = total - len(missing_any)
    report = {
        "projects_root": projects_root,
        "total_projects": total,
        "ok": ok,
        "with_issues": len(missing_any),
        "projects": projects,
    }
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
    return report

def write_per_project_reports(report: Dict):
    """Write per-project JSON and Markdown reports into each project folder."""
    for p in report.get("projects", []):
        proj_dir = Path(p["path"])
        try:
            # JSON report
            with open(proj_dir / "data_report.json", "w") as f:
                json.dump(p, f, indent=2)
            # Markdown summary
            missing = p.get("missing", [])
            status = "OK" if not missing else "MISSING: " + ", ".join(missing)
            md = [
                f"# Data Report: {p['name']}",
                "",
                f"Status: {status}",
                "",
                "## Files",
            ]
            for fname, exists in p.get("files", {}).items():
                md.append(f"- {fname}: {'✓' if exists else '✗'}")
            (proj_dir / "data_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        except Exception:
            pass

def print_summary(report: Dict):
    table = Table(title="Data Validation - Projects")
    table.add_column("Project", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Missing", style="yellow")
    for p in report["projects"]:
        status = "OK" if not p["missing"] else "MISSING"
        missing_list = ", ".join(p["missing"]) if p["missing"] else "-"
        table.add_row(p["name"], status, missing_list)
    console.print(table)
    console.print(
        f"[bold]Summary:[/] total={report['total_projects']} ok={report['ok']} with_issues={report['with_issues']}"
    )

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate per-project generated data")
    parser.add_argument("--projects-root", default="output/projects")
    parser.add_argument("--report", default="output/validate_data.json")
    parser.add_argument("--write-per-project", action="store_true", help="Write per-project reports inside each project folder")
    args = parser.parse_args()
    report = validate_projects(args.projects_root, args.report)
    if args.write_per_project:
        write_per_project_reports(report)
    print_summary(report)
    # Exit code non-zero if any issues
    if report["with_issues"] > 0:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
