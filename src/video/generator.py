"""
Main video generation module.

Handles the orchestration of video creation from slides and audio.
"""
import os
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
import logging
import numpy as np

# Import MoviePy using explicit submodules for broad compatibility
try:
    from moviepy.editor import (
        VideoFileClip, ImageClip, TextClip, CompositeVideoClip, 
        concatenate_videoclips, AudioFileClip, ColorClip
    )
    from moviepy.video.tools.subtitles import SubtitlesClip
    from moviepy.video.VideoClip import TextClip
    from moviepy.config import change_settings
    
    # Ensure ImageMagick is available for text rendering
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            os.environ['IMAGEMAGICK_BINARY'] = ffmpeg_path
            change_settings({"IMAGEMAGICK_BINARY": ffmpeg_path})
    except Exception as e:
        logger.warning(f"Could not set ImageMagick binary: {e}")
        
except ImportError as e:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.VideoClip import ImageClip, TextClip, ColorClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.video.tools.subtitles import SubtitlesClip
    except ImportError as e:
        raise ImportError(
            "MoviePy is required for video generation. "
            "Install with: pip install moviepy"
        ) from e

# Import local modules
from .slides import SlideGenerator
from .themes import ThemeManager
from .fonts import FontManager
from .subtitles import create_srt_file

# Import local modules
from .slides import SlideGenerator
from .themes import ThemeManager
from .fonts import FontManager

logger = logging.getLogger("video.generator")

class VideoGenerator:
    """Main class for generating videos from slides and audio."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the video generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.resolution = tuple(self.config.get("resolution", [1280, 720]))
        self.fps = self.config.get("fps", 30)
        
        # Initialize components
        self.slide_generator = SlideGenerator(config)
        self.theme_manager = ThemeManager(config)
        self.font_manager = FontManager(config)
        
    def create_video(
        self,
        output_path: Union[str, Path],
        slides: List[Dict],
        audio_path: Optional[Union[str, Path]] = None,
        duration_per_slide: Optional[float] = None,
        transition_duration: float = 1.0,
        include_subtitles: bool = True,
        subtitle_font: Optional[str] = None,
        subtitle_font_size: int = 36,
        subtitle_color: str = 'white',
        subtitle_bg_color: str = 'black',
        subtitle_bg_opacity: float = 0.5,
        subtitle_position: str = 'bottom',
        subtitle_margin: int = 50
    ) -> str:
        """Create a video from slides and optional audio with optional subtitles.
        
        Args:
            output_path: Path to save the output video
            slides: List of slide definitions (dicts with 'text', 'theme', etc.)
            audio_path: Optional path to background audio
            duration_per_slide: Duration for each slide in seconds
            transition_duration: Duration of crossfade between slides
            include_subtitles: Whether to add subtitles to the video
            subtitle_font: Font family for subtitles
            subtitle_font_size: Font size for subtitles
            subtitle_color: Text color for subtitles
            subtitle_bg_color: Background color for subtitles
            subtitle_bg_opacity: Opacity of subtitle background (0.0 to 1.0)
            subtitle_position: Position of subtitles ('top', 'center', 'bottom')
            subtitle_margin: Margin from the edge of the video in pixels
            
        Returns:
            Path to the generated video file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating video with {len(slides)} slides: {output_path}")
        logger.debug(f"Subtitle settings - enabled: {include_subtitles}, font: {subtitle_font}, size: {subtitle_font_size}")
        
        # Generate slide images and collect text for subtitles
        slide_images = []
        slide_texts = []
        
        for i, slide_def in enumerate(slides):
            logger.debug(f"Generating slide {i+1}/{len(slides)}")
            try:
                # Make a copy to avoid modifying the original
                slide_def = slide_def.copy()
                
                # Extract text for subtitles
                slide_text = slide_def.get('text', '')
                if slide_text:
                    slide_texts.append({
                        'text': slide_text,
                        'start': i * (duration_per_slide or self.config.get("default_slide_duration", 5.0)),
                        'end': (i + 1) * (duration_per_slide or self.config.get("default_slide_duration", 5.0))
                    })
                
                # Generate slide image
                slide_img = self.slide_generator.create_slide(**slide_def)
                slide_images.append(slide_img)
            except Exception as e:
                logger.error(f"Failed to generate slide {i+1}: {e}")
                raise
        
        # Create video clips from images
        video_clips = []
        for i, img in enumerate(slide_images):
            # Create image clip with specified duration or calculate from audio
            duration = (
                duration_per_slide or 
                self.config.get("default_slide_duration", 5.0)
            )
            
            # Convert PIL Image to numpy array if needed
            if hasattr(img, 'convert'):  # Check if it's a PIL Image
                img = np.array(img)
                
            clip = ImageClip(img).set_duration(duration)
            
            # Add crossfade transition
            if i > 0 and transition_duration > 0:
                clip = clip.crossfadein(transition_duration)
            
            video_clips.append(clip)
        
        # Concatenate all clips with transitions
        if len(video_clips) == 0:
            raise ValueError("No video clips were created")
            
        # Create the base video clip
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(str(audio_path))
                
                # Trim audio to match video duration if needed
                if audio_clip.duration > final_clip.duration:
                    audio_clip = audio_clip.subclip(0, final_clip.duration)
                
                final_clip = final_clip.set_audio(audio_clip)
            except Exception as e:
                logger.warning(f"Failed to add audio: {e}")
        
        # Add subtitles if enabled and we have text
        if include_subtitles and slide_texts:
            try:
                logger.info("Adding subtitles to video")
                
                # Create a temporary directory for subtitle files
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir = Path(temp_dir)
                    srt_path = temp_dir / 'subtitles.srt'
                    
                    # Create SRT file
                    create_srt_file(slide_texts, srt_path)
                    
                    # Create subtitle clip
                    def make_text(txt):
                        """Helper function to create styled text for subtitles."""
                        return TextClip(
                            txt,
                            font=subtitle_font,
                            fontsize=subtitle_font_size,
                            color=subtitle_color,
                            stroke_color='black',
                            stroke_width=1,
                            method='caption',
                            align='center',
                            size=(final_clip.w * 0.9, None)
                        )
                    
                    # Generate subtitle clip
                    subtitles = SubtitlesClip(
                        str(srt_path),
                        make_text
                    )
                    
                    # Position subtitles
                    if subtitle_position == 'top':
                        subtitles = subtitles.set_position(('center', subtitle_margin))
                    elif subtitle_position == 'center':
                        subtitles = subtitles.set_position('center')
                    else:  # bottom (default)
                        subtitles = subtitles.set_position(('center', final_clip.h - subtitle_margin - 50))
                    
                    # Add semi-transparent background to subtitles for better readability
                    if subtitle_bg_opacity > 0:
                        def add_bg(clip):
                            txt = clip.get_frame(0)
                            h, w = txt.shape[:2]
                            bg = ColorClip(
                                size=(w + 20, h + 10),
                                color=[int(c * 255) for c in ColorClip.color_str_to_array(subtitle_bg_color)]
                            ).set_opacity(subtitle_bg_opacity)
                            
                            # Center the text on the background
                            txt_clip = clip.set_position(('center', 'center'))
                            return CompositeVideoClip([bg, txt_clip])
                        
                        subtitles = subtitles.fl(add_bg)
                    
                    # Set the duration of the subtitles to match the video
                    subtitles = subtitles.set_duration(final_clip.duration)
                    
                    # Composite the subtitles on top of the video
                    final_clip = CompositeVideoClip([final_clip, subtitles])
                    
            except Exception as e:
                logger.error(f"Failed to add subtitles: {e}", exc_info=True)
        
        # Write the final video file
        logger.info(f"Writing video to {output_path}")
        temp_output = str(output_path).replace('.mp4', '_temp.mp4')
        
        try:
            final_clip.write_videofile(
                temp_output,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(Path(temp_output).with_suffix('.tmp.m4a')),
                remove_temp=True,
                threads=4,
                preset='medium',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',  # Better compatibility
                    '-movflags', '+faststart'  # For web streaming
                ]
            )
            
            # Replace the original file with the new one
            if os.path.exists(temp_output):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_output, output_path)
                
        except Exception as e:
            logger.error(f"Error writing video file: {e}", exc_info=True)
            if os.path.exists(temp_output):
                os.remove(temp_output)
            raise
        
        # Close clips to free resources
        final_clip.close()
        if 'audio_clip' in locals():
            audio_clip.close()
        
        return str(output_path)
    
    def generate_from_markdown(
        self,
        markdown_content: str,
        output_dir: Union[str, Path],
        audio_path: Optional[Union[str, Path]] = None,
        theme: str = "tech",
        **kwargs
    ) -> Dict[str, str]:
        """Generate a video from markdown content.
        
        Args:
            markdown_content: Markdown text to convert to slides
            output_dir: Directory to save output files
            audio_path: Optional path to background audio
            theme: Theme to use for the slides
            **kwargs: Additional arguments to pass to create_video
            
        Returns:
            Dictionary with paths to generated files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse markdown into slides (simple split by ---)
        slide_texts = [s.strip() for s in markdown_content.split('---') if s.strip()]
        
        # Create slide definitions
        slides = [
            {
                'text': text,
                'theme': theme,
                'template': 'classic',
                'font_size': self.config.get('font_size', 48)
            }
            for text in slide_texts
        ]
        
        # Generate output filename
        timestamp = int(time.time())
        video_path = output_dir / f"output_{timestamp}.mp4"
        
        # Create the video
        self.create_video(
            output_path=video_path,
            slides=slides,
            audio_path=audio_path,
            **kwargs
        )
        
        return {
            'video': str(video_path),
            'slides': [str(output_dir / f"slide_{i:03d}.png") for i in range(len(slides))]
        }
