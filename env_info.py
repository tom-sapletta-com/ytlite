#!/usr/bin/env python3
"""
Environment Information Script
"""
import os
import sys
import platform
import subprocess

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def main():
    """Main function to gather environment information."""
    # System information
    print_section("System Information")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Python information
    print_section("Python Environment")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check basic commands
    print_section("Command Availability")
    for cmd in ["ls", "python3", "pip3", "ffmpeg"]:
        try:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {cmd}: {result.stdout.strip()}")
            else:
                print(f"❌ {cmd}: Not found")
        except Exception as e:
            print(f"⚠️  Error checking {cmd}: {e}")
    
    # Check file permissions
    print_section("File System Check")
    try:
        test_file = "test_permission.txt"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Can write to current directory")
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")
    
    print("\nEnvironment check complete!")

if __name__ == "__main__":
    main()
