#!/usr/bin/env python3
"""
Working version of the new refactored YTLite Web GUI
Uses the modular architecture with updated routes.py
"""
import sys
import os
from pathlib import Path

# Setup path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Set fast test mode
os.environ['YTLITE_FAST_TEST'] = '1'

def main():
    try:
        print("🚀 Starting New Refactored YTLite Web GUI")
        print("✓ Using modular architecture (ytlite_web_gui.py)")
        print("✓ Updated routes.py with corrected SVGDataURIPackager")
        print("✓ Enhanced form validation and error display")
        
        # Import and create app
        from ytlite_web_gui import create_production_app
        app = create_production_app()
        
        print(f"🌐 Server starting on http://localhost:5000")
        print("🔧 Press Ctrl+C to stop")
        
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
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
