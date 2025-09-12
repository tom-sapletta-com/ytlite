#!/usr/bin/env python3
"""
YTLite Web GUI - Simple Working Version
A simplified version to test the refactored components work together.
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask

def create_simple_app():
    """Create a simple Flask app with the refactored components."""
    app = Flask(__name__)
    
    # Define paths
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / 'output'
    
    # Ensure directories exist
    output_dir.mkdir(exist_ok=True)
    (output_dir / 'projects').mkdir(exist_ok=True)
    (output_dir / 'svg_projects').mkdir(exist_ok=True)
    
    # Setup routes
    from web_gui.routes import setup_routes
    setup_routes(app, base_dir, output_dir)
    
    # Add JavaScript serving
    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        from web_gui.javascript import JAVASCRIPT_CODE
        return JAVASCRIPT_CODE, 200, {'Content-Type': 'application/javascript'}
    
    return app

if __name__ == '__main__':
    print("🚀 Starting YTLite Web GUI (Simple Version)")
    app = create_simple_app()
    
    # Test the app first
    with app.test_client() as client:
        resp = client.get('/')
        print(f"✓ Index route test: {resp.status_code}")
        
        resp = client.get('/api/projects')
        print(f"✓ Projects API test: {resp.status_code}")
    
    print("✓ Basic tests passed, starting server...")
    print("📂 Open: http://localhost:5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
