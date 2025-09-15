#!/usr/bin/env python3
"""Run the YTLite Web GUI using the application factory."""
import os
import sys
from pathlib import Path

# Ensure src is in the path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from web_gui import create_app

# Set default FAST_TEST mode if not already set
os.environ.setdefault('YTLITE_FAST_TEST', '0')

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    print("🚀 YTLite Web GUI with App Factory")
    print(f"✓ FAST_TEST mode: {'ON (tone audio)' if os.environ.get('YTLITE_FAST_TEST') == '1' else 'OFF (Edge TTS)'}")
    print(f"🌐 http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
