import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
try:
    from flask import Flask
    print("Flask imported successfully.")
except ImportError as e:
    print(f"Failed to import Flask: {e}")
