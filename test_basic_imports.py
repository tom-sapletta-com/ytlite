#!/usr/bin/env python3
"""Test basic imports to isolate the problem."""
import sys
from pathlib import Path

print("Starting basic import test...")

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))
print(f"Added {src_dir} to sys.path")

try:
    print("Testing YTLite import...")
    from ytlite_main import YTLite
    print("✅ YTLite imported successfully")
    
    print("Testing YTLite initialization...")
    ytlite = YTLite()
    print("✅ YTLite initialized successfully")
    
    print("Testing config overrides...")
    overrides = {'theme': 'test', 'voice': 'test-voice'}
    ytlite_override = YTLite(config_overrides=overrides)
    print(f"✅ Config overrides work: theme={ytlite_override.config.get('theme')}")
    
    print("Testing web_gui import...")
    from web_gui import create_app
    print("✅ web_gui imported successfully")
    
    print("Testing Flask app creation...")
    app = create_app()
    print("✅ Flask app created successfully")
    
    print("\n🎉 All basic functionality tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
