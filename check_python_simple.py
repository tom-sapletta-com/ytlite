#!/usr/bin/env python3
# Simple Python check script

import sys

def main():
    print("Python Environment Check")
    print("======================")
    
    # Basic info
    print(f"Python Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Current Directory: {__file__}")
    
    # Try to write to a file
    try:
        with open("test_output.txt", "w") as f:
            f.write("Test successful!")
        print("✅ Successfully wrote to test_output.txt")
    except Exception as e:
        print(f"❌ Error writing to file: {e}")
    
    # Try to import a module
    try:
        import os
        print(f"✅ Successfully imported 'os' module")
    except ImportError as e:
        print(f"❌ Error importing 'os': {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
