#!/usr/bin/env python3
"""Simple system check script"""
import os
import sys

def main():
    print("=== Simple System Check ===\n")
    
    # Basic Python info
    print("Python:")
    print(f"  Version: {sys.version}")
    print(f"  Executable: {sys.executable}")
    print(f"  Path: {sys.path}\n")
    
    # Current directory
    print("Current Directory:")
    print(f"  Path: {os.getcwd()}")
    print(f"  Contents: {os.listdir('.')}\n")
    
    # Environment variables
    print("Environment Variables:")
    for var in ['PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'PWD', 'VIRTUAL_ENV']:
        print(f"  {var}: {os.environ.get(var, 'Not set')}")
    
    # File system access
    print("\nFile System Access:")
    for path in ['/tmp', '/usr/bin', '/usr/local/bin', '.']:
        try:
            exists = os.path.exists(path)
            is_dir = os.path.isdir(path) if exists else False
            can_read = os.access(path, os.R_OK) if exists else False
            can_write = os.access(path, os.W_OK) if exists else False
            can_exec = os.access(path, os.X_OK) if exists else False
            
            print(f"\n{path}:")
            print(f"  exists: {exists}")
            if exists:
                print(f"  is_dir: {is_dir}")
                print(f"  readable: {can_read}")
                print(f"  writable: {can_write}")
                print(f"  executable: {can_exec}")
        except Exception as e:
            print(f"  Error checking {path}: {e}")
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    main()
