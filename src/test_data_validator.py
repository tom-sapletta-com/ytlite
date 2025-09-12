#!/usr/bin/env python3
"""
YTLite Test Data Validator Module
Tests project folders, media, and SVG files for errors and optionally removes faulty files
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime
import logging
import shutil

console = Console()
logger = logging.getLogger(__name__)

try:
    import whisper
except ImportError:
    console.print("[yellow]Whisper not installed. Attempting to install...[/]")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
        import whisper
    except Exception as install_error:
        console.print(f"[bold red]Failed to install Whisper: {install_error}[/]")
        logger.error(f"Failed to install Whisper", extra={"error": str(install_error)})

try:
    # MoviePy 1.x path
    from moviepy.editor import VideoFileClip
except Exception:
    try:
        # MoviePy 2.x path
        from moviepy import VideoFileClip
    except Exception as e:
        console.print("[yellow]MoviePy not found. Attempting to install...[/]")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy==1.0.3"])
            from moviepy.editor import VideoFileClip
        except Exception as inner_e:
            console.print(f"[bold red]MoviePy import failed after install: {inner_e}[/]")
            logger.error(f"MoviePy import failed after install", extra={"error": str(inner_e)})
            raise

class TestDataValidator:
    def __init__(self, remove_faulty: bool = False):
        self.remove_faulty = remove_faulty
        self.results = {}
        
    def test_data(self) -> dict:
        """Test all data in project folders"""
        results = {}
        project_dir = Path("output/projects")
        project_dir.mkdir(exist_ok=True, parents=True)
        for project_folder in project_dir.glob("*"):
            if project_folder.is_dir():
                results[project_folder.name] = self.test_project(project_folder)
        with open("output/test_data_report.json", "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"[bold green]✓ Report saved to output/test_data_report.json[/]")
        logger.info("Test data report saved", extra={"report_path": "output/test_data_report.json"})
        return results

    def test_project(self, project_path: Path) -> dict:
        """Test a single project's files"""
        result = {
            "status": "Valid",
            "media_files": {},
            "svg_files": {},
            "errors": []
        }
        # Test media files
        media_dir = project_path / "media"
        if media_dir.exists():
            for media_file in media_dir.glob("*"):
                if media_file.is_file():
                    media_result = self.test_media_file(media_file)
                    result["media_files"][media_file.name] = media_result
                    if media_result["status"] == "Error":
                        result["status"] = "Error"
                        result["errors"].append(f"Media file {media_file.name}: {media_result['error']}")
                        if self.remove_faulty:
                            media_file.unlink()
                            console.print(f"[red]Removed faulty media file: {media_file}[/]")
                            logger.info(f"Removed faulty media file", extra={"file": str(media_file)})
        # Test SVG files
        svg_dir = project_path / "versions"
        if svg_dir.exists():
            for svg_file in svg_dir.glob("*.svg"):
                if svg_file.is_file():
                    svg_result = self.test_svg_file(svg_file)
                    result["svg_files"][svg_file.name] = svg_result
                    if svg_result["status"] == "Error":
                        result["status"] = "Error"
                        result["errors"].append(f"SVG file {svg_file.name}: {svg_result['error']}")
                        if self.remove_faulty:
                            svg_file.unlink()
                            console.print(f"[red]Removed faulty SVG file: {svg_file}[/]")
                            logger.info(f"Removed faulty SVG file", extra={"file": str(svg_file)})
        return result

    def test_media_file(self, media_path: Path) -> dict:
        """Test a single media file"""
        result = {
            "status": "Valid",
            "error": ""
        }
        try:
            if media_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
                video = VideoFileClip(str(media_path))
                result["duration"] = video.duration
                video.close()
                logger.info(f"Validated media file: {media_path}", extra={"status": "Valid", "duration": video.duration})
            elif media_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                try:
                    from PIL import Image
                    img = Image.open(media_path)
                    img.close()
                    logger.info(f"Validated media file: {media_path}", extra={"status": "Valid"})
                except ImportError:
                    console.print("[yellow]PIL not installed. Installing...[/]")
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
                    from PIL import Image
                    img = Image.open(media_path)
                    img.close()
                    logger.info(f"Validated media file: {media_path}", extra={"status": "Valid"})
        except Exception as e:
            result["status"] = "Error"
            result["error"] = str(e)
            logger.error(f"Error validating media file {media_path}", extra={"error": str(e)})
        return result

    def test_svg_file(self, svg_path: Path) -> dict:
        """Test a single SVG file"""
        result = {
            "status": "Valid",
            "error": ""
        }
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(svg_path)
            root = tree.getroot()
            logger.info(f"Validated SVG file: {svg_path}", extra={"status": "Valid"})
        except ImportError as e:
            console.print("[yellow]xml.etree.ElementTree not found. Installing...[/]")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml"])
            import xml.etree.ElementTree as ET
            tree = ET.parse(svg_path)
            root = tree.getroot()
            logger.info(f"Validated SVG file: {svg_path}", extra={"status": "Valid"})
        except Exception as e:
            result["status"] = "Error"
            result["error"] = str(e)
            logger.error(f"Error validating SVG file {svg_path}", extra={"error": str(e)})
        return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test project data for errors')
    parser.add_argument('command', choices=['test_data'], help='Command to execute')
    parser.add_argument('--remove-faulty', action='store_true', help='Remove faulty files')
    args = parser.parse_args()
    validator = TestDataValidator(remove_faulty=args.remove_faulty)
    if args.command == 'test_data':
        validator.test_data()

if __name__ == "__main__":
    main()
