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
from svg_packager import build_svg
from svg_validator import SVGOperationManager, validate_all_project_svgs

# Load environment variables
load_dotenv()

console = Console()
logger = get_logger("ytlite_main")

class YTLite:
    """Main YTLite orchestrator using modular components"""
    
    def __init__(self, config_path: str = "config.yaml", output_dir: str = "output", project_name: str = None, config_overrides: dict = None):
        self.config = self._load_config(config_path)
        self.content_parser = ContentParser()
        self.audio_generator = AudioGenerator(self.config)
        self.video_generator = VideoGenerator(self.config)

        if config_overrides:
            # Deep merge would be better, but for flat keys this is fine
            for key, value in config_overrides.items():
                if value:
                    self.config[key] = value
            logger.info("Applied config overrides from web GUI", extra={"overrides": config_overrides})
        
        # Setup output directories
        self.output_dir = Path(output_dir)
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
            # Prioritize GUI overrides, then frontmatter, then defaults
            lang = self.config.get('lang') or metadata.get('lang')
            theme = self.config.get('theme') or metadata.get('theme', 'tech')
            template = self.config.get('template') or metadata.get('template', 'classic')
            font_size_override = self.config.get('font_size') or metadata.get('font_size')
            colors = self.config.get('colors') or metadata.get('colors')
            if not isinstance(colors, dict):
                colors = None

            # Voice override for audio
            voice_override = self.config.get('voice') or metadata.get('voice')
            if voice_override:
                self.audio_generator.voice = voice_override
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
            self.video_generator.create_thumbnail(str(video_path), str(thumbnail_path), str(audio_path))
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
            logger.info("Packaging step completed for project", extra={"project": base_name})
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

        # Create SVG single-file package with validation
        logger.info("Building SVG package")
        svg_path, is_valid, validation_errors = build_svg(project_dir, metadata, paragraphs, video_path, audio_path, thumbnail_path)
        
        # Report validation results
        if is_valid:
            logger.info(f"✓ SVG generated and validated successfully: {svg_path}")
        else:
            logger.warning(f"⚠ SVG validation issues found:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
        
        # Validate all project SVGs for comprehensive check
        validation_results = validate_all_project_svgs(project_dir)
        invalid_count = sum(1 for is_valid, _ in validation_results.values() if not is_valid)
        
        if invalid_count == 0:
            logger.info(f"✓ All {len(validation_results)} SVG files in project are valid")
        else:
            logger.warning(f"⚠ {invalid_count} of {len(validation_results)} SVG files have validation issues")
        
        logger.info("Packaging done")


        # Create a simple index.md to navigate assets (if not SVG-only)
        index_md = f"""
# {metadata.get('title', base_name)}

![Thumbnail](thumbnail.jpg)

- Video: [video.mp4](video.mp4)
- Audio: [audio.mp3](audio.mp3)
{('- Short: [short.mp4](short.mp4)\n' if shorts_path and os.path.exists(shorts_path) else '')}- Description: [description.md](description.md)
- SVG (single-file package): [{svg_path.name}]({svg_path.name})
"""
        (project_dir / "index.md").write_text(index_md.strip() + "\n", encoding="utf-8")

        # Optional: SVG_ONLY mode - keep only the SVG artifact in the project dir
        try:
            if os.getenv("SVG_ONLY") == "1":
                for fname in ["video.mp4", "audio.mp3", "thumbnail.jpg", "short.mp4", "description.md", "index.md", "source.md"]:
                    fp = project_dir / fname
                    if fp.exists():
                        try:
                            os.remove(fp)
                        except Exception:
                            pass
                # Write a minimal README pointing to the SVG
                (project_dir / "README.md").write_text(f"# {metadata.get('title', base_name)}\n\n- SVG: [{svg_path.name}]({svg_path.name})\n", encoding="utf-8")
        except Exception:
            pass

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

    def run_from_content(self, markdown_content: str, project_name: str, force_regenerate: bool = False):
        """Generate video from markdown content string."""
        project_dir = self.output_dir / "projects" / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        tmp_md_path = project_dir / f"{project_name}.md"

        # If we don't force regenerate, and video exists, skip
        video_path = self.output_dir / "videos" / f"{project_name}.mp4"
        if not force_regenerate and video_path.exists():
            logger.info(f"Video for {project_name} already exists and force_regenerate is False. Skipping.")
            return {"success": True, "message": "Video already exists.", "video_path": str(video_path)}

        try:
            tmp_md_path.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Created temporary markdown file: {tmp_md_path}")
            self.generate_video(str(tmp_md_path))
            return {"success": True, "message": "Video generated successfully."}
        except Exception as e:
            logger.error(f"Failed to generate video from content for {project_name}: {e}", exc_info=True)
            return {"success": False, "message": str(e)}
        finally:
            # Clean up the temporary markdown file if it exists
            if tmp_md_path.exists():
                # pass # Keep for debugging
                tmp_md_path.unlink()

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
@click.option('--project', help='Project name to generate video for')
def generate_project(project):
    """Generate video for a specific project"""
    if not project:
        console.print("[red]Error: --project option is required[/]")
        sys.exit(1)
    
    verify_dependencies()
    ytlite = YTLite(project_name=project)
    project_dir = ytlite.output_dir / "projects" / project
    console.print(f"[cyan]Looking for markdown file in {project_dir}[/]")
    markdown_file = project_dir / "description.md"
    if not markdown_file.exists():
        markdown_file = project_dir / f"{project}.md"
    if not markdown_file.exists():
        console.print(f"[red]Error: Markdown file for project {project} not found in {project_dir}[/]")
        sys.exit(1)
    console.print(f"[cyan]Found markdown file: {markdown_file}[/]")
    ytlite.generate_video(str(markdown_file))

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
