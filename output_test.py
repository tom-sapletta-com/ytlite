#!/usr/bin/env python3
# Simple output test script

def main():
    # Try to write to a file
    with open("test_output.txt", "w") as f:
        f.write("This is a test file.\n")
        f.write("If you can see this, file writing works.\n")
    
    # Print to stdout
    print("This is stdout output")
    
    # Print to stderr
    import sys
    print("This is stderr output", file=sys.stderr)
    
    # Print environment info
    import os
    print("\nEnvironment:")
    for var in ["PATH", "HOME", "USER", "SHELL", "LANG"]:
        print(f"{var}: {os.environ.get(var, 'Not set')}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
