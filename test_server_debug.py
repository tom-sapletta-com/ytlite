#!/usr/bin/env python3
"""Debug version of test server to isolate startup issues."""
import os
import sys
from pathlib import Path

print("DEBUG: Starting test server debug script")

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

print(f"DEBUG: Added {src_dir} to sys.path")

try:
    print("DEBUG: Importing Flask")
    from flask import Flask
    print("DEBUG: Flask imported successfully")
    
    print("DEBUG: Importing create_app")
    from web_gui import create_app
    print("DEBUG: create_app imported successfully")
    
    print("DEBUG: Creating Flask app")
    app = create_app()
    print("DEBUG: Flask app created successfully")
    
    print("DEBUG: Starting server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
