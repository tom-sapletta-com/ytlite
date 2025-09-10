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

console = Console()

# Import moviepy directly
try:
    from moviepy.editor import (
        VideoFileClip, TextClip, CompositeVideoClip, 
        ImageClip, concatenate_videoclips, AudioFileClip
    )
except ImportError:
    console.print("[red]MoviePy not available. Installing...[/]")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy.editor import (
        VideoFileClip, TextClip, CompositeVideoClip, 
        ImageClip, concatenate_videoclips, AudioFileClip
    )

class VideoGenerator:
    def __init__(self, config):
        self.config = config
        self.resolution = tuple(config.get("resolution", [1280, 720]))
        self.fps = config.get("fps", 30)
        self.font_size = config.get("font_size", 48)
        
    def create_slide(self, text: str, theme: str = "tech") -> str:
        """Create a slide image from text"""
        # Get theme colors
        themes = self.config.get("themes", {})
        theme_config = themes.get(theme, themes.get("tech"))
        
        bg_color = theme_config.get("bg_color", "#1e1e2e")
        text_color = theme_config.get("text_color", "#cdd6f4")
        
        # Create image
        img = Image.new("RGB", self.resolution, bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                                    self.font_size)
        except:
            console.print("[yellow]Warning: Could not load font, using default[/]")
            font = ImageFont.load_default()
        
        # Draw text centered
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.resolution[0] - text_width) // 2
        y = (self.resolution[1] - text_height) // 2
        
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Save temporary image
        temp_path = f"/tmp/slide_{hash(text)}.png"
        img.save(temp_path)
        return temp_path
    
    def create_video_from_slides(self, slides: List[str], audio_path: str, output_path: str):
        """Create video from slide images and audio"""
        
        console.print(f"[cyan]Creating video from {len(slides)} slides...[/]")
        
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
            raise
        
        console.print(f"[green]✓ Video created: {output_path}[/]")
        
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
        
        # Resize to 9:16 aspect ratio
        short_clip = short_clip.resize(height=1920)
        short_clip = short_clip.crop(x_center=short_clip.w/2, width=1080)
        
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
