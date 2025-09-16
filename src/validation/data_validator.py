#!/usr/bin/env python3
"""
Data Validation Module for YTLite
Handles validation of data structure and content files
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
from rich.console import Console

console = Console()


class DataValidator:
    def __init__(self, project_dir: str = '.'):
        self.project_dir = project_dir
        self.reports_dir = os.path.join(project_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def validate_data(self, content_path: str = 'content') -> Tuple[dict, str]:
        """Validate data structure and content"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "data_structure",
            "results": []
        }
        
        passed = 0
        failed = 0
        
        def check_directory(path, name):
            nonlocal passed, failed
            if os.path.exists(path) and os.path.isdir(path):
                console.print(f"[green]✓ {name} directory exists[/]")
                passed += 1
                return {
                    "test": f"{name} directory existence",
                    "status": "PASS",
                    "details": f"Directory found at {path}"
                }
            else:
                console.print(f"[red]✗ {name} directory missing[/]")
                failed += 1
                return {
                    "test": f"{name} directory existence",
                    "status": "FAIL", 
                    "details": f"Directory not found at {path}"
                }
        
        def check_file(path, name):
            nonlocal passed, failed
            if os.path.exists(path) and os.path.isfile(path):
                console.print(f"[green]✓ {name} file exists[/]")
                passed += 1
                return {
                    "test": f"{name} file existence",
                    "status": "PASS",
                    "details": f"File found at {path}"
                }
            else:
                console.print(f"[red]✗ {name} file missing[/]")
                failed += 1
                return {
                    "test": f"{name} file existence",
                    "status": "FAIL",
                    "details": f"File not found at {path}"
                }
        
        def check_content_files(content_dir):
            nonlocal passed, failed
            content_count = 0
            if os.path.exists(content_dir):
                for file in os.listdir(content_dir):
                    if file.endswith('.md'):
                        content_count += 1
                        
                if content_count > 0:
                    console.print(f"[green]✓ Found {content_count} content files[/]")
                    passed += 1
                    return {
                        "test": "Content files availability",
                        "status": "PASS",
                        "details": f"Found {content_count} markdown files in {content_dir}"
                    }
                else:
                    console.print(f"[yellow]⚠ No content files found in {content_dir}[/]")
                    failed += 1
                    return {
                        "test": "Content files availability",
                        "status": "FAIL",
                        "details": f"No .md files found in {content_dir}"
                    }
            else:
                console.print(f"[red]✗ Content directory {content_dir} not found[/]")
                failed += 1
                return {
                    "test": "Content files availability",
                    "status": "FAIL",
                    "details": f"Content directory {content_dir} does not exist"
                }

        # Check main directories
        directories_to_check = [
            (content_path, "Content"),
            ("output", "Output"),
            ("templates", "Templates")
        ]
        
        for dir_path, dir_name in directories_to_check:
            results["results"].append(check_directory(dir_path, dir_name))
        
        # Check essential files
        files_to_check = [
            ("config.yaml", "Configuration"),
            ("requirements.txt", "Requirements"),
            ("README.md", "README")
        ]
        
        for file_path, file_name in files_to_check:
            results["results"].append(check_file(file_path, file_name))
        
        # Check content files
        results["results"].append(check_content_files(content_path))
        
        # Validate config.yaml structure if it exists
        config_path = "config.yaml"
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                required_keys = ['output_path', 'themes', 'fonts']
                missing_keys = [key for key in required_keys if key not in config]
                
                if not missing_keys:
                    console.print("[green]✓ Config structure is valid[/]")
                    passed += 1
                    results["results"].append({
                        "test": "Config structure validation",
                        "status": "PASS",
                        "details": "All required configuration keys present"
                    })
                else:
                    console.print(f"[yellow]⚠ Config missing keys: {missing_keys}[/]")
                    failed += 1
                    results["results"].append({
                        "test": "Config structure validation",
                        "status": "FAIL",
                        "details": f"Missing required keys: {missing_keys}"
                    })
            except Exception as e:
                console.print(f"[red]✗ Config validation error: {e}[/]")
                failed += 1
                results["results"].append({
                    "test": "Config structure validation",
                    "status": "ERROR",
                    "details": f"Failed to validate config: {str(e)}"
                })
        
        # Calculate summary
        total_tests = len(results["results"])
        results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        # Save report
        report_path = self._save_report(results, "data")
        return results["summary"], report_path

    def _save_report(self, report: dict, report_type: str) -> str:
        """Save the validation report to a file as plain text"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self.project_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"{report_type}_validation_{timestamp}.txt")
        
        try:
            with open(report_path, 'w') as f:
                # Write header
                f.write(f"YTLite {report_type.title()} Validation Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {report['timestamp']}\n")
                f.write(f"Validation Type: {report['validation_type']}\n\n")
                
                # Write summary
                if 'summary' in report:
                    summary = report['summary']
                    f.write(f"Summary:\n")
                    f.write(f"  Total Tests: {summary['total_tests']}\n")
                    f.write(f"  Passed: {summary['passed']}\n")
                    f.write(f"  Failed: {summary['failed']}\n")
                    f.write(f"  Success Rate: {summary['success_rate']}\n\n")
                
                # Write detailed results
                f.write("Detailed Results:\n")
                f.write("-" * 30 + "\n")
                for result in report['results']:
                    f.write(f"Test: {result['test']}\n")
                    f.write(f"Status: {result['status']}\n")
                    f.write(f"Details: {result['details']}\n\n")
                
            console.print(f"[green]Report saved to {report_path}[/]")
            
        except Exception as e:
            console.print(f"[bold red]Failed to save {report_type} validation report: {e}[/]")
        return report_path

    def summarize_report(self, report):
        """Summarize the validation report into a concise format."""
        summary = f"Validation Type: {report['validation_type'].capitalize()}\nTimestamp: {report['timestamp']}\n"
        pass_count = sum(1 for r in report['results'] if r['status'] == 'PASS')
        fail_count = sum(1 for r in report['results'] if r['status'] == 'FAIL')
        error_count = sum(1 for r in report['results'] if r['status'] == 'ERROR')
        
        summary += f"Results: {pass_count} passed, {fail_count} failed, {error_count} errors\n"
        
        if fail_count > 0 or error_count > 0:
            summary += "Issues:\n"
            for result in report['results']:
                if result['status'] in ['FAIL', 'ERROR']:
                    summary += f"  - {result['test']}: {result['status']}\n"
                summary += "\n"
        return summary
