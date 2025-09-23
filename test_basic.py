#!/usr/bin/env python3
# Basic test script to verify Python functionality

def main():
    print("Basic Python Test")
    print("================")
    print("If you can see this message, Python is working correctly.")
    
    # Test file operations
    try:
        with open("test_output.txt", "w") as f:
            f.write("Test successful!\n")
        print("✅ Successfully wrote to test_output.txt")
    except Exception as e:
        print(f"❌ Error writing to file: {e}")
    
    # Test imports
    print("\nTesting imports...")
    try:
        import sys
        print(f"✅ sys imported successfully (Python {sys.version.split()[0]})")
    except ImportError as e:
        print(f"❌ Failed to import sys: {e}")

if __name__ == "__main__":
    main()
