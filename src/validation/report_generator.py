#!/usr/bin/env python3
"""
Report Generation Module for YTLite Validation
Handles generating and displaying validation reports
"""

import json
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.table import Table

console = Console()


class ReportGenerator:
    def generate_report(self, results: List[Dict], output_path: str = "output/validation_report.txt", detailed: bool = False):
        """Generate comprehensive validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_videos": len(results),
            "passed": sum(1 for r in results if r.get("status") == "passed"),
            "failed": sum(1 for r in results if r.get("status", "").startswith("failed")),
            "warnings": sum(1 for r in results if "warning" in r.get("status", "")),
            "errors": sum(1 for r in results if r.get("status") == "error"),
            "results": results,
            "detailed": detailed
        }
        
        # Ensure all values in results are JSON serializable with a comprehensive recursive function
        def make_serializable(obj):
            if isinstance(obj, (bool, int, float, str, type(None))):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: make_serializable(value) for key, value in obj.items()}
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                return str(obj)
        
        report = make_serializable(report)
        
        # Save to file
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            console.print(f"[green]Report saved to {output_path}[/]")
        except Exception as e:
            console.print(f"[red]Failed to save report: {e}[/]")
        
        # Display summary
        self._display_summary_table(report)
        
        # Display detailed results if requested
        if detailed:
            for result in results:
                console.print(f"\n[bold cyan]Video: {result.get('video_path', 'Unknown')}[/]")
                console.print(f"Status: {result.get('status', 'Unknown')}")
                
                if "properties" in result:
                    props = result["properties"]
                    console.print(f"Duration: {props.get('duration', 'Unknown')}s")
                    console.print(f"FPS: {props.get('fps', 'Unknown')}")
                    console.print(f"Size: {props.get('size', 'Unknown')}")
                    console.print(f"Has Audio: {props.get('has_audio', 'Unknown')}")
                
                if "transcription" in result and "text" in result["transcription"]:
                    text = result["transcription"]["text"][:100] + "..." if len(result["transcription"]["text"]) > 100 else result["transcription"]["text"]
                    console.print(f"Transcription: {text}")
                
                if "quality" in result:
                    quality = result["quality"]
                    console.print(f"Quality Grade: {quality.get('grade', 'Unknown')}")
        
        return report
    
    def _display_summary_table(self, report: Dict):
        """Display validation results in a table"""
        table = Table(title="Video Validation Report")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Percentage", justify="right", style="green")
        
        total = report["total_videos"]
        if total > 0:
            table.add_row("Total Videos", str(total), "100%")
            table.add_row("Passed", str(report["passed"]), f"{report['passed']/total*100:.1f}%")
            table.add_row("Failed", str(report["failed"]), f"{report['failed']/total*100:.1f}%")
            table.add_row("Warnings", str(report["warnings"]), f"{report['warnings']/total*100:.1f}%")
            table.add_row("Errors", str(report["errors"]), f"{report['errors']/total*100:.1f}%")
        else:
            table.add_row("Total Videos", "0", "N/A")
        
        console.print(table)


def convert_booleans_to_strings(obj):
    """Convert boolean values to strings for JSON serialization"""
    if isinstance(obj, bool):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_booleans_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_booleans_to_strings(item) for item in obj]
    return obj
