#!/usr/bin/env python3
"""
Helper functions for the Web GUI to avoid circular dependencies.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import shutil

from logging_setup import get_logger
from media_validator import check_audio_silence, check_video_audio_silence
from mqtt_client import publish_mqtt_event

logger = get_logger("web_gui.helpers")

def generate_missing_media(project_name: str, output_dir: Path) -> tuple[bool, list[str], str]:
    """Generate audio, video, and thumbnail if they don't exist."""
    from ytlite_main import YTLite

    project_dir = output_dir / 'projects' / project_name
    if not project_dir.exists():
        return False, [], f"Project directory {project_dir} not found."

    # Prefer existing description.md, otherwise fallback to project_name.md
    md_file = project_dir / 'description.md'
    if not md_file.exists():
        md_file = project_dir / f"{project_name}.md"

    if not md_file.exists():
        return False, [], f"No markdown file found in {project_dir}."

    generated_files: list[str] = []
    try:
        ytlite = YTLite(output_dir=str(output_dir), project_name=project_name)
        ytlite.generate_video(str(md_file))

        audio_path = output_dir / 'audio' / f"{project_name}.mp3"
        if not audio_path.exists():
            alt_wav = output_dir / 'audio' / f"{project_name}.wav"
            if alt_wav.exists():
                audio_path = alt_wav
        video_path = output_dir / 'videos' / f"{project_name}.mp4"
        thumb_path = output_dir / 'thumbnails' / f"{project_name}.jpg"

        if audio_path.exists():
            generated_files.append(str(audio_path))
        if video_path.exists():
            generated_files.append(str(video_path))
        if thumb_path.exists():
            generated_files.append(str(thumb_path))

        # Validate media loudness and publish MQTT notifications
        try:
            ares = check_audio_silence(audio_path)
            vres = check_video_audio_silence(video_path)
            publish_mqtt_event(
                'postgen_audio_silence' if ares.get('silent') else 'postgen_audio_ok',
                'error' if ares.get('silent') else 'info',
                project_name,
                {'check': ares},
                tags=['postgen', 'media']
            )
            publish_mqtt_event(
                'postgen_video_silence' if (vres.get('silent') or not vres.get('has_audio')) else 'postgen_video_ok',
                'error' if (vres.get('silent') or not vres.get('has_audio')) else 'info',
                project_name,
                {'check': vres},
                tags=['postgen', 'media']
            )
        except Exception as _e:
            logger.warning(f"Media validation publish failed for {project_name}: {_e}")

        return True, generated_files, ""

    except Exception as e:
        logger.error(f"Error generating media for {project_name}: {e}")
        return False, [], str(e)

def create_svg_project(project_name: str, content: str, metadata: Dict[str, Any] = None,
                      output_path: Path = None, force_regenerate: bool = False) -> Optional[Path]:
    """Create a single SVG project file with embedded media."""
    
    from ytlite_main import YTLite
    from svg_datauri_packager import SVGDataURIPackager

    if output_path is None:
        output_path = Path('output/svg_projects') / f"{project_name}.svg"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if metadata is None:
        metadata = {}

    try:
        # Use YTLite to generate the necessary files from content
        logger.info(f"Running YTLite to generate media for {project_name}")
        if force_regenerate:
            logger.info(f"Force regenerate enabled for {project_name}. Deleting existing media.")
            # Correctly reference the base 'output' directory from the svg_projects path
            base_output_dir = output_path.parent.parent 
            media_files = [
                base_output_dir / 'audio' / f"{project_name}.mp3",
                base_output_dir / 'videos' / f"{project_name}.mp4",
                base_output_dir / 'thumbnails' / f"{project_name}.jpg"
            ]
            for f in media_files:
                if f.exists():
                    try:
                        f.unlink()
                        logger.info(f"Deleted {f}")
                    except OSError as e:
                        logger.error(f"Error deleting {f}: {e}")

        ytlite = YTLite(output_dir=str(output_path.parent.parent), project_name=project_name)
        
        # Create a temporary markdown file for YTLite to process
        project_dir = output_path.parent.parent / 'projects' / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        md_file = project_dir / f"{project_name}.md"
        md_file.write_text(content, encoding='utf-8')

        # Generate the video and audio
        ytlite.generate_video(str(md_file))
        
        # Resolve centralized output directories
        base_output_dir = output_path.parent.parent
        videos_dir = base_output_dir / 'videos'
        audio_dir = base_output_dir / 'audio'
        thumbs_dir = base_output_dir / 'thumbnails'

        # Resolve paths to generated files (prefer centralized dirs, fallback to project dir)
        video_path = videos_dir / f"{project_name}.mp4"
        if not video_path.exists():
            video_path = project_dir / f"{project_name}.mp4"

        audio_path = audio_dir / f"{project_name}.mp3"
        if not audio_path.exists():
            audio_path = project_dir / f"{project_name}.mp3"
        if not audio_path.exists():
            # WAV fallbacks
            ap = output_dir / 'audio' / f"{project_name}.wav"
            if ap.exists():
                audio_path = ap
            else:
                ap2 = project_dir / f"{project_name}.wav"
                if ap2.exists():
                    audio_path = ap2

        thumbnail_path = thumbs_dir / f"{project_name}.jpg"
        if not thumbnail_path.exists():
            thumbnail_path = project_dir / 'thumbnail.jpg'

        if not video_path.exists():
            logger.error(f"Video file not generated for {project_name} at {video_path}")
            return None

        # Validate audio/video and publish MQTT notifications
        try:
            ares = check_audio_silence(audio_path)
            vres = check_video_audio_silence(video_path)
            publish_mqtt_event(
                'postgen_audio_silence' if ares.get('silent') else 'postgen_audio_ok',
                'error' if ares.get('silent') else 'info',
                project_name,
                {'check': ares},
                tags=['postgen', 'media']
            )
            publish_mqtt_event(
                'postgen_video_silence' if (vres.get('silent') or not vres.get('has_audio')) else 'postgen_video_ok',
                'error' if (vres.get('silent') or not vres.get('has_audio')) else 'info',
                project_name,
                {'check': vres},
                tags=['postgen', 'media']
            )
        except Exception as _e:
            logger.warning(f"Media validation failed for {project_name}: {_e}")

        # If YTLite already produced a packaged SVG in the project directory, reuse it
        packaged_svg = project_dir / f"{project_name}.svg"
        if packaged_svg.exists():
            try:
                shutil.copyfile(str(packaged_svg), str(output_path))
                logger.info(f"Copied packaged SVG to {output_path}")
                return output_path
            except Exception as copy_err:
                logger.warning(f"Failed to copy packaged SVG, will repackage: {copy_err}")

        # Create packager and generate SVG
        packager = SVGDataURIPackager()
        svg_content = packager.create_svg_project(
            project_name,
            metadata,
            video_path,
            audio_path if audio_path.exists() else None,
            thumbnail_path if thumbnail_path.exists() else None,
        )

        # Save SVG file
        output_path.write_text(svg_content, encoding='utf-8')

        logger.info(f"Created SVG project: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed during SVG project creation for {project_name}: {e}", exc_info=True)
        return None
