#!/usr/bin/env python3
"""
Application Validation Module for YTLite
Handles validation of app setup, dependencies, and build tests
"""

import os
import subprocess
import importlib
from datetime import datetime
from typing import Dict, Tuple
from rich.console import Console

console = Console()


class AppValidator:
    def __init__(self, project_dir: str = '.'):
        self.project_dir = project_dir
        self.reports_dir = os.path.join(project_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def validate_app(self, detailed: bool = False) -> dict:
        """Validate app setup and dependencies"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "app_setup",
            "results": []
        }
        
        passed = 0
        failed = 0
        errors = 0

        def check_package(package_name, display_name):
            nonlocal passed, failed
            try:
                importlib.import_module(package_name)
                console.print(f"[green]✓ {display_name} is available[/]")
                passed += 1
                return {
                    "test": f"{display_name} availability",
                    "status": "PASS",
                    "details": f"{display_name} module imported successfully"
                }
            except ImportError as e:
                console.print(f"[red]✗ {display_name} is not available: {e}[/]")
                failed += 1
                return {
                    "test": f"{display_name} availability", 
                    "status": "FAIL",
                    "details": f"Failed to import {display_name}: {str(e)}"
                }
            except Exception as e:
                console.print(f"[yellow]⚠ {display_name} check error: {e}[/]")
                failed += 1
                return {
                    "test": f"{display_name} availability",
                    "status": "ERROR", 
                    "details": f"Unexpected error checking {display_name}: {str(e)}"
                }

        # Check core packages
        for pkg in [("flask", "Flask"), ("yaml", "PyYAML"), ("moviepy", "MoviePy"), ("openai_whisper", "Whisper")]:
            results["results"].append(check_package(pkg[0], pkg[1]))

        def run_build_test(command, test_name):
            nonlocal passed, failed, errors
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    console.print(f"[green]✓ {test_name} passed[/]")
                    passed += 1
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "details": f"Command succeeded: {command}"
                    }
                else:
                    console.print(f"[red]✗ {test_name} failed[/]")
                    if detailed:
                        console.print(f"[dim]Command: {command}[/]")
                        console.print(f"[dim]stdout: {result.stdout}[/]")
                        console.print(f"[dim]stderr: {result.stderr}[/]")
                    failed += 1
                    return {
                        "test": test_name,
                        "status": "FAIL", 
                        "details": f"Command failed with return code {result.returncode}. stderr: {result.stderr}"
                    }
            except subprocess.TimeoutExpired:
                console.print(f"[yellow]⚠ {test_name} timed out[/]")
                errors += 1
                return {
                    "test": test_name,
                    "status": "TIMEOUT",
                    "details": f"Command timed out after 300 seconds: {command}"
                }
            except Exception as e:
                console.print(f"[red]✗ {test_name} error: {e}[/]")
                errors += 1
                return {
                    "test": test_name,
                    "status": "ERROR",
                    "details": f"Exception running command: {str(e)}"
                }

        # Run build tests if detailed validation requested
        if detailed:
            build_tests = [
                ("python3 -c 'import sys; print(sys.version)'", "Python version check"),
                ("python3 -m pip list", "Pip packages list"),
            ]
            
            for command, test_name in build_tests:
                results["results"].append(run_build_test(command, test_name))

        # Calculate summary
        total_tests = len(results["results"])
        results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }

        # Save report
        report_path = self._save_report(results, "app")
        results["report_path"] = report_path
        return results

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
                    f.write(f"  Errors: {summary['errors']}\n")
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
