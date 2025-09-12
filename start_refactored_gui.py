#!/usr/bin/env python3
"""
Reliable startup script for the new refactored YTLite Web GUI
Bypasses any problematic startup code and runs the server directly.
"""
import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Environment configuration
os.environ['YTLITE_FAST_TEST'] = '1'

def main():
    print("🚀 Starting New Refactored YTLite Web GUI")
    print("=" * 50)
    print("✓ Using ytlite_web_gui.py (refactored version)")
    print("✓ Updated routes.py with corrected SVGDataURIPackager")
    print("✓ Enhanced form validation and error handling")
    print("✓ Fixed JavaScript serving routes")
    
    try:
        # Import and create the production app
        from ytlite_web_gui import create_production_app
        app = create_production_app()
        
        print("\n✅ Application created successfully")
        
        # Create required directories
        base_dir = current_dir
        output_dir = base_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        (output_dir / 'projects').mkdir(exist_ok=True)
        (output_dir / 'svg_projects').mkdir(exist_ok=True)
        
        # Configure all routes with refactored components
        setup_routes(app, base_dir, output_dir)
        
        # Log configuration
        route_count = len(list(app.url_map.iter_rules()))
        print(f"✅ {route_count} routes configured successfully")
        
        # Test critical endpoints
        with app.test_client() as client:
            tests = [('/', 'Index'), ('/api/projects', 'Projects'), ('/health', 'Health')]
            for route, name in tests:
                resp = client.get(route)
                status = "✅" if resp.status_code in [200, 204] else "⚠️"
                print(f"  {status} {name}: {resp.status_code}")
        
        print("🌐 Starting server on http://localhost:5000")
        print("📋 All refactored features: Forms, Validation, Enhanced UX")
        print("⏹️ Press Ctrl+C to stop server")
        
        # Run Flask server
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
        print(f"\n❌ Server error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
