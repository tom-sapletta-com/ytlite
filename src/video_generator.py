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
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.VideoClip import ImageClip, TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.audio.io.AudioFileClip import AudioFileClip
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
        # Cache fonts by (path, size) and avoid repeating fallback warnings
        self._font_cache: dict[tuple[str, int], ImageFont.ImageFont] = {}
        self._font_warning_emitted = False
        
    def _pick_font(self, lang: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Pick a font with caching and environment/config overrides.
        Respects config['font_path'], env YTLITE_FONT_PATH or FONT_PATH.
        Emits the fallback warning at most once per process.
        """
        # Prefer explicit overrides
        font_path = self.config.get("font_path")
        env_font = os.getenv("YTLITE_FONT_PATH") or os.getenv("FONT_PATH")
        candidates: list[str] = []
        if font_path:
            candidates.append(font_path)
        if env_font:
            candidates.append(env_font)
        # Common font locations across Linux/macOS
        candidates.extend([
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ])

        for fp in candidates:
            if not fp:
                continue
            cache_key = (fp, int(size))
            if cache_key in self._font_cache:
                return self._font_cache[cache_key]
            try:
                font = ImageFont.truetype(fp, size)
                self._font_cache[cache_key] = font
                return font
            except Exception:
                continue
        # Fallback
        if not self._font_warning_emitted:
            console.print("[yellow]Warning: Could not load preferred fonts, using default[/]")
            try:
                logger.warning("Falling back to default font; set config.font_path or YTLITE_FONT_PATH for custom font")
            except Exception:
                pass
            self._font_warning_emitted = True
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
                     template: str = "classic", font_size: int | str | None = None,
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
        if isinstance(font_size, str):
            font_size_map = {
                'small': 24,
                'medium': 48,
                'large': 72
            }
            fsize = font_size_map.get(font_size.lower(), self.font_size)
        else:
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
        audio = None
        clips: list[ImageClip] = []
        video = None
        final_video = None
        try:
            # Load audio to get duration
            audio = AudioFileClip(audio_path)
            total_duration = max(0.1, float(audio.duration or 0.1))
            slide_count = max(1, len(slides))
            slide_duration = total_duration / slide_count

            # Create video clips from slides
            for slide_path in slides:
                try:
                    clip = ImageClip(slide_path).set_duration(slide_duration)
                    clips.append(clip)
                except Exception as e:
                    console.print(f"[red]Error creating clip from slide {slide_path}: {e}[/]")
                    logger.error("Error creating clip from slide", extra={"error": str(e), "slide_path": slide_path})
                    raise

            # Concatenate clips
            try:
                video = concatenate_videoclips(clips, method="compose")
            except Exception as e:
                console.print(f"[red]Error concatenating video clips: {e}[/]")
                logger.error("Error concatenating video clips", extra={"error": str(e)})
                raise

            # Add audio
            try:
                final_video = video.set_audio(audio)
            except Exception as e:
                console.print(f"[red]Error setting audio to video: {e}[/]")
                logger.error("Error setting audio to video", extra={"error": str(e)})
                raise

            # Write output
            console.print(f"[cyan]Writing video to {output_path}...[/]")
            try:
                final_video.write_videofile(
                    output_path,
                    fps=self.fps,
                    codec="libx264",
                    audio_codec="aac",
                    logger=None,
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
            except Exception as e:
                console.print(f"[red]Error writing video file: {e}[/]")
                logger.error("Error writing video file", extra={"error": str(e), "output_file": output_path})
                raise

            console.print(f"[green]✓ Video created: {output_path}[/]")
            logger.info("Video created", extra={"output": output_path})
        except Exception as e:
            console.print(f"[red]Failed to create video: {e}[/]")
            logger.error("Failed to create video", extra={"error": str(e)})
            raise
        finally:
            # Cleanup resources and temp files
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass
            try:
                if final_video is not None:
                    final_video.close()
            except Exception:
                pass
            try:
                if video is not None:
                    video.close()
            except Exception:
                pass
            try:
                if audio is not None:
                    audio.close()
            except Exception:
                pass
            for slide_path in slides:
                try:
                    if os.path.exists(slide_path):
                        os.remove(slide_path)
                except Exception:
                    pass

    def create_shorts(self, video_path: str, output_path: str):
        """Create YouTube Shorts from video"""
        console.print(f"[cyan]Creating Shorts from {video_path}...[/]")
        video = None
        short_clip = None
        txt_clip = None
        final_short = None
        try:
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
            except Exception:
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
        finally:
            # Close resources
            for clip in [txt_clip, short_clip, final_short]:
                try:
                    if clip is not None:
                        clip.close()
                except Exception:
                    pass
            try:
                if video is not None:
                    video.close()
            except Exception:
                pass

    def create_thumbnail(self, video_path: str, output_path: str, audio_path: Optional[str] = None):
        """Create a thumbnail image from a representative video frame and overlay
        an audio waveform in the bottom 20% of the image if audio is available.
        If audio is missing or fails to load, draw a baseline instead.
        """
        console.print(f"[cyan]Creating thumbnail for {video_path}...[/]")
        logger.info("Create thumbnail start", extra={"video": video_path, "output": output_path})
        clip = None
        img = None
        try:
            clip = VideoFileClip(video_path)
            # Take frame from 1/3rd of the video or at 0.5s if too short
            ts = max(0.5, min(clip.duration - 0.05, clip.duration / 3))
            frame = clip.get_frame(ts)
            img = Image.fromarray(frame)
        finally:
            try:
                if clip is not None:
                    clip.close()
            except Exception:
                pass
        # Overlay audio waveform on the bottom part of the image (configurable)
        if img is not None:
            try:
                # Read config for waveform rendering
                wf_cfg = (self.config.get("thumbnail") or {}).get("waveform", {})
                height_ratio = float(wf_cfg.get("height_ratio", 0.20))
                # Colors from config (hex + alpha)
                def _rgba(hexstr: str, alpha: int) -> tuple[int, int, int, int]:
                    r, g, b = self._parse_hex(hexstr)
                    a = max(0, min(255, int(alpha)))
                    return (r, g, b, a)
                wave_color = _rgba(wf_cfg.get("color", "#00ff88"), int(wf_cfg.get("alpha", 180)))
                bg_rgba = _rgba(wf_cfg.get("bg_color", "#000000"), int(wf_cfg.get("bg_alpha", 120)))
                axes_color = _rgba(wf_cfg.get("axes_color", "#ffffff"), int(wf_cfg.get("axes_alpha", 80)))
                baseline_color = _rgba(wf_cfg.get("baseline_color", "#ffffff"), int(wf_cfg.get("baseline_alpha", 160)))
                show_axes = bool(wf_cfg.get("show_axes", True))
                time_tick_seconds = max(1, int(wf_cfg.get("time_tick_seconds", 10)))
                level_tick_count = max(0, int(wf_cfg.get("level_tick_count", 4)))
                baseline_width = max(1, int(wf_cfg.get("baseline_width", 2)))

                overlay_h = max(10, int(img.height * height_ratio))
                wave_top = img.height - overlay_h
                baseline_y = wave_top + overlay_h // 2

                # Prepare transparent overlay for alpha compositing
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                odraw = ImageDraw.Draw(overlay)
                # Semi-transparent background for the waveform strip
                odraw.rectangle([0, wave_top, img.width, img.height], fill=bg_rgba)

                drew_waveform = False
                audio_duration = None
                if audio_path and os.path.exists(audio_path):
                    audio = None
                    try:
                        audio = AudioFileClip(audio_path)
                        audio_duration = float(audio.duration or 0.0)
                        if audio_duration > 0:
                            width = img.width
                            # Sample amplitude at evenly spaced times across the track
                            amps = []
                            for x in range(width):
                                t = (x + 0.5) / width * audio_duration
                                try:
                                    sample = audio.get_frame(t)
                                    # sample can be scalar or array-like (channels)
                                    if hasattr(sample, '__len__'):
                                        val = sum(abs(float(s)) for s in sample) / max(1, len(sample))
                                    else:
                                        val = abs(float(sample))
                                    amps.append(val)
                                except Exception:
                                    amps.append(0.0)

                            # Scale amplitudes to fit overlay height (use robust max)
                            if any(a > 0 for a in amps):
                                srt = sorted(amps)
                                idx = int(0.95 * (len(srt) - 1)) if srt else 0
                                ref = srt[idx] if srt else 1.0
                                ref = max(ref, max(amps), 1e-6)
                                half_h = int(overlay_h * 0.45)
                                for x, a in enumerate(amps):
                                    dy = int(min(half_h, a / ref * half_h))
                                    odraw.line([(x, baseline_y - dy), (x, baseline_y + dy)], fill=wave_color)
                                drew_waveform = True
                    except Exception as e:
                        logger.warning("Waveform overlay failed", extra={"audio": audio_path, "error": str(e)})
                    finally:
                        try:
                            if audio is not None:
                                audio.close()
                        except Exception:
                            pass

                # If not drawn, draw a simple baseline
                if not drew_waveform:
                    odraw.line([(0, baseline_y), (img.width - 1, baseline_y)], fill=baseline_color, width=baseline_width)

                # Optional axes: time ticks and level ticks for better scale
                if show_axes:
                    # Time ticks (top edge of the strip)
                    # Prefer audio duration; if unavailable, try to approximate with video duration used earlier
                    dur_for_ticks = None
                    try:
                        # We don't have video duration stored; approximate from baseline position using image width vs audio duration
                        dur_for_ticks = audio_duration if audio_duration and audio_duration > 0 else None
                    except Exception:
                        pass
                    if dur_for_ticks and dur_for_ticks > 0:
                        tick_t = 0.0
                        while tick_t <= dur_for_ticks + 1e-6:
                            x = int((tick_t / dur_for_ticks) * (img.width - 1)) if dur_for_ticks > 0 else 0
                            odraw.line([(x, wave_top), (x, wave_top + max(3, overlay_h // 12))], fill=axes_color)
                            tick_t += time_tick_seconds
                    else:
                        # Draw a few evenly spaced ticks if duration unknown
                        for i in range(0, 6):
                            x = int(i / 5 * (img.width - 1))
                            odraw.line([(x, wave_top), (x, wave_top + max(3, overlay_h // 12))], fill=axes_color)

                    # Level ticks (horizontal faint lines)
                    if level_tick_count > 0:
                        half_h = int(overlay_h * 0.45)
                        for i in range(1, level_tick_count + 1):
                            frac = i / (level_tick_count + 1)
                            dy = int(frac * half_h)
                            # above baseline
                            odraw.line([(0, baseline_y - dy), (img.width - 1, baseline_y - dy)], fill=axes_color)
                            # below baseline
                            odraw.line([(0, baseline_y + dy), (img.width - 1, baseline_y + dy)], fill=axes_color)

                # Composite overlay onto image
                base_rgba = img.convert('RGBA')
                img = Image.alpha_composite(base_rgba, overlay).convert('RGB')
                logger.info("Thumbnail waveform overlay applied", extra={"audio": audio_path, "output": output_path})
            except Exception as e:
                logger.warning("Thumbnail overlay step failed", extra={"error": str(e), "output": output_path})

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        if img is None:
            console.print(f"[yellow]Warning: Could not extract frame for thumbnail from {video_path}[/]")
            logger.warning("Thumbnail extraction failed; no image frame", extra={"video": video_path})
            return
        img.save(output_path, format='JPEG', quality=90)
        console.print(f"[green]✓ Thumbnail created: {output_path}[/]")
        logger.info("Thumbnail created", extra={"output": output_path})
