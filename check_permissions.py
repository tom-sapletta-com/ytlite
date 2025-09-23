#!/usr/bin/env python3
"""Check system permissions and command execution"""
import os
import sys
import subprocess
from pathlib import Path

def check_command(cmd, description):
    """Check if a command can be executed."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Run permission checks."""
    print("=== System Permission Checks ===\n")
    
    # Check basic commands
    commands = [
        ("echo 'Hello, World!'", "Basic command execution"),
        ("python -c \"print('Python works')\"", "Python command execution"),
        ("which python", "Python executable location"),
        ("which ffmpeg", "FFmpeg installation"),
        ("ls -la", "Directory listing"),
        ("pwd", "Current working directory"),
        ("whoami", "Current user"),
        ("groups", "User groups"),
        ("ulimit -a", "System limits")
    ]
    
    for cmd, desc in commands:
        print(f"\n{desc}:")
        print(f"$ {cmd}")
        result = check_command(cmd, desc)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        elif result['success']:
            if result['stdout']:
                print(f"✅ Output: {result['stdout']}")
            else:
                print("✅ Command executed successfully")
        else:
            print(f"❌ Failed with return code {result['returncode']}")
            if result['stderr']:
                print(f"Error: {result['stderr']}")
    
    # Check file permissions
    print("\n=== File Permissions ===")
    paths = [
        "/usr/bin",
        "/usr/local/bin",
        "/tmp",
        ".",
        "test_output"
    ]
    
    for path in paths:
        try:
            path_obj = Path(path)
            print(f"\n{path}:")
            print(f"  exists: {path_obj.exists()}")
            if path_obj.exists():
                print(f"  is_dir: {path_obj.is_dir()}")
                print(f"  is_file: {path_obj.is_file()}")
                print(f"  readable: {os.access(str(path_obj), os.R_OK)}")
                print(f"  writable: {os.access(str(path_obj), os.W_OK)}")
                print(f"  executable: {os.access(str(path_obj), os.X_OK)}")
        except Exception as e:
            print(f"  Error checking {path}: {e}")
    
    print("\n=== Environment Variables ===")
    for var in ['PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'PWD']:
        print(f"{var}: {os.environ.get(var, 'Not set')}")

if __name__ == "__main__":
    main()
