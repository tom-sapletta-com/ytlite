#!/usr/bin/env python3
"""Test server specifically for testing form validation."""
import sys
import os
from pathlib import Path

# Add src directory to path  
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from flask import Flask, jsonify, request
from web_gui.templates import get_html_template
from web_gui.javascript import get_javascript_content

app = Flask(__name__)

@app.route('/')
def index():
    return get_html_template()

@app.route('/main.js')
def main_js():
    return get_javascript_content(), 200, {'Content-Type': 'application/javascript'}

@app.route('/api/projects')
def api_projects():
    # Sample projects including one with detailed metadata for testing edit form
    return jsonify({
        'projects': [
            {
                'name': 'test-project-1',
                'type': 'svg', 
                'svg_valid': True,
                'created': '2025-01-15',
                'title': 'Test Project One',
                'svg': 'test-project-1.svg',
                'has_video': False
            },
            {
                'name': 'example-project',
                'type': 'directory',
                'svg': 'example.svg',
                'versions': 1,
                'created': '2025-01-14'
            }
        ]
    })

@app.route('/api/svg_meta')
def api_svg_meta():
    project = request.args.get('project', '')
    if not project:
        return jsonify({'error': 'No project specified'}), 400
    
    # Provide different metadata based on project name to test field population
    if project == 'test-project-1':
        return jsonify({
            'title': 'Test Project One',
            'markdown_content': 'title: Test Project One\ndate: 2025-01-15\ntheme: wetware\ntags: [test, validation]\n\n# Test Content\n\nThis is **markdown content** for testing the edit form.\n\n- Item 1\n- Item 2\n\n## Features\n- Form validation\n- Real-time error display',
            'theme': 'wetware',
            'template': 'modern', 
            'voice': 'en-US',
            'font_size': 'medium'
        })
    elif project == 'example-project':
        return jsonify({
            'title': 'Example Project',
            'markdown': 'title: Example Project\ndate: 2025-01-14\n\n# Example\n\nThis project has markdown in the "markdown" field instead of "markdown_content".',
            'theme': 'default',
            'template': 'simple',
            'voice': 'en-GB',
            'font_size': 'large'
        })
    else:
        return jsonify({'error': 'Project not found'}), 404

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.form
    project = data.get('project', '')
    markdown = data.get('markdown', '')
    
    print(f"Generate request - Project: '{project}', Content length: {len(markdown)}")
    
    # Test validation logic
    errors = []
    
    if not project:
        errors.append('Project name is required')
    elif len(project) < 3:
        errors.append('Project name must be at least 3 characters long')
    elif not project.replace('-', '').replace('_', '').isalnum():
        errors.append('Project name can only contain letters, numbers, hyphens, and underscores')
    
    if not markdown:
        errors.append('Content is required')
    elif len(markdown) < 10:
        errors.append('Content must be at least 10 characters long')
    
    if errors:
        return jsonify({
            'error': 'Validation failed',
            'validation_errors': errors
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
    print("Starting validation test server on http://localhost:5000")
    print("Test scenarios:")
    print("1. Create project with invalid name (< 3 chars)")
    print("2. Create project with empty content")
    print("3. Edit 'test-project-1' - should populate with markdown_content") 
    print("4. Edit 'example-project' - should populate with markdown field")
    print("5. Test real-time validation on field blur")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
