"""
Utility functions for video generation.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple
import tempfile
import logging

logger = logging.getLogger("video.utils")

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def create_temp_dir(prefix: str = "ytlite_") -> Path:
    """Create a temporary directory.
    
    Args:
        prefix: Prefix for the temporary directory name
        
    Returns:
        Path to the created temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    logger.debug(f"Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_dir(temp_dir: Union[str, Path]) -> None:
    """Remove a temporary directory and its contents.
    
    Args:
        temp_dir: Path to the temporary directory
    """
    try:
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            logger.debug(f"Removed temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")

def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted time string (HH:MM:SS)
    """
    seconds = int(round(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in megabytes
    """
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except OSError:
        return 0.0

def validate_resolution(resolution: Union[tuple, list]) -> tuple:
    """Validate and normalize video resolution.
    
    Args:
        resolution: Resolution as (width, height)
        
    Returns:
        Normalized resolution as (width, height)
        
    Raises:
        ValueError: If resolution is invalid
    """
    if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
        raise ValueError("Resolution must be a tuple or list of (width, height)")
    
    width, height = map(int, resolution)
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers")
    
    # Ensure even dimensions (required by some codecs)
    width = width - (width % 2)
    height = height - (height % 2)
    
    return (width, height)
