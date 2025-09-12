#!/usr/bin/env python3
"""
Production YTLite Web GUI - Refactored Version
Complete modular architecture with enhanced validation
"""
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
        print("🚀 YTLite Web GUI - Refactored Version")
        print("✓ Modular architecture with enhanced validation")
        print("✓ Real-time form validation and error display")
        print("✓ Updated routes.py with corrected SVGDataURIPackager")
        
        # Direct Flask setup
        from flask import Flask
        from web_gui.routes import setup_routes
        
        app = Flask(__name__)
        
        # Setup directories
        base_dir = current_dir
        output_dir = base_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        (output_dir / 'projects').mkdir(exist_ok=True)
        (output_dir / 'svg_projects').mkdir(exist_ok=True)
        
        # Setup all refactored routes
        setup_routes(app, base_dir, output_dir)
        
        route_count = len(list(app.url_map.iter_rules()))
        print(f"✅ {route_count} routes configured")
        
        # Quick validation
        with app.test_client() as client:
            resp = client.get('/')
            if resp.status_code == 200:
                print("✅ Main page working")
            resp = client.get('/api/projects')
            if resp.status_code == 200:
                print("✅ Projects API working")
            resp = client.get('/static/js/web_gui.js')
            if resp.status_code == 200:
                print("✅ JavaScript serving working")
        
        print("🌐 Starting server on http://localhost:5000")
        print("📋 Features: Enhanced forms, Real-time validation, Modular design")
        print("⏹️ Press Ctrl+C to stop")
        
        # Start server with production settings
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
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
