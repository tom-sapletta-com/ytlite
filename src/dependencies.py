#!/usr/bin/env python3
"""
YTLite Dependencies Checker
Checks and installs required dependencies
"""

import sys
import subprocess
from rich.console import Console

console = Console()

def check_and_install_package(package_name, import_name=None):
    """Check if package is installed, install if missing"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        console.print(f"[yellow]Package {package_name} not found. Installing...[/]")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            console.print(f"[green]✓ {package_name} installed successfully[/]")
            return True
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ Failed to install {package_name}[/]")
            return False

def check_os_dependencies():
    """Check for essential OS-level command-line tools."""
    console.print("[cyan]Checking OS-level dependencies...[/]")
    required_commands = ["ffmpeg", "sox", "espeak-ng"]
    all_found = True

    for cmd in required_commands:
        if subprocess.call(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            console.print(f"[bold red]✗ Dependency '{cmd}' not found.[/]")
            console.print(f"  Please install it using your system's package manager.")
            console.print(f"  Example: [cyan]sudo apt-get install {cmd}[/]")
            all_found = False

    return all_found

def verify_dependencies():
    """Verify all required dependencies are installed"""
    required_packages = [
        ("moviepy", "moviepy.editor"),
        ("edge-tts", "edge_tts"),
        ("python-frontmatter", "frontmatter"),
        ("pyyaml", "yaml"),
        ("pillow", "PIL"),
        ("rich", "rich"),
        ("python-dotenv", "dotenv"),
        ("numpy", "numpy"),
    ]
    
    console.print("[cyan]Checking dependencies...[/]")
    all_ok = True
    
    for package, import_name in required_packages:
        if not check_and_install_package(package, import_name):
            all_ok = False
            # Special handling for moviepy due to import issues
            if package == "moviepy":
                console.print(f"[yellow]Forcing reinstall of a specific version of {package} due to import issue...[/]")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "moviepy==1.0.3"])
                    console.print(f"[green]✓ {package} version 1.0.3 reinstalled successfully[/]")
                    if check_and_install_package(package, import_name):
                        all_ok = True  # Recheck after reinstall
                except subprocess.CalledProcessError:
                    console.print(f"[red]✗ Failed to reinstall {package}[/]")
    
    # Check OS-level dependencies like ffmpeg
    if not check_os_dependencies():
        all_ok = False

    if all_ok:
        console.print("[green]✓ All dependencies verified[/]")
    else:
        console.print("[red]✗ Some dependencies failed to install[/]")
        sys.exit(1)
    
    return all_ok

if __name__ == "__main__":
    verify_dependencies()
