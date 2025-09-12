#!/usr/bin/env python3
"""
Debug Web GUI - Minimal working version to test API endpoints
"""
import os
import sys
from pathlib import Path

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# Basic routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>YTLite Debug</title></head>
    <body>
        <h1>YTLite Web GUI Debug</h1>
        <p>Server is running!</p>
        <div>
            <h2>Test API Endpoints:</h2>
            <button onclick="fetch('/api/projects').then(r=>r.text()).then(console.log)">Test /api/projects</button>
            <button onclick="fetch('/api/svg_meta?project=test').then(r=>r.text()).then(console.log)">Test /api/svg_meta</button>
        </div>
        <script>
        function testGenerate() {
            const formData = new FormData();
            formData.append('project', 'wetware_intro');
            formData.append('markdown', 'title: Test\\n\\n# Test Content');
            formData.append('theme', 'default');
            formData.append('template', 'simple');
            fetch('/api/generate', {method: 'POST', body: formData})
                .then(r => r.text()).then(console.log);
        }
        </script>
        <button onclick="testGenerate()">Test /api/generate</button>
    </body>
    </html>
    '''

@app.route('/api/projects')
def api_projects():
    try:
        return jsonify({'projects': [], 'message': 'Debug endpoint working'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/svg_meta')
def api_svg_meta():
    try:
        project = request.args.get('project', '')
        return jsonify({'project': project, 'message': 'svg_meta debug endpoint'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.form.to_dict()
        project = data.get('project', 'test')
        
        # Mock successful response
        return jsonify({
            'message': f'Debug: Would generate project "{project}"',
            'project': project,
            'data_received': data
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 Starting YTLite Debug Web GUI on http://localhost:5000")
    print("📝 This is a minimal version to test API endpoints")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {e}")
        traceback.print_exc()
