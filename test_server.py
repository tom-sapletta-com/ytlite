#!/usr/bin/env python3
"""
Minimal test server to verify Flask functionality
"""
import sys
sys.path.insert(0, 'src')

from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html>
<head><title>YTLite Test Server</title></head>
<body>
    <h1>✅ YTLite Test Server Working</h1>
    <p>Flask is functioning correctly</p>
    <ul>
        <li><a href="/api/test">Test API</a></li>
        <li><a href="/api/projects">Projects API</a></li>
    </ul>
</body>
</html>'''

@app.route('/api/test')
def api_test():
    return jsonify({"status": "ok", "message": "API working"})

@app.route('/api/projects')
def api_projects():
    # Simple projects check
    projects_dir = Path('output/projects')
    items = []
    
    if projects_dir.exists():
        for p in sorted(projects_dir.glob('*/')):
            name = p.name
            svg_files = list(p.glob('*.svg'))
            items.append({
                "name": name, 
                "svg": svg_files[0].name if svg_files else None
            })
    
    return jsonify({"projects": items})

if __name__ == '__main__':
    print("🚀 Starting YTLite test server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
