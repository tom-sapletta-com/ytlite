#!/usr/bin/env python3
"""Simple debug server to test the web GUI."""
import sys
import os
from pathlib import Path

# Add src directory to path  
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

log_file = open('debug_server_log.txt', 'w')
sys.stdout = log_file
sys.stderr = log_file

print(f"Starting debug server...")
print(f"Current dir: {current_dir}")
print(f"Src dir: {src_dir}")

try:
    from flask import Flask, jsonify, request
    print("Flask imported successfully")
    
    from web_gui.templates import INDEX_HTML
    print("Templates imported successfully")
    
    from web_gui.javascript import get_javascript_content  
    print("JavaScript imported successfully")
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        print("Serving index page")
        return INDEX_HTML
    
    @app.route('/main.js')
    def main_js():
        print("Serving main.js")
        return get_javascript_content(), 200, {'Content-Type': 'application/javascript'}
    
    @app.route('/api/projects')
    def api_projects():
        print("API projects called")
        # Sample project for testing
        return jsonify({
            'projects': [{
                'name': 'test-project',
                'type': 'svg', 
                'svg_valid': True,
                'created': '2025-01-15',
                'title': 'Test Project',
                'svg': 'test-project.svg',
                'has_video': False
            }]
        })
    
    @app.route('/api/svg_meta')
    def api_svg_meta():
        project = request.args.get('project', '')
        print(f"API svg_meta called for project: {project}")
        if not project:
            return jsonify({'error': 'No project specified'}), 400
        
        # Sample metadata for testing
        return jsonify({
            'title': 'Test Project Title',
            'markdown': 'title: Test Project\ndate: 2025-01-15\ntheme: default\n\n# Test Content\n\nThis is test markdown content for validation testing.',
            'markdown_content': 'title: Test Project\ndate: 2025-01-15\ntheme: default\n\n# Test Content\n\nThis is test markdown content for validation testing.',
            'theme': 'default',
            'template': 'modern', 
            'voice': 'en-US',
            'font_size': 'medium'
        })
    
    @app.route('/api/generate', methods=['POST'])
    def api_generate():
        print("API generate called")
        data = request.form
        project = data.get('project', '')
        markdown = data.get('markdown', '')
        
        print(f"Generate project: {project}")
        print(f"Markdown length: {len(markdown)}")
        
        # Simulate validation
        if not project or len(project) < 3:
            return jsonify({
                'error': 'Project name must be at least 3 characters',
                'validation_errors': ['Project name must be at least 3 characters']
            }), 400
        
        if not markdown or len(markdown) < 10:
            return jsonify({
                'error': 'Content must be at least 10 characters', 
                'validation_errors': ['Content must be at least 10 characters']
            }), 400
        
        # Success response
        return jsonify({
            'message': f'Project "{project}" generated successfully',
            'project': project
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})
    
    if __name__ == '__main__':
        print("Starting debug server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    log_file.close()
