#!/usr/bin/env python3
"""
Minimal working Web GUI for YTLite
"""
from flask import Flask, jsonify, render_template_string
from pathlib import Path
import json

app = Flask(__name__)

# Simple HTML template
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YTLite Web GUI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .project-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .btn { padding: 8px 15px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        .btn:hover { background: #0056b3; }
        .projects-grid { display: grid; gap: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 YTLite Web GUI</h1>
        <div id="projectsList">Loading projects...</div>
        <br>
        <button onclick="createNewProject()" class="btn">➕ Create New Project</button>
    </div>

    <script>
    async function loadProjects() {
        try {
            const res = await fetch('/api/projects');
            const data = await res.json();
            const container = document.getElementById('projectsList');
            
            if (data.projects && data.projects.length > 0) {
                container.innerHTML = '<h2>Projects:</h2><div class="projects-grid">' + 
                    data.projects.map(project => 
                        '<div class="project-card">' +
                            '<h3>' + project.name + '</h3>' +
                            '<p>' + (project.svg ? '📄 SVG Package Available' : '📁 Files Only') + '</p>' +
                            (project.svg ? 
                                '<a href="/files/projects/' + project.name + '/' + project.svg + '" target="_blank" class="btn">📄 Open SVG</a>' : 
                                ''
                            ) +
                            '<a href="/files/projects/' + project.name + '/" target="_blank" class="btn">📂 Browse Files</a>' +
                        '</div>'
                    ).join('') + 
                '</div>';
            } else {
                container.innerHTML = '<p>No projects found. Create your first project!</p>';
            }
        } catch (e) {
            console.error('Failed to load projects:', e);
            document.getElementById('projectsList').innerHTML = '<p>Error loading projects: ' + e.message + '</p>';
        }
    }

    function createNewProject() {
        const name = prompt('Enter project name:');
        if (name) {
            alert('Project creation feature coming soon! Project name: ' + name);
        }
    }

    // Load projects when page loads
    document.addEventListener('DOMContentLoaded', loadProjects);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/api/projects')
def api_projects():
    """List all projects in output/projects directory"""
    try:
        projects_dir = Path('output/projects')
        items = []
        
        if projects_dir.exists():
            for project_dir in sorted(projects_dir.glob('*/')):
                name = project_dir.name
                svg_files = list(project_dir.glob('*.svg'))
                items.append({
                    "name": name,
                    "svg": svg_files[0].name if svg_files else None
                })
        
        return jsonify({"projects": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<path:filepath>')
def serve_files(filepath):
    """Serve files from output directory"""
    from flask import send_from_directory
    try:
        return send_from_directory('output', filepath)
    except Exception as e:
        return f"File not found: {e}", 404

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    print("🚀 Starting YTLite Web GUI on http://localhost:5000")
    print("📁 Projects directory: output/projects/")
    
    # Ensure output directories exist
    Path('output/projects').mkdir(parents=True, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
