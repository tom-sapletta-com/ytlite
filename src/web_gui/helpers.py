#!/usr/bin/env python3
"""
Helper functions for the Web GUI to avoid circular dependencies.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from logging_setup import get_logger

logger = get_logger("web_gui.helpers")

def create_svg_project(project_name: str, content: str, metadata: Dict[str, Any] = None,
                      output_path: Path = None) -> Optional[Path]:
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
        ytlite = YTLite(output_dir=str(output_path.parent.parent), project_name=project_name)
        
        # Create a temporary markdown file for YTLite to process
        project_dir = output_path.parent.parent / 'projects' / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        md_file = project_dir / f"{project_name}.md"
        md_file.write_text(content, encoding='utf-8')

        # Generate the video and audio
        ytlite.generate_video(str(md_file))
        
        # Define paths to generated files
        video_path = project_dir / f"{project_name}.mp4"
        audio_path = project_dir / f"{project_name}.mp3"
        thumbnail_path = project_dir / 'thumbnail.jpg'

        if not video_path.exists():
            logger.error(f"Video file not generated for {project_name} at {video_path}")
            return None

        # Create packager and generate SVG
        packager = SVGDataURIPackager()
        svg_content = packager.create_svg_project(
            project_name, metadata, video_path, audio_path, 
            thumbnail_path if thumbnail_path.exists() else None
        )
        
        # Save SVG file
        output_path.write_text(svg_content, encoding='utf-8')
        
        logger.info(f"Created SVG project: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed during SVG project creation for {project_name}: {e}", exc_info=True)
        return None
