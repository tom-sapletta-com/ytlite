#!/usr/bin/env python3
"""
Incremental test server to isolate YTLite Web GUI issues
Tests each component step by step
"""
import sys
import os
import traceback
from pathlib import Path
from flask import Flask, jsonify, render_template_string

# Setup paths
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

print(f"🔍 Testing YTLite components step by step...")
print(f"📁 Current dir: {current_dir}")
print(f"📁 Source dir: {src_dir}")

app = Flask(__name__)

# Test 1: Basic Flask
@app.route('/')
def index():
    return '''
    <html>
    <head><title>YTLite Component Test</title></head>
    <body>
        <h1>🧪 YTLite Component Test Server</h1>
        <h2>Tests:</h2>
        <ul>
            <li>✅ Flask: Working</li>
            <li><a href="/test-templates">Test Templates</a></li>
            <li><a href="/test-javascript">Test JavaScript</a></li>
            <li><a href="/test-routes">Test Routes</a></li>
            <li><a href="/api/projects">Test API</a></li>
        </ul>
    </body>
    </html>
    '''

# Test 2: Templates
@app.route('/test-templates')
def test_templates():
    try:
        from web_gui.templates import get_html_template
        return "<h1>✅ Templates: OK</h1><p>Templates module imported successfully</p>"
    except Exception as e:
        return f"<h1>❌ Templates: FAIL</h1><p>Error: {e}</p><pre>{traceback.format_exc()}</pre>"

# Test 3: JavaScript
@app.route('/test-javascript')
def test_javascript():
    try:
        from web_gui.javascript import get_javascript_content
        return "<h1>✅ JavaScript: OK</h1><p>JavaScript module imported successfully</p>"
    except Exception as e:
        return f"<h1>❌ JavaScript: FAIL</h1><p>Error: {e}</p><pre>{traceback.format_exc()}</pre>"

# Test 4: Routes
@app.route('/test-routes')
def test_routes():
    try:
        from web_gui.routes import setup_routes
        return "<h1>✅ Routes: OK</h1><p>Routes module imported successfully</p>"
    except Exception as e:
        return f"<h1>❌ Routes: FAIL</h1><p>Error: {e}</p><pre>{traceback.format_exc()}</pre>"

# Test 5: Full integration
@app.route('/test-full')
def test_full():
    try:
        from web_gui.templates import get_html_template
        from web_gui.javascript import get_javascript_content
        from web_gui.routes import setup_routes
        
        # Try to get the full template
        html = get_html_template()
        return "<h1>✅ Full Integration: OK</h1><p>All components working together</p>"
    except Exception as e:
        return f"<h1>❌ Full Integration: FAIL</h1><p>Error: {e}</p><pre>{traceback.format_exc()}</pre>"

@app.route('/api/projects')
def api_projects():
    return jsonify({'projects': [], 'status': 'test_mode'})

if __name__ == '__main__':
    print("🚀 Starting YTLite Component Test Server")
    print("🌐 Server: http://localhost:5000")
    print("🔧 Testing each refactored component individually")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        traceback.print_exc()
