#!/usr/bin/env python3
# Simple test script to verify Python environment

def main():
    print("Python Environment Test")
    print("======================")
    print("This is a test to verify basic Python functionality.")
    print("If you can see this message, Python is working correctly.")
    
    # Try to write to a file
    try:
        with open("test_output.txt", "w") as f:
            f.write("Test successful!\n")
        print("✅ Successfully wrote to test_output.txt")
    except Exception as e:
        print(f"❌ Error writing to file: {e}")

if __name__ == "__main__":
    main()
