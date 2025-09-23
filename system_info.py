#!/usr/bin/env python3
"""Gather system information using Python's built-in modules"""
import os
import sys
import platform
import stat
import pwd
import grp
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def get_file_perms(path):
    """Get file permissions in human-readable format."""
    try:
        mode = os.stat(path).st_mode
        perms = {
            'read': bool(mode & 0o400),
            'write': bool(mode & 0o200),
            'execute': bool(mode & 0o100),
            'mode': oct(stat.S_IMODE(mode))
        }
        return perms
    except Exception as e:
        return {'error': str(e)}

def main():
    """Main function to gather system information."""
    # Basic system information
    print_section("SYSTEM INFORMATION")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # User information
    print_section("USER INFORMATION")
    try:
        print(f"Current User: {pwd.getpwuid(os.getuid()).pw_name}")
        print(f"Effective User: {pwd.getpwuid(os.geteuid()).pw_name}")
        print(f"Groups: {', '.join(grp.getgrgid(g).gr_name for g in os.getgroups())}")
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    # Environment information
    print_section("ENVIRONMENT VARIABLES")
    for var in ['PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'PWD', 'VIRTUAL_ENV']:
        print(f"{var}: {os.environ.get(var, 'Not set')}")
    
    # File system information
    print_section("FILE SYSTEM PERMISSIONS")
    paths = [
        "/usr/bin",
        "/usr/local/bin",
        "/tmp",
        ".",
        "test_output"
    ]
    
    for path in paths:
        print(f"\n{path}:")
        try:
            path_obj = Path(path)
            print(f"  exists: {path_obj.exists()}")
            if path_obj.exists():
                print(f"  is_dir: {path_obj.is_dir()}")
                print(f"  is_file: {path_obj.is_file()}")
                perms = get_file_perms(str(path_obj))
                if 'error' in perms:
                    print(f"  Error: {perms['error']}")
                else:
                    print(f"  mode: {perms['mode']}")
                    print(f"  readable: {perms['read']}")
                    print(f"  writable: {perms['write']}")
                    print(f"  executable: {perms['execute']}")
        except Exception as e:
            print(f"  Error checking {path}: {e}")
    
    # Python module information
    print_section("PYTHON MODULES")
    modules = ['numpy', 'moviepy', 'PIL', 'ffmpeg', 'imageio']
    for module in modules:
        try:
            __import__(module)
            version = sys.modules[module].__version__
            print(f"{module}: {version}")
        except ImportError:
            print(f"{module}: Not installed")
        except Exception as e:
            print(f"{module}: Error - {e}")
    
    # System resources
    print_section("SYSTEM RESOURCES")
    try:
        import resource
        print("Resource limits:")
        for res, desc in [
            (resource.RLIMIT_CORE, 'Core file size'),
            (resource.RLIMIT_CPU, 'CPU time'),
            (resource.RLIMIT_FSIZE, 'File size'),
            (resource.RLIMIT_NOFILE, 'Open files'),
            (resource.RLIMIT_NPROC, 'Processes'),
            (resource.RLIMIT_STACK, 'Stack size')
        ]:
            soft, hard = resource.getrlimit(res)
            print(f"  {desc}: soft={soft}, hard={hard}")
    except Exception as e:
        print(f"Could not get resource limits: {e}")

if __name__ == "__main__":
    main()
