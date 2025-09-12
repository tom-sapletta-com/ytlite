#!/usr/bin/env python3
"""Test script to run the new refactored ytlite_web_gui.py"""
import sys
import os
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Set environment for fast testing
os.environ['YTLITE_FAST_TEST'] = '1'

try:
    print("🚀 Starting new refactored YTLite Web GUI...")
    
    # Import the new version
    from ytlite_web_gui import create_production_app
    
    print("✓ Creating production app...")
    app = create_production_app()
    
    print("✓ App created successfully")
    
    # List routes to verify
    routes = list(app.url_map.iter_rules())
    api_routes = [r.rule for r in routes if '/api/' in r.rule]
    print(f"✓ {len(api_routes)} API routes configured:")
    for route in api_routes[:5]:  # Show first 5
        print(f"  {route}")
    
    print(f"\n🌐 Starting server on http://localhost:5000")
    print("📋 Updated routes.py with new SVGDataURIPackager usage")
    print("🔧 Using refactored modular architecture")
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True, 
        use_reloader=False
    )
    
except KeyboardInterrupt:
    print("\n👋 Server stopped by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
