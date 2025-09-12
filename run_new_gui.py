#!/usr/bin/env python3
"""Simple, reliable startup for new refactored YTLite Web GUI"""
import sys
import os
from pathlib import Path

# Setup
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'  
sys.path.insert(0, str(src_dir))
os.environ['YTLITE_FAST_TEST'] = '1'

# Direct imports and app creation
from flask import Flask
from web_gui.templates import get_html_template
from web_gui.javascript import get_javascript_content  
from web_gui.routes import setup_routes

# Create app
app = Flask(__name__)
base_dir = current_dir
output_dir = base_dir / 'output'
output_dir.mkdir(exist_ok=True)

# Setup routes
setup_routes(app, base_dir, output_dir)

print("🚀 New Refactored YTLite Web GUI")
print("✓ Using modular ytlite_web_gui.py architecture") 
print("✓ Updated routes.py with corrected SVGDataURIPackager")
print("✓ Enhanced form validation and real-time errors")
print("🌐 http://localhost:5000")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
