"""
Subtitle generation for videos.

Handles the creation and management of subtitle files.
"""
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path
import logging
import os

logger = logging.getLogger("video.subtitles")

def create_srt_file(
    subtitles: List[Dict[str, Union[str, float]]],
    output_path: Union[str, Path],
    encoding: str = 'utf-8'
) -> str:
    """Create an SRT subtitle file from a list of subtitle entries.
    
    Args:
        subtitles: List of subtitle dictionaries with 'start', 'end', and 'text' keys
        output_path: Path to save the SRT file
        encoding: File encoding to use
        
    Returns:
        Path to the created SRT file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    srt_content = []
    for i, sub in enumerate(subtitles, 1):
        start = _format_srt_timestamp(sub['start'])
        end = _format_srt_timestamp(sub['end'])
        text = sub['text'].strip()
        
        srt_content.append(f"{i}\n{start} --> {end}\n{text}\n")
    
    with open(output_path, 'w', encoding=encoding) as f:
        f.write('\n'.join(srt_content))
    
    logger.info(f"Created SRT file with {len(subtitles)} entries: {output_path}")
    return str(output_path)

def _format_srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
