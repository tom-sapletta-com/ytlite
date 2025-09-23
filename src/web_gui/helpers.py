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
            # publish_mqtt_event(
            #     'postgen_audio_silence' if ares.get('silent') else 'postgen_audio_ok',
            #     'error' if ares.get('silent') else 'info',
            #     project_name,
            #     {'check': ares},
            #     tags=['postgen', 'media']
            # )
            # publish_mqtt_event(
            #     'postgen_video_silence' if (vres.get('silent') or not vres.get('has_audio')) else 'postgen_video_ok',
            #     'error' if (vres.get('silent') or not vres.get('has_audio')) else 'info',
            #     project_name,
            #     {'check': vres},
            #     tags=['postgen', 'media']
            # )
        except Exception as _e:
            logger.warning(f"Media validation publish failed for {project_name}: {_e}")

        return True, generated_files, ""

    except Exception as e:
        logger.error(f"Error generating media for {project_name}: {e}")
        return False, [], str(e)

def detect_changes_and_get_regeneration_flags(project_name: str, markdown_content: str, config_overrides: Optional[dict] = None) -> Dict[str, bool]:
    """Detect what changed and determine what needs regeneration."""
    import os
    import json
    from pathlib import Path
    
    # Paths to check previous state
    project_dir = Path('content') / project_name
    metadata_file = project_dir / 'metadata.json'
    
    regeneration_flags = {
        'audio': False,
        'video': False, 
        'slides': False
    }
    
    # If no previous metadata exists, regenerate everything
    if not metadata_file.exists():
        logger.info(f"No metadata found for {project_name} - will regenerate all assets")
        return {'audio': True, 'video': True, 'slides': True}
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            previous_metadata = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read metadata for {project_name}: {str(e)}")
        # If can't read metadata, regenerate everything
        return {'audio': True, 'video': True, 'slides': True}
    
    # Compare content (affects audio + video)
    previous_content = previous_metadata.get('content', '')
    if markdown_content.strip() != previous_content.strip():
        regeneration_flags['audio'] = True
        regeneration_flags['video'] = True  # Video depends on audio
        logger.info(f"Content changed for {project_name} - will regenerate audio and video")
    
    # Compare visual settings (affects slides + video only)
    config_overrides = config_overrides or {}
    previous_config = previous_metadata.get('config', {})
    
    visual_fields = ['font_size', 'theme', 'template', 'font_family']
    visual_changed = False
    
    for field in visual_fields:
        if config_overrides.get(field) != previous_config.get(field):
            visual_changed = True
            logger.info(f"Visual setting '{field}' changed for {project_name}")
            # If font size changes, we need to regenerate both slides and video
            if field == 'font_size':
                logger.info(f"Font size changed - will regenerate slides and video for {project_name}")
                regeneration_flags['slides'] = True
                regeneration_flags['video'] = True
            break
            
    if visual_changed and not regeneration_flags['slides']:  # If not already handled by font_size
        regeneration_flags['slides'] = True
        regeneration_flags['video'] = True  # Video needs slides
    
    # Compare voice settings (affects audio + video)
    voice_fields = ['voice', 'language']
    voice_changed = False
    
    for field in voice_fields:
        if config_overrides.get(field) != previous_config.get(field):
            voice_changed = True
            logger.info(f"Voice setting '{field}' changed for {project_name}")
            break
            
    if voice_changed:
        regeneration_flags['audio'] = True
        regeneration_flags['video'] = True  # Video depends on audio
        
    # If audio needs regeneration, force video regeneration as well
    if regeneration_flags['audio'] and not regeneration_flags['video']:
        logger.info(f"Audio needs regeneration for {project_name}, will also regenerate video")
        regeneration_flags['video'] = True
    
    return regeneration_flags

def save_project_metadata(project_name: str, markdown_content: str, config_overrides: Optional[dict] = None):
    """Save current project metadata for future comparison."""
    import json
    from pathlib import Path
    from datetime import datetime
    
    try:
        project_dir = Path('content') / project_name
        logger.info(f"Ensuring project directory exists: {project_dir}")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save markdown content
        md_path = project_dir / 'content.md'
        logger.info(f"Saving markdown content to: {md_path}")
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.debug(f"Successfully saved {len(markdown_content)} characters to {md_path}")
        except Exception as e:
            logger.error(f"Failed to save markdown content: {str(e)}")
            return {'success': False, 'error': f'Failed to save markdown: {str(e)}'}
        
        # Prepare metadata
        metadata = {
            'content': markdown_content,
            'config': config_overrides or {},
            'last_updated': datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_file = project_dir / 'metadata.json'
        logger.info(f"Saving metadata to: {metadata_file}")
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully saved metadata to {metadata_file}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
            return {'success': False, 'error': f'Failed to save metadata: {str(e)}'}
            
    except Exception as e:
        logger.error(f"Error in save_project_metadata: {str(e)}")
        logger.exception("Error details:")
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

def run_ytlite_generation(project_name: str, markdown_content: str, force_regenerate: bool = False, config_overrides: Optional[dict] = None) -> dict:
    """Run YTLite generation process with intelligent regeneration."""
    from ytlite_main import YTLite
    import os
    import json
    from pathlib import Path
    
    logger.info(f"Starting YTLite generation for project: {project_name}")
    logger.debug(f"Force regenerate: {force_regenerate}")
    logger.debug(f"Config overrides: {config_overrides}")
    
    # Initialize config_overrides if None
    if config_overrides is None:
        config_overrides = {}
    
    # Process font size if provided
    if 'font_size' in config_overrides:
        font_size = config_overrides['font_size']
        # Handle string font sizes by mapping them to numeric values
        if isinstance(font_size, str):
            font_size_map = {
                'small': 24,
                'medium': 48, 
                'large': 72,
                'xl': 96
            }
            config_overrides['font_size'] = font_size_map.get(font_size.lower(), 48)  # default to medium
        else:
            config_overrides['font_size'] = int(font_size)
    
    # Process subtitle settings if provided
    subtitle_settings = {}
    if 'include_subtitles' in config_overrides:
        subtitle_settings['enabled'] = config_overrides.pop('include_subtitles') in (True, 'true', '1', 1)
        
    # Add other subtitle settings if they exist
    for setting in ['subtitle_font', 'subtitle_font_size', 'subtitle_color', 
                   'subtitle_bg_color', 'subtitle_bg_opacity', 'subtitle_position', 
                   'subtitle_margin']:
        if setting in config_overrides:
            subtitle_settings[setting] = config_overrides.pop(setting)
    
    # If we have any subtitle settings, add them to config_overrides
    if subtitle_settings:
        # Convert the settings to the format expected by the video generator
        config_overrides.update({
            'include_subtitles': subtitle_settings.get('enabled', False),
            'subtitle_font': subtitle_settings.get('subtitle_font', 'Arial'),
            'subtitle_font_size': int(subtitle_settings.get('subtitle_font_size', 36)),
            'subtitle_color': subtitle_settings.get('subtitle_color', 'white'),
            'subtitle_bg_color': subtitle_settings.get('subtitle_bg_color', 'black'),
            'subtitle_bg_opacity': float(subtitle_settings.get('subtitle_bg_opacity', 0.5)),
            'subtitle_position': subtitle_settings.get('subtitle_position', 'bottom'),
            'subtitle_margin': int(subtitle_settings.get('subtitle_margin', 50))
        })
    
    # If not forcing regeneration, use intelligent detection
    logger.info("Checking if regeneration is needed")
    try:
        regeneration_flags = detect_changes_and_get_regeneration_flags(
            project_name, markdown_content, config_overrides
        )
        logger.debug(f"Regeneration flags: {regeneration_flags}")
        
        if force_regenerate:
            logger.info("Force regeneration requested, setting all flags to True")
            for key in regeneration_flags:
                regeneration_flags[key] = True
    except Exception as e:
        logger.error(f"Error checking for changes: {str(e)}")
        logger.exception("Change detection error:")
        return {'success': False, 'error': f'Change detection failed: {str(e)}'}
    
    # If nothing changed, skip generation
    if not any(regeneration_flags.values()):
        logger.info(f"No changes detected for {project_name} - skipping regeneration")
        return {"success": True, "status": "skipped", "reason": "no_changes"}
        
    # Apply selective regeneration
    config_overrides['regenerate_audio'] = regeneration_flags['audio']
    config_overrides['regenerate_video'] = regeneration_flags['video'] 
    config_overrides['regenerate_slides'] = regeneration_flags['slides']
        
    logger.info(f"Selective regeneration for {project_name}: audio={regeneration_flags['audio']}, video={regeneration_flags['video']}, slides={regeneration_flags['slides']}")
    
    # Initialize YTLite with config overrides
    logger.info("Initializing YTLite with config overrides")
    try:
        output_dir = str(Path('output').resolve())
        
        # Initialize YTLite with required parameters
        yt = YTLite(
            output_dir=output_dir,
            project_name=project_name,
            config_overrides=config_overrides or {}
        )
        logger.debug("YTLite initialized successfully")
    except Exception as e:
        error_msg = f"Failed to initialize YTLite: {str(e)}"
        logger.error(error_msg)
        logger.exception("YTLite initialization error:")
        return {'success': False, 'error': error_msg}
    
    try:
        logger.info(f"Running YTLite generation for project: {project_name}")
        result = yt.run_from_content(markdown_content, project_name, force_regenerate)
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {'success': True, 'result': result}
            
        # Save metadata for future comparisons if generation was successful
        if result.get('success', False):
            save_project_metadata(project_name, markdown_content, config_overrides)
        
        return result
        
    except Exception as e:
        error_msg = f"YTLite generation failed: {str(e)}"
        logger.error(error_msg)
        logger.exception("Generation error details:")
        return {'success': False, 'error': error_msg}

def create_svg_project(project_name: str, content: str, metadata: Dict[str, Any] = None,
                      output_path: Path = None, force_regenerate: bool = False, config_overrides: Optional[dict] = None) -> dict:
    """
    Create a single SVG project file with embedded media.
    
    Returns:
        dict: A dictionary with 'success' key indicating success/failure, and additional
              information like 'path' on success or 'error' on failure.
    """
    from svg_datauri_packager import SVGDataURIPackager
    import shutil

    logger.info(f"Starting SVG project creation for {project_name}")
    logger.debug(f"Content length: {len(content)} characters")
    logger.debug(f"Metadata: {metadata}")
    logger.debug(f"Force regenerate: {force_regenerate}")
    logger.debug(f"Config overrides: {config_overrides}")
    
    # Set default output path if not provided
    if output_path is None:
        output_path = Path('output/svg_projects') / f"{project_name}.svg"
    output_path = Path(output_path)  # Ensure it's a Path object
    
    output_dir = output_path.parent if output_path else Path('output')
    logger.info(f"Ensuring output directory exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if metadata is None:
        metadata = {}

    try:
        # Run YTLite generation process, passing the specific overrides
        logger.info(f"Running YTLite generation for {project_name}")
        ytlite_result = run_ytlite_generation(project_name, content, force_regenerate, config_overrides)

        if not ytlite_result.get('success'):
            error_msg = ytlite_result.get('error', 'Unknown error during YTLite generation')
            logger.error(f"YTLite generation failed for {project_name}: {error_msg}")
            return {'success': False, 'error': error_msg, 'step': 'ytlite_generation'}
            
        logger.info(f"YTLite generation completed successfully for {project_name}")
        logger.debug(f"YTLite result: {ytlite_result}")

        # Resolve centralized output directories
        base_output_dir = output_dir.parent
        videos_dir = base_output_dir / 'videos'
        audio_dir = base_output_dir / 'audio'
        thumbs_dir = base_output_dir / 'thumbnails'
        project_dir = base_output_dir / 'projects' / project_name

        # Resolve paths to generated files (prefer centralized dirs, fallback to project dir)
        video_path = videos_dir / f"{project_name}.mp4"
        if not video_path.exists():
            video_path = project_dir / f"{project_name}.mp4"
            
        audio_path = audio_dir / f"{project_name}.mp3"
        if not audio_path.exists():
            audio_path = project_dir / f"{project_name}.mp3"
            
        thumb_path = thumbs_dir / f"{project_name}.jpg"
        if not thumb_path.exists():
            thumb_path = project_dir / f"{project_name}.jpg"
        
        # Check if all required files exist
        missing_files = []
        for path, name in [
            (video_path, 'video'),
            (audio_path, 'audio'),
            (thumb_path, 'thumbnail')
        ]:
            if not path.exists():
                missing_files.append((name, str(path)))
                logger.warning(f"Required {name} file not found: {path}")
        
        if missing_files:
            missing_list = ", ".join(f"{name} ({path})" for name, path in missing_files)
            error_msg = f"Required files not found: {missing_list}"
            logger.error(error_msg)
            return {
                'success': False, 
                'error': error_msg, 
                'missing_files': missing_files,
                'step': 'file_validation'
            }

        # If YTLite already produced a packaged SVG in the project directory, reuse it
        packaged_svg = project_dir / f"{project_name}.svg"
        if packaged_svg.exists():
            try:
                logger.info(f"Found existing packaged SVG at {packaged_svg}, copying to {output_path}")
                shutil.copyfile(str(packaged_svg), str(output_path))
                logger.info(f"Successfully copied packaged SVG to {output_path}")
                return {
                    'success': True, 
                    'path': str(output_path),
                    'source': 'existing_package'
                }
            except Exception as copy_err:
                logger.warning(f"Failed to copy packaged SVG, will repackage: {str(copy_err)}")

        # Create packager and generate SVG
        logger.info(f"Creating new SVG project for {project_name}")
        try:
            packager = SVGDataURIPackager()
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate SVG content
            logger.debug(f"Generating SVG with video: {video_path}, audio: {audio_path}, thumbnail: {thumb_path}")
            svg_content = packager.create_svg_project(
                project_name,
                metadata or {},
                str(video_path.absolute()),
                str(audio_path.absolute()),
                str(thumb_path.absolute())
            )

            # Save SVG file
            logger.info(f"Saving SVG to {output_path}")
            output_path.write_text(svg_content, encoding='utf-8')

            logger.info(f"Successfully created SVG project at {output_path}")
            return {
                'success': True, 
                'path': str(output_path),
                'source': 'new_generation'
            }
            
        except Exception as svg_err:
            error_msg = f"Failed to generate SVG: {str(svg_err)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False, 
                'error': error_msg,
                'step': 'svg_generation'
            }

    except Exception as e:
        error_msg = f"Unexpected error during SVG project creation for {project_name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'success': False, 
            'error': error_msg,
            'step': 'unexpected_error'
        }
