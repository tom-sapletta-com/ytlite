#!/usr/bin/env python3
"""Basic system check script"""
import os
import sys
import platform
import subprocess

def run_command(cmd):
    """Run a command and return its output."""
    print(f"\nRunning: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function."""
    # Basic system info
    print("\n=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test basic commands
    print("\n=== Testing Basic Commands ===")
    commands = [
        ["echo", "Hello, World!"],
        ["python", "--version"],
        ["python3", "--version"],
        ["which", "python"],
        ["which", "python3"],
        ["which", "ffmpeg"],
        ["ffmpeg", "-version"],
        ["ls", "-la"],
        ["pwd"],
        ["whoami"]
    ]
    
    for cmd in commands:
        run_command(cmd)
    
    print("\n=== Test Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
