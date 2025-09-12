#!/usr/bin/env python3
"""
YTLite Web GUI - Definitive Working Version
This is the final working version that uses the refactored modular components.
"""
import os
import sys
from pathlib import Path

# Ensure proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Main function to start the web GUI."""
    try:
        print("🔧 Setting up YTLite Web GUI...")
        
        # Import Flask
        from flask import Flask
        print("✓ Flask imported")
        
        # Create app
        app = Flask(__name__)
        print("✓ Flask app created")
        
        # Setup paths
        base_dir = Path(__file__).resolve().parent.parent
        output_dir = base_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        (output_dir / 'projects').mkdir(exist_ok=True)
        (output_dir / 'svg_projects').mkdir(exist_ok=True)
        print(f"✓ Paths configured: {output_dir}")
        
        # Import and setup routes
        from web_gui.routes import setup_routes
        setup_routes(app, base_dir, output_dir)
        print("✓ Routes configured")
        
        # Add JavaScript route
        @app.route('/static/js/web_gui.js')
        def serve_javascript():
            from web_gui.javascript import JAVASCRIPT_CODE
            return JAVASCRIPT_CODE, 200, {'Content-Type': 'application/javascript'}
        print("✓ JavaScript route added")
        
        # Test the app
        with app.test_client() as client:
            resp = client.get('/')
            if resp.status_code != 200:
                raise Exception(f"Index route failed: {resp.status_code}")
            
            resp = client.get('/api/projects')
            if resp.status_code != 200:
                raise Exception(f"Projects API failed: {resp.status_code}")
        
        print("✓ App tested successfully")
        
        # Get port
        port = int(os.getenv('FLASK_PORT', 5000))
        
        print(f"🚀 Starting server on http://localhost:{port}")
        print("📂 Open the URL above in your browser")
        print("🔄 All refactored components are now active")
        print("⏹️  Press Ctrl+C to stop")
        
        # Start the server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
