#!/usr/bin/env python3
"""
YTLite - Minimalist YouTube Content Generator
Filozofia: Simple > Complex, Consistency > Perfection
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

import click
import edge_tts
import frontmatter
import yaml
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip
except ImportError:
    console.print("[red]Error: moviepy not installed properly. Installing...[/]")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()

class YTLite:
    """Minimalist YouTube content generator"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "shorts").mkdir(exist_ok=True)
        (self.output_dir / "thumbnails").mkdir(exist_ok=True)
        
        # Predefiniowane style wizualne (proste!)
        self.themes = {
            "tech": {
                "bg_color": "#1e1e2e",
                "text_color": "#cdd6f4",
                "accent": "#89b4fa"
            },
            "philosophy": {
                "bg_color": "#2e2e3e",
                "text_color": "#f5f5f5",
                "accent": "#ffd700"
            },
            "wetware": {
                "bg_gradient": ["#667eea", "#764ba2"],
                "text_color": "#ffffff",
                "accent": "#ff6b6b"
            }
        }
    
    def _load_config(self, path: str) -> dict:
        """Load or create default config"""
        if Path(path).exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default config from environment or fallback
        return {
            "voice": os.getenv("EDGE_TTS_VOICE", "pl-PL-MarekNeural"),
            "resolution": [1280, 720],
            "fps": int(os.getenv("VIDEO_FPS", 30)),
            "font_size": int(os.getenv("FONT_SIZE", 48)),
            "style": "minimalist"
        }
    
    async def generate_audio(self, text: str, output_file: str) -> str:
        """Generate audio using edge-tts (free!)"""
        voice = self.config.get("voice", os.getenv("EDGE_TTS_VOICE", "pl-PL-MarekNeural"))
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return output_file
    
    def create_simple_slide(self, text: str, theme: str = "tech") -> Image.Image:
        """Create minimalist slide - just text on gradient"""
        width, height = self.config["resolution"]
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Simple gradient background
        theme_config = self.themes.get(theme, self.themes["tech"])
        if "bg_gradient" in theme_config:
            # Simple two-color gradient
            for i in range(height):
                ratio = i / height
                r = int(102 * (1-ratio) + 118 * ratio)
                g = int(126 * (1-ratio) + 75 * ratio)
                b = int(234 * (1-ratio) + 162 * ratio)
                draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
        else:
            draw.rectangle([(0, 0), (width, height)], fill=theme_config["bg_color"])
        
        # Add text (centered, wrapped)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                                     self.config["font_size"])
        except:
            console.print("[yellow]Warning: Could not load DejaVuSans-Bold font. Falling back to default.[/]")
            try:
                font = ImageFont.load_default()
            except:
                console.print("[red]Error: Could not load any font. Text rendering may fail.[/]")
                font = None
        
        # Simple text wrapping
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(test_line) * 10  # Rough estimate
            
            if text_width > width - 100:  # Leave margins
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw centered text
        y_offset = (height - len(lines) * 60) // 2
        for line in lines:
            if font:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 10
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill=theme_config["text_color"], font=font)
            y_offset += 60
        
        return img
    
    def create_video_from_markdown(self, md_file: Path) -> Path:
        """Main function - markdown to video"""
        console.print(f"[bold green]Processing:[/] {md_file.name}")
        
        # Parse markdown with frontmatter
        with open(md_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        metadata = post.metadata
        content = post.content
        
        # Split content into paragraphs (each = one slide)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Determine theme from metadata or filename
        theme = metadata.get('theme', 'tech')
        if 'człowieczy' in str(md_file).lower() or 'philosophy' in str(md_file).lower():
            theme = 'philosophy'
        elif 'wetware' in str(md_file).lower():
            theme = 'wetware'
        
        # Generate audio for full text
        audio_file = self.output_dir / "videos" / f"{md_file.stem}_audio.mp3"
        full_text = ' '.join(paragraphs)
        
        console.print("[yellow]Generating audio...[/]")
        asyncio.run(self.generate_audio(full_text, str(audio_file)))
        
        # Load audio and calculate duration
        audio_clip = AudioFileClip(str(audio_file))
        total_duration = audio_clip.duration
        slide_duration = total_duration / len(paragraphs) if paragraphs else 5
        
        # Generate slides
        console.print("[yellow]Creating slides...[/]")
        video_clips = []
        
        for i, paragraph in enumerate(track(paragraphs, description="Generating slides")):
            # Create slide
            slide_img = self.create_simple_slide(paragraph[:200], theme)
            
            # Convert to video clip
            slide_array = np.array(slide_img)
            slide_clip = ImageClip(slide_array).set_duration(slide_duration)
            
            # Add simple fade transition
            if i > 0:
                slide_clip = slide_clip.crossfadein(0.5)
            
            video_clips.append(slide_clip)
        
        if not video_clips:
            # Create a single slide with title if no content
            title_slide = self.create_simple_slide(metadata.get('title', 'YTLite Video'), theme)
            video_clips = [ImageClip(np.array(title_slide)).set_duration(audio_clip.duration)]
        
        # Concatenate all slides
        console.print("[yellow]Composing video...[/]")
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.set_audio(audio_clip)
        
        # Export
        output_file = self.output_dir / "videos" / f"{md_file.stem}.mp4"
        console.print("[yellow]Exporting video...[/]")
        
        final_video.write_videofile(
            str(output_file),
            fps=self.config["fps"],
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=4,
            logger=None  # Suppress moviepy output
        )
        
        console.print(f"[bold green]✓ Video saved:[/] {output_file}")
        
        # Clean up temp audio
        if audio_file.exists():
            audio_file.unlink()
        
        return output_file
    
    def create_shorts_version(self, video_path: Path) -> Path:
        """Extract 60s highlight for YouTube Shorts"""
        console.print("[yellow]Creating Shorts version...[/]")
        
        video = VideoFileClip(str(video_path))
        
        # Take middle 60 seconds (usually the meat of content)
        duration = video.duration
        shorts_duration = int(os.getenv("SHORTS_DURATION", 60))
        
        if duration > shorts_duration:
            start = (duration - shorts_duration) / 2
            short_clip = video.subclip(start, start + shorts_duration)
        else:
            short_clip = video
        
        # Resize to 9:16 (Shorts format)
        short_clip = short_clip.resize(height=1920)
        if short_clip.w > 1080:
            short_clip = short_clip.crop(x_center=short_clip.w/2, width=1080)
        
        # Add "SHORTS" watermark
        try:
            txt_clip = TextClip("SHORTS", fontsize=40, color='white', font='Arial')
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(short_clip.duration)
            final_short = CompositeVideoClip([short_clip, txt_clip])
        except:
            console.print("[yellow]Warning: TextClip failed. Falling back to video without watermark.[/]")
            final_short = short_clip
        
        # Export
        output_file = self.output_dir / "shorts" / f"{video_path.stem}_short.mp4"
        
        final_short.write_videofile(
            str(output_file),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            logger=None
        )
        
        console.print(f"[bold green]✓ Shorts saved:[/] {output_file}")
        return output_file
    
    def generate_thumbnail(self, video_path: Path, title: str) -> Path:
        """Auto-generate thumbnail"""
        video = VideoFileClip(str(video_path))
        
        # Get frame from 1/3 of video (usually interesting part)
        frame = video.get_frame(video.duration / 3)
        img = Image.fromarray(frame.astype('uint8'))
        
        # Add text overlay
        draw = ImageDraw.Draw(img)
        
        # Semi-transparent background for text
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(0, img.height//2), (img.width, img.height)], 
                               fill=(0, 0, 0, 180))
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Add title
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            console.print("[yellow]Warning: Could not load DejaVuSans-Bold font. Falling back to default.[/]")
            try:
                font = ImageFont.load_default()
            except:
                console.print("[red]Error: Could not load any font. Text rendering may fail.[/]")
                font = None
        
        # Wrap title
        words = title.split()
        if len(words) > 5:
            title = ' '.join(words[:5]) + '\n' + ' '.join(words[5:])
        
        draw.text((img.width//2, img.height*3//4), title, 
                 fill='white', font=font, anchor='mm')
        
        # Save
        thumb_path = self.output_dir / "thumbnails" / f"{video_path.stem}_thumb.jpg"
        img.save(thumb_path, quality=95)
        
        console.print(f"[bold green]✓ Thumbnail saved:[/] {thumb_path}")
        return thumb_path


# CLI Interface
@click.group()
def cli():
    """YTLite - Minimalist YouTube content automation"""
    pass

@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
def generate(markdown_file):
    """Generate video from markdown file"""
    generator = YTLite()
    video_path = generator.create_video_from_markdown(Path(markdown_file))
    
    # Also create shorts and thumbnail if enabled
    if os.getenv("GENERATE_SHORTS", "true").lower() == "true":
        generator.create_shorts_version(video_path)
    
    # Extract title for thumbnail
    with open(markdown_file, 'r') as f:
        post = frontmatter.load(f)
        title = post.metadata.get('title', Path(markdown_file).stem)
    
    generator.generate_thumbnail(video_path, title)

@cli.command()
@click.argument('video_files', nargs=-1, type=click.Path(exists=True))
def shorts(video_files):
    """Create Shorts from existing videos"""
    generator = YTLite()
    
    if not video_files:
        # Process all videos in output/videos
        video_files = list(Path("output/videos").glob("*.mp4"))
    
    for video_file in video_files:
        generator.create_shorts_version(Path(video_file))

@cli.command()
def daily():
    """Generate daily content based on trending topics"""
    console.print("[yellow]Generating daily content...[/]")
    
    # Example: create content based on date
    today = datetime.now()
    
    content = f"""---
title: Tech Refleksja #{today.strftime('%j')}
date: {today.strftime('%Y-%m-%d')}
theme: philosophy
tags: [daily, tech, philosophy]
---

# {today.strftime('%A, %d %B %Y')}

Dziś zastanawiam się nad tym, jak technologia zmienia nasze postrzeganie czasu.

Każda sekunda jest zapisywana, każdy moment utrwalony, a jednak czujemy, że czas ucieka szybciej niż kiedykolwiek.

Może to nie technologia przyspiesza czas, ale nasza obsesja na punkcie jego dokumentowania?

Pomyśl o tym dzisiaj. Kiedy ostatni raz byłeś w pełni obecny, bez telefonu w ręku?
"""
    
    # Save to file
    content_dir = Path("content/episodes")
    content_dir.mkdir(parents=True, exist_ok=True)
    
    filename = content_dir / f"daily_{today.strftime('%Y%m%d')}.md"
    filename.write_text(content, encoding='utf-8')
    
    # Generate video
    generator = YTLite()
    generator.create_video_from_markdown(filename)
    
    console.print("[bold green]✓ Daily content ready![/]")
    
@cli.command()
def stats():
    """Show channel statistics"""
    output_dir = Path("output")
    videos = list((output_dir / "videos").glob("*.mp4"))
    shorts = list((output_dir / "shorts").glob("*.mp4"))
    
    console.print("[bold cyan]📊 YTLite Statistics[/]")
    console.print(f"Videos generated: [bold]{len(videos)}[/]")
    console.print(f"Shorts created: [bold]{len(shorts)}[/]")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in videos + shorts)
    console.print(f"Total size: [bold]{total_size / (1024*1024):.2f} MB[/]")
    
    # Show latest
    if videos:
        latest = max(videos, key=lambda f: f.stat().st_mtime)
        console.print(f"Latest video: [bold]{latest.name}[/]")

@cli.command()
def watch():
    """Watch for new markdown files and auto-generate"""
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    
    class MarkdownHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.src_path.endswith('.md'):
                console.print(f"[bold yellow]New file detected:[/] {event.src_path}")
                generator = YTLite()
                generator.create_video_from_markdown(Path(event.src_path))
    
    observer = Observer()
    observer.schedule(MarkdownHandler(), 'content/episodes', recursive=False)
    observer.start()
    
    console.print("[bold green]Watching for new content...[/] (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    cli()
