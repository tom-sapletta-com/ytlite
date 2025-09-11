#!/usr/bin/env python3
"""
YTLite - Main Entry Point
Refactored to use modular components
"""

import os
import sys
import shutil
from pathlib import Path
import click
import yaml
from rich.console import Console
from dotenv import load_dotenv
from logging_setup import get_logger
from progress import ProgressReporter

# Import our modules
from dependencies import verify_dependencies
from content_parser import ContentParser
from audio_generator import AudioGenerator
from video_generator import VideoGenerator

# Load environment variables
load_dotenv()

console = Console()
logger = get_logger("ytlite_main")

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
                cfg = yaml.safe_load(f)
        else:
            console.print(f"[yellow]Config file {config_path} not found. Using defaults.[/]")
            cfg = {
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
        # FAST_TEST overrides to make E2E quick
        try:
            import os
            if os.getenv("YTLITE_FAST_TEST") == "1":
                cfg = dict(cfg or {})
                cfg.setdefault("resolution", [320, 180])
                cfg.setdefault("fps", 12)
                cfg.setdefault("font_size", 24)
                cfg["generate_shorts"] = False
                logger.info("FAST_TEST config overrides applied", extra={"resolution": cfg["resolution"], "fps": cfg["fps"]})
        except Exception:
            pass
        return cfg
    
    def generate_video(self, markdown_path: str):
        """Generate video from markdown file"""
        console.print(f"[bold cyan]Processing: {markdown_path}[/bold cyan]")
        try:
            # Load per-project .env if present (output/projects/<stem>/.env)
            try:
                base_for_env = Path(markdown_path).stem
                env_path = self.output_dir / "projects" / base_for_env / ".env"
                if env_path.exists():
                    load_dotenv(env_path)
                    console.print(f"[dim]Loaded per-project .env: {env_path}[/dim]")
                    logger.info("Loaded per-project .env", extra={"env": str(env_path)})
            except Exception:
                pass

            # Initialize progress reporter
            base_name = Path(markdown_path).stem
            pr = ProgressReporter(base_name, self.output_dir)
            pr.update("parse", "Step 1: Parsing content...", 10, {"file": markdown_path})
            console.print("Step 1: Parsing content...")
            logger.info("Step 1: parse_markdown start", extra={"file": markdown_path})
            metadata, paragraphs = self.content_parser.parse_markdown(markdown_path)
            console.print("Step 1: Done.")
            logger.info("Step 1: parse_markdown done", extra={"title": metadata.get('title')})
            pr.update("parse_done", "Step 1: Done.", 20, {"title": metadata.get('title')})

            console.print("Step 2: Preparing output paths...")
            audio_path = self.output_dir / "audio" / f"{base_name}.mp3"
            video_path = self.output_dir / "videos" / f"{base_name}.mp4"
            console.print(f"Audio path: {audio_path}")
            console.print(f"Video path: {video_path}")
            console.print("Step 2: Done.")
            logger.info("Step 2: paths prepared", extra={"audio": str(audio_path), "video": str(video_path)})
            pr.update("paths", "Step 2: Paths ready", 30, {"audio": str(audio_path), "video": str(video_path)})

            console.print("Step 3: Generating audio...")
            combined_text = self.audio_generator.combine_text_for_audio(paragraphs)
            self.audio_generator.generate_audio(combined_text, str(audio_path))
            console.print("Step 3: Done.")
            logger.info("Step 3: audio done", extra={"audio": str(audio_path)})
            pr.update("audio", "Step 3: Audio ready", 50, {"audio": str(audio_path)})

            console.print("Step 4: Creating slides...")
            slides_text = self.content_parser.prepare_content_for_video(paragraphs)
            slide_paths = []
            # Metadata overrides
            lang = metadata.get('lang')
            theme = metadata.get('theme', 'tech')
            template = metadata.get('template', 'classic')
            font_size_override = metadata.get('font_size')
            colors = metadata.get('colors') if isinstance(metadata.get('colors'), dict) else None
            # Voice override for audio
            if metadata.get('voice'):
                self.audio_generator.voice = metadata['voice']
            for i, text in enumerate(slides_text):
                slide_path = self.video_generator.create_slide(
                    text,
                    theme=theme,
                    lang=lang,
                    template=template,
                    font_size=font_size_override,
                    colors=colors
                )
                slide_paths.append(slide_path)
            console.print(f"Step 4: Done. Created {len(slide_paths)} slides.")
            logger.info("Step 4: slides done", extra={"count": len(slide_paths)})
            pr.update("slides", f"Step 4: {len(slide_paths)} slides created", 65, {"count": len(slide_paths)})

            console.print("Step 5: Creating video...")
            self.video_generator.create_video_from_slides(
                slide_paths, 
                str(audio_path), 
                str(video_path)
            )
            console.print("Step 5: Done.")
            logger.info("Step 5: video done", extra={"video": str(video_path)})
            pr.update("video", "Step 5: Video ready", 85, {"video": str(video_path)})
            
            console.print(f"[green]✓ Video generated: {video_path}[/green]")
            # Generate thumbnail
            thumbnail_path = self.output_dir / "thumbnails" / f"{base_name}.jpg"
            self.video_generator.create_thumbnail(str(video_path), str(thumbnail_path))
            logger.info("Thumbnail created", extra={"thumb": str(thumbnail_path)})
            pr.update("thumbnail", "Thumbnail created", 90, {"thumb": str(thumbnail_path)})

            if self.config.get("generate_shorts", True):
                console.print("Step 6: Generating shorts...")
                shorts_path = self.output_dir / "shorts" / f"{base_name}_short.mp4"
                try:
                    self.video_generator.create_shorts(str(video_path), str(shorts_path))
                    console.print("Step 6: Done.")
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to generate shorts: {e}[/]")
                    shorts_path = None
                    logger.warning("Shorts generation failed", extra={"error": str(e)})
            else:
                shorts_path = None
            pr.update("shorts", "Step 6: Shorts done or skipped", 92, {"shorts": bool(shorts_path)})

            # Package project assets into output/projects/<name>
            self.package_project(
                base_name=base_name,
                metadata=metadata,
                paragraphs=paragraphs,
                markdown_path=markdown_path,
                audio_path=str(audio_path),
                video_path=str(video_path),
                thumbnail_path=str(thumbnail_path),
                shorts_path=str(shorts_path) if shorts_path else None,
            )
            logger.info("Packaging done", extra={"project": base_name})
            pr.update("package", "Packaging done", 98)

            pr.done("Completed")
            return str(video_path)
        except Exception as e:
            console.print(f"[bold red]Error in generate_video for {markdown_path}: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            logger.error("generate_video failed", extra={"file": markdown_path, "error": str(e)})
            raise

    def package_project(self, base_name: str, metadata: dict, paragraphs: list, markdown_path: str,
                        audio_path: str, video_path: str, thumbnail_path: str, shorts_path: str | None = None):
        """Create per-project folder with all assets and a description markdown."""
        project_dir = self.output_dir / "projects" / base_name
        project_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Packaging start", extra={"project_dir": str(project_dir)})

        # Copy assets
        try:
            shutil.copy2(video_path, project_dir / "video.mp4")
        except Exception as e:
            console.print(f"[yellow]Warning: could not copy video: {e}")
            logger.warning("Copy video failed", extra={"error": str(e)})
        try:
            shutil.copy2(audio_path, project_dir / "audio.mp3")
        except Exception as e:
            console.print(f"[yellow]Warning: could not copy audio: {e}")
            logger.warning("Copy audio failed", extra={"error": str(e)})
        try:
            shutil.copy2(thumbnail_path, project_dir / "thumbnail.jpg")
        except Exception as e:
            console.print(f"[yellow]Warning: could not copy thumbnail: {e}")
            logger.warning("Copy thumbnail failed", extra={"error": str(e)})
        if shorts_path and os.path.exists(shorts_path):
            try:
                shutil.copy2(shorts_path, project_dir / "short.mp4")
            except Exception as e:
                console.print(f"[yellow]Warning: could not copy short: {e}")
                logger.warning("Copy short failed", extra={"error": str(e)})

        # Save original source content for reference
        try:
            src_text = Path(markdown_path).read_text(encoding="utf-8")
            (project_dir / "source.md").write_text(src_text, encoding="utf-8")
        except Exception:
            pass

        # Create description.md based on metadata and paragraphs
        fm_lines = [
            "---",
            f"title: {metadata.get('title', base_name)}",
            f"date: {metadata.get('date', '')}",
            f"theme: {metadata.get('theme', 'tech')}",
            f"tags: {metadata.get('tags', [])}",
            "---",
            "",
        ]
        description_body = "\n\n".join(paragraphs) if paragraphs else metadata.get('title', base_name)
        (project_dir / "description.md").write_text("\n".join(fm_lines) + description_body + "\n", encoding="utf-8")

        # Create a simple index.md to navigate assets
        index_md = f"""
# {metadata.get('title', base_name)}

![Thumbnail](thumbnail.jpg)

- Video: [video.mp4](video.mp4)
- Audio: [audio.mp3](audio.mp3)
{('- Short: [short.mp4](short.mp4)\n' if shorts_path and os.path.exists(shorts_path) else '')}- Description: [description.md](description.md)
"""
        (project_dir / "index.md").write_text(index_md.strip() + "\n", encoding="utf-8")

    def build_output_index(self):
        """Build output/README.md summary with links and thumbnails to projects."""
        projects_root = self.output_dir / "projects"
        projects_root.mkdir(parents=True, exist_ok=True)
        items = []
        for p in sorted(projects_root.glob("*/")):
            name = p.name
            title = name
            desc_path = p / "description.md"
            if desc_path.exists():
                try:
                    import frontmatter
                    post = frontmatter.load(desc_path)
                    title = post.metadata.get('title', name)
                except Exception:
                    pass
            items.append({
                'name': name,
                'title': title,
                'thumb': f"projects/{name}/thumbnail.jpg",
                'video': f"projects/{name}/video.mp4",
                'index': f"projects/{name}/index.md",
            })

        lines = [
            "# Output Projects Index",
            "",
            "Kliknij miniaturkę, aby obejrzeć wideo lub wejdź do projektu:",
            "",
        ]
        for it in items:
            lines.append(f"## {it['title']}")
            lines.append("")
            lines.append(f"[![{it['title']}]({it['thumb']})]({it['video']})")
            lines.append("")
            lines.append(f"- Projekt: [{it['name']}]({it['index']})")
            lines.append("")

        (self.output_dir / "README.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        logger.info("Output index written", extra={"path": str(self.output_dir / 'README.md'), "count": len(items)})

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
    
    # Build index summary after batch
    try:
        ytlite.build_output_index()
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to build output index: {e}[/]")

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
