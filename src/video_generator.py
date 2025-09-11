#!/usr/bin/env python3
"""
YTLite Video Generator Module
Handles video creation from images and audio
"""

import os
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from logging_setup import get_logger

console = Console()
logger = get_logger("video")

# Import MoviePy using explicit submodules for broad compatibility
try:
    from moviepy.editor import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
except ImportError:
    console.print("[yellow]Warning: moviepy.editor not found, trying alternative imports...[/]")
    try:
        from moviepy.video.VideoClip import VideoFileClip, ImageClip, TextClip, CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.audio.AudioClip import AudioFileClip
    except ImportError as e:
        console.print(f"[red]Error: Failed to import moviepy components: {e}[/]")
        logger.error("MoviePy import failed", extra={"error": str(e)})
        raise

class VideoGenerator:
    def __init__(self, config):
        self.config = config
        self.resolution = tuple(config.get("resolution", [1280, 720]))
        self.fps = config.get("fps", 30)
        self.font_size = config.get("font_size", 48)
        
    def _pick_font(self, lang: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        # Language-aware font selection (DejaVu covers PL/DE/EN). Allow override via config font_path
        font_path = self.config.get("font_path")
        candidates = []
        if font_path:
            candidates.append(font_path)
        # Common Linux path
        candidates.append("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        # MacOS
        candidates.append("/Library/Fonts/Arial Unicode.ttf")
        # Fallbacks
        for fp in candidates:
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
        console.print("[yellow]Warning: Could not load font, using default[/]")
        return ImageFont.load_default()

    def _parse_hex(self, hexstr: str) -> tuple[int, int, int]:
        s = hexstr.lstrip('#')
        if len(s) == 3:
            s = ''.join([c*2 for c in s])
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except Exception:
            return (30, 30, 46)

    def _draw_gradient_bg(self, img: Image.Image, start: str = "#1e1e2e", end: str = "#3b3b5b"):
        w, h = img.size
        draw = ImageDraw.Draw(img)
        sr, sg, sb = self._parse_hex(start)
        er, eg, eb = self._parse_hex(end)
        for y in range(h):
            ratio = y / max(1, h - 1)
            r = int(sr + (er - sr) * ratio)
            g = int(sg + (eg - sg) * ratio)
            b = int(sb + (eb - sb) * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

    def create_slide(self, text: str, theme: str = "tech", lang: str | None = None,
                     template: str = "classic", font_size: int | None = None,
                     colors: dict | None = None) -> str:
        """Create a slide image from text with optional template and language-aware font."""
        # Get theme colors
        themes = self.config.get("themes", {})
        theme_config = themes.get(theme, themes.get("tech", {}))
        if colors:
            theme_config = {**theme_config, **colors}
        bg_color = theme_config.get("bg_color", "#1e1e2e")
        text_color = theme_config.get("text_color", "#cdd6f4")

        # Create image
        img = Image.new("RGB", self.resolution, bg_color)
        draw = ImageDraw.Draw(img)

        # Optional gradient background
        if template == "gradient":
            try:
                # Use darker/lighter variant if available
                self._draw_gradient_bg(img, bg_color, theme_config.get("bg_color_2", "#3b3b5b"))
            except Exception:
                pass

        # Font
        fsize = int(font_size or self.font_size)
        font = self._pick_font(lang, fsize)

        # Multi-line support (split on \n)
        lines = [line for line in text.split("\n") if line.strip()]
        line_heights = []
        max_w = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            max_w = max(max_w, w)
            line_heights.append(h)
        total_h = sum(line_heights) + (len(lines) - 1) * int(fsize * 0.3)

        # Positioning
        x = (self.resolution[0] - max_w) // 2
        y = (self.resolution[1] - total_h) // 2
        if template == "left":
            x = int(self.resolution[0] * 0.1)
        
        # Optional boxed background for text
        if template == "boxed":
            padding = int(fsize * 0.6)
            box_w = max_w + 2 * padding
            box_h = total_h + 2 * padding
            box_x = (self.resolution[0] - box_w) // 2
            box_y = (self.resolution[1] - box_h) // 2
            draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=theme_config.get("box_color", "#00000080"))

        # Draw each line
        cur_y = y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if template != "left":
                cur_x = (self.resolution[0] - w) // 2
            else:
                cur_x = x
            draw.text((cur_x, cur_y), line, fill=text_color, font=font)
            cur_y += h + int(fsize * 0.3)

        # Save temporary image
        temp_path = f"/tmp/slide_{hash((text, theme, template, fsize))}.png"
        img.save(temp_path)
        logger.info("Slide created", extra={"path": temp_path, "len": len(text)})
        return temp_path
    
    def create_video_from_slides(self, slides: List[str], audio_path: str, output_path: str):
        """Create video from slide images and audio"""
        
        console.print(f"[cyan]Creating video from {len(slides)} slides...[/]")
        logger.info("Create video start", extra={"slides": len(slides), "audio": audio_path, "output": output_path})
        
        # Load audio to get duration
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        slide_duration = total_duration / len(slides)
        
        # Create video clips from slides
        clips = []
        for slide_path in slides:
            clip = ImageClip(slide_path).set_duration(slide_duration)
            clips.append(clip)
        
        # Concatenate clips
        video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        final_video = video.set_audio(audio)
        
        # Write output
        console.print(f"[cyan]Writing video to {output_path}...[/]")
        try:
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                logger=None,  # Suppress moviepy output
                verbose=False,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
        except Exception as e:
            console.print(f"[red]Error writing video: {e}[/]")
            logger.error("write_videofile failed", extra={"error": str(e)})
            raise
        
        console.print(f"[green]✓ Video created: {output_path}[/]")
        logger.info("Video created", extra={"output": output_path})
        
        # Cleanup
        for slide_path in slides:
            if os.path.exists(slide_path):
                os.remove(slide_path)
    
    def create_shorts(self, video_path: str, output_path: str):
        """Create YouTube Shorts from video"""
        
        console.print(f"[cyan]Creating Shorts from {video_path}...[/]")
        
        video = VideoFileClip(video_path)
        
        # Get first 60 seconds
        duration = min(60, video.duration)
        short_clip = video.subclip(0, duration)
        
        # Resize to 9:16 aspect ratio with compatibility across MoviePy versions
        try:
            # Prefer functional FX (MoviePy 2.x compatible)
            try:
                from moviepy.video.fx.resize import resize as fx_resize
            except Exception:
                from moviepy.video.fx.all import resize as fx_resize
            try:
                from moviepy.video.fx.crop import crop as fx_crop
            except Exception:
                from moviepy.video.fx.all import crop as fx_crop
            short_clip = fx_resize(short_clip, height=1920)
            short_clip = fx_crop(short_clip, x_center=short_clip.w/2, width=1080)
        except Exception:
            # Fallback to method API (MoviePy 1.x)
            try:
                short_clip = short_clip.resize(height=1920)
                short_clip = short_clip.crop(x_center=short_clip.w/2, width=1080)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to apply resize/crop FX: {e}[/]")

        # Add watermark
        try:
            txt_clip = TextClip("SHORTS", fontsize=40, color='white', font='Arial')
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(short_clip.duration)
            final_short = CompositeVideoClip([short_clip, txt_clip])
        except:
            console.print("[yellow]Warning: Could not add watermark[/]")
            final_short = short_clip
        
        # Write output
        final_short.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            logger=None
        )
        
        console.print(f"[green]✓ Shorts created: {output_path}[/]")

    def create_thumbnail(self, video_path: str, output_path: str):
        """Create a thumbnail image from a representative video frame"""
        console.print(f"[cyan]Creating thumbnail for {video_path}...[/]")
        logger.info("Create thumbnail start", extra={"video": video_path, "output": output_path})
        clip = VideoFileClip(video_path)
        # Take frame from 1/3rd of the video or at 0.5s if too short
        ts = max(0.5, min(clip.duration - 0.05, clip.duration / 3))
        frame = clip.get_frame(ts)
        img = Image.fromarray(frame)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, format='JPEG', quality=90)
        console.print(f"[green]✓ Thumbnail created: {output_path}[/]")
        logger.info("Thumbnail created", extra={"output": output_path})
