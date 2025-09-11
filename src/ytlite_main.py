#!/usr/bin/env python3
"""
YTLite - Main Entry Point
Refactored to use modular components
"""

import os
import sys
from pathlib import Path
import click
import yaml
from rich.console import Console
from dotenv import load_dotenv

# Import our modules
from dependencies import verify_dependencies
from content_parser import ContentParser
from audio_generator import AudioGenerator
from video_generator import VideoGenerator

# Load environment variables
load_dotenv()

console = Console()

class YTLite:
    """Main YTLite orchestrator using modular components"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.content_parser = ContentParser()
        self.audio_generator = AudioGenerator(self.config)
        self.video_generator = VideoGenerator(self.config)
        
        # Setup output directories
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "shorts").mkdir(exist_ok=True)
        (self.output_dir / "thumbnails").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            console.print(f"[yellow]Config file {config_path} not found. Using defaults.[/]")
            return {
                "voice": "pl-PL-MarekNeural",
                "resolution": [1280, 720],
                "fps": 30,
                "font_size": 48,
                "themes": {
                    "tech": {
                        "bg_color": "#1e1e2e",
                        "text_color": "#cdd6f4"
                    }
                }
            }
    
    def generate_video(self, markdown_path: str):
        """Generate video from markdown file"""
        console.print(f"[bold cyan]Processing: {markdown_path}[/bold cyan]")
        try:
            console.print("Step 1: Parsing content...")
            metadata, paragraphs = self.content_parser.parse_markdown(markdown_path)
            console.print("Step 1: Done.")

            console.print("Step 2: Preparing output paths...")
            base_name = Path(markdown_path).stem
            audio_path = self.output_dir / "audio" / f"{base_name}.mp3"
            video_path = self.output_dir / "videos" / f"{base_name}.mp4"
            console.print(f"Audio path: {audio_path}")
            console.print(f"Video path: {video_path}")
            console.print("Step 2: Done.")

            console.print("Step 3: Generating audio...")
            combined_text = self.audio_generator.combine_text_for_audio(paragraphs)
            self.audio_generator.generate_audio(combined_text, str(audio_path))
            console.print("Step 3: Done.")

            console.print("Step 4: Creating slides...")
            slides_text = self.content_parser.prepare_content_for_video(paragraphs)
            slide_paths = []
            for i, text in enumerate(slides_text):
                slide_path = self.video_generator.create_slide(
                    text, 
                    theme=metadata.get('theme', 'tech')
                )
                slide_paths.append(slide_path)
            console.print(f"Step 4: Done. Created {len(slide_paths)} slides.")

            console.print("Step 5: Creating video...")
            self.video_generator.create_video_from_slides(
                slide_paths, 
                str(audio_path), 
                str(video_path)
            )
            console.print("Step 5: Done.")
            
            console.print(f"[green]✓ Video generated: {video_path}[/green]")
            
            if self.config.get("generate_shorts", True):
                console.print("Step 6: Generating shorts...")
                shorts_path = self.output_dir / "shorts" / f"{base_name}_short.mp4"
                self.video_generator.create_shorts(str(video_path), str(shorts_path))
                console.print("Step 6: Done.")
            
            return str(video_path)
        except Exception as e:
            console.print(f"[bold red]Error in generate_video for {markdown_path}: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            raise

@click.group()
def cli():
    """YTLite - Minimalist YouTube Content Generator"""
    pass

@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
def generate(markdown_file):
    """Generate video from markdown file"""
    # Check dependencies first
    verify_dependencies()
    
    # Generate video
    ytlite = YTLite()
    ytlite.generate_video(markdown_file)

@cli.command()
def check():
    """Check and install dependencies"""
    verify_dependencies()
    console.print("[green]✓ System ready[/]")

@cli.command()
@click.argument('directory', type=click.Path(exists=True), default='content/episodes')
def batch(directory):
    """Generate videos for all markdown files in directory"""
    verify_dependencies()
    
    ytlite = YTLite()
    md_files = list(Path(directory).glob("*.md"))
    
    console.print(f"[cyan]Found {len(md_files)} markdown files[/]")
    
    failures = 0
    for md_file in md_files:
        try:
            ytlite.generate_video(str(md_file))
        except Exception as e:
            console.print(f"[bold red]Error processing {md_file}: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            failures += 1
            continue
    
    if failures > 0:
        console.print(f"[bold red]❌ Finished with {failures} errors.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
