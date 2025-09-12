#!/usr/bin/env python3
"""Simple direct start for refactored YTLite Web GUI"""
import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Environment
os.environ['YTLITE_FAST_TEST'] = '1'

def main():
    try:
        # Direct Flask app creation
        from flask import Flask
        from web_gui.templates import get_html_template
        from web_gui.javascript import get_javascript_content
        from web_gui.routes import setup_routes
        
        print("🚀 Starting YTLite Web GUI (Refactored Version)")
        
        # Create Flask app
        app = Flask(__name__)
        
        # Setup paths
        base_dir = current_dir
        output_dir = base_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        (output_dir / 'projects').mkdir(exist_ok=True)
        (output_dir / 'svg_projects').mkdir(exist_ok=True)
        
        # Setup routes
        setup_routes(app, base_dir, output_dir)
        
        print(f"✅ Routes configured: {len(list(app.url_map.iter_rules()))} endpoints")
        print("🌐 Server: http://localhost:5000")
        print("✓ Modular architecture with updated routes.py")
        print("✓ Enhanced form validation")
        print("✓ Real-time error display")
        
        # Start server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
