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
    """Run the universal OS dependency installer script."""
    console.print("[cyan]Checking OS-level dependencies (e.g., ffmpeg)...[/]")
    script_path = Path(__file__).parent.parent / "scripts" / "install-os-deps.sh"
    
    if not script_path.exists():
        console.print(f"[red]Error: Dependency installer script not found at {script_path}[/]")
        return False

    try:
        # Make sure the script is executable
        subprocess.check_call(["chmod", "+x", str(script_path)])
        # Run the script
        subprocess.check_call([str(script_path)])
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]OS dependency installation failed: {e}[/]")
        return False

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
