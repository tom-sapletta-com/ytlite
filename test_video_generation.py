#!/usr/bin/env python3
"""
Test script to verify video generation functionality
"""
import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Set up detailed logging
log_file = Path("test_video_generation.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ytlite_main import YTLite
except ImportError as e:
    logger.error("Failed to import YTLite. Make sure you're in the project root directory.")
    logger.error(traceback.format_exc())
    sys.exit(1)

from rich.console import Console

console = Console()
console.print(f"[yellow]Logging to {log_file.absolute()}[/yellow]")

def test_video_generation():
    """Test video generation with a simple markdown file."""
    try:
        # Create a test output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple markdown file
        test_md = output_dir / "test_video.md"
        test_content = """---
title: Test Video
description: A test video
---

# Test Video

This is a test video generation.
"""
        test_md.write_text(test_content)
        logger.info(f"Created test markdown file at {test_md}")
        
        # Initialize YTLite with debug logging
        logger.info("Initializing YTLite...")
        ytlite = YTLite(output_dir=str(output_dir))
        
        # Check if required directories exist
        required_dirs = [
            output_dir / "audio",
            output_dir / "videos",
            output_dir / "thumbnails"
        ]
        
        for d in required_dirs:
            d.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {d}")
        
        # Generate video
        console.print("[cyan]Generating video...[/]")
        logger.info(f"Starting video generation for {test_md}")
        
        try:
            ytlite.generate_video(str(test_md))
            logger.info("Video generation completed")
        except Exception as e:
            logger.error(f"Error during video generation: {e}")
            logger.error(traceback.format_exc())
            raise
        
        # Check if video was created
        video_path = output_dir / "videos" / "test_video.mp4"
        if video_path.exists():
            size_mb = video_path.stat().st_size / (1024 * 1024)
            console.print(f"[green]✓ Video generated successfully: {video_path}[/]")
            console.print(f"[blue]File size: {size_mb:.2f} MB[/]")
            logger.info(f"Video generated successfully at {video_path} (Size: {size_mb:.2f} MB)")
            return True
        else:
            console.print("[red]✗ Video file was not created[/]")
            logger.error("Video file was not created")
            
            # Check for partial files
            for dir_type in ["audio", "videos", "thumbnails"]:
                check_dir = output_dir / dir_type
                if check_dir.exists():
                    files = list(check_dir.glob("*"))
                    if files:
                        console.print(f"\nFiles in {dir_type} directory:")
                        logger.info(f"Files in {check_dir}:")
                        for f in files:
                            size = f.stat().st_size
                            console.print(f"  - {f.name} ({size} bytes)")
                            logger.info(f"  - {f.name} ({size} bytes)")
            
            return False
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        import traceback
        console.print(traceback.format_exc())
        return False

if __name__ == "__main__":
    start_time = datetime.now()
    console.rule("[bold blue]Starting Video Generation Test")
    logger.info(f"Starting test at {start_time}")
    
    try:
        success = test_video_generation()
        test_status = "PASSED" if success else "FAILED"
        console.print(f"\n[bold]{'='*50}[/]")
        console.print(f"[bold]Test {test_status}![/]")
        console.print(f"[dim]Log file: {log_file.absolute()}")
        console.print(f"[dim]Duration: {datetime.now() - start_time}")
        console.print(f"[dim]{'='*50}[/]")
        
        if not success:
            console.print("\n[bold yellow]Troubleshooting Tips:[/]")
            console.print("1. Check if FFmpeg is installed and in your PATH")
            console.print("2. Verify that all required Python packages are installed")
            console.print("3. Check the log file for detailed error messages")
            console.print("4. Try running with sudo if you encounter permission issues")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        console.print(f"\n[bold red]CRITICAL ERROR: {e}")
        console.print("\nCheck the log file for full traceback.")
        console.print(f"[dim]Log file: {log_file.absolute()}")
        sys.exit(1)
