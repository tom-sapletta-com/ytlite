#!/usr/bin/env python3
"""Simple write test"""
import os
import sys

def main():
    test_file = "test_write.txt"
    test_message = "This is a test message.\n"
    
    print(f"Attempting to write to {test_file}...")
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_message)
        print(f"Successfully wrote to {test_file}")
        
        # Verify the file was written
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"File content: {content!r}")
            os.remove(test_file)  # Clean up
            print("Test file removed")
        else:
            print("Error: File was not created")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
