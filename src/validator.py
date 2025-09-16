#!/usr/bin/env python3
"""
YTLite Video Validator Module - Refactored
Main entry point for all validation functionality
"""

import argparse
import sys
from rich.console import Console

from validation.video_validator import VideoValidator, validate_all_videos
from validation.app_validator import AppValidator
from validation.data_validator import DataValidator
from validation.report_generator import ReportGenerator

console = Console()

# Maintain backward compatibility by exposing classes at module level
VideoValidator = VideoValidator
Validator = AppValidator  # For backward compatibility


def main():
    """Main CLI entry point for validation commands"""
    parser = argparse.ArgumentParser(description='Validate YTLite data and app setup')
    parser.add_argument('command', choices=['validate_data', 'validate_app', 'validate_videos'], 
                       help='Command to execute')
    parser.add_argument('--detailed', action='store_true', help='Show detailed validation results')
    parser.add_argument('--content-dir', default='content', help='Content directory path')
    parser.add_argument('--video-dir', default='output/videos', help='Video directory path')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'validate_data':
            console.print("[bold blue]Running data validation...[/]")
            validator = DataValidator()
            summary, report_path = validator.validate_data(args.content_dir)
            console.print(f"[green]Data validation completed[/]")
            console.print(f"Report saved to: {report_path}")
            
        elif args.command == 'validate_app':
            console.print("[bold blue]Running app validation...[/]")
            validator = AppValidator()
            results = validator.validate_app(detailed=args.detailed)
            console.print(f"[green]App validation completed[/]")
            console.print(f"Report saved to: {results['report_path']}")
            
        elif args.command == 'validate_videos':
            console.print("[bold blue]Running video validation...[/]")
            report = validate_all_videos(
                video_dir=args.video_dir,
                content_dir=args.content_dir,
                detailed=args.detailed
            )
            console.print(f"[green]Video validation completed[/]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Validation interrupted by user[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Validation failed: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
