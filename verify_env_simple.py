#!/usr/bin/env python3
"""Simple environment verification script"""
import os
import sys

def main():
    # Create a test file
    test_file = "test_env.txt"
    test_message = "Environment test successful!\n"
    
    try:
        # Test file write
        with open(test_file, 'w') as f:
            f.write(test_message)
        
        # Test file read
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Verify content
        if content == test_message:
            print("✅ Environment verification successful!")
            print(f"Python: {sys.version}")
            print(f"Working directory: {os.getcwd()}")
            print(f"File system access: Working")
        else:
            print("❌ Content verification failed")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    main()
