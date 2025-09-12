#!/usr/bin/env python3
"""
Minimal working Web GUI for YTLite
"""
from flask import Flask, jsonify, render_template_string
from pathlib import Path
import json

app = Flask(__name__)

# Enhanced HTML template with refactored features
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YTLite Web GUI - Refactored</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin-bottom: 10px; }
        .header p { color: #666; margin: 0; }
        .project-card { border: 1px solid #e1e5e9; padding: 20px; margin: 15px 0; border-radius: 8px; background: #f8f9fa; transition: all 0.3s ease; }
        .project-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .btn { padding: 12px 20px; margin: 8px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; border: none; cursor: pointer; font-size: 14px; transition: all 0.3s ease; }
        .btn:hover { background: #0056b3; transform: translateY(-1px); }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #1e7e34; }
        .projects-grid { display: grid; gap: 20px; }
        .form-container { background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 20px 0; border: 1px solid #dee2e6; }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        .form-input { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px; transition: border-color 0.3s ease; }
        .form-input:focus { border-color: #007bff; outline: none; }
        .form-input.error { border-color: #dc3545; }
        .error-message { color: #dc3545; font-size: 12px; margin-top: 5px; display: none; }
        .success-message { color: #28a745; font-size: 14px; margin: 10px 0; }
        .hidden { display: none; }
        .loading { opacity: 0.6; pointer-events: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 YTLite Web GUI</h1>
            <p>Enhanced with real-time validation and modern UX</p>
        </div>
        
        <div id="projectsList">Loading projects...</div>
        
        <div class="form-container hidden" id="createForm">
            <h3>➕ Create New Project</h3>
            <form id="projectForm">
                <div class="form-group">
                    <label class="form-label" for="projectName">Project Name</label>
                    <input type="text" id="projectName" class="form-input" required>
                    <div class="error-message" id="nameError">Project name is required</div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="projectDesc">Description</label>
                    <textarea id="projectDesc" class="form-input" rows="3" placeholder="Describe your project..."></textarea>
                    <div class="error-message" id="descError">Description should be at least 10 characters</div>
                </div>
                <button type="submit" class="btn btn-success">Create Project</button>
                <button type="button" class="btn" onclick="cancelForm()">Cancel</button>
            </form>
        </div>
        
        <div id="messages"></div>
        
        <br>
        <button onclick="showCreateForm()" class="btn" id="createBtn">➕ Create New Project</button>
    </div>

    <script>
    // Enhanced JavaScript with real-time validation
    let formVisible = false;
    
    async function loadProjects() {
        try {
            const res = await fetch('/api/projects');
            const data = await res.json();
            const container = document.getElementById('projectsList');
            
            if (data.projects && data.projects.length > 0) {
                container.innerHTML = '<h2>📁 Your Projects:</h2><div class="projects-grid">' + 
                    data.projects.map(project => 
                        '<div class="project-card">' +
                            '<h3>' + escapeHtml(project.name) + '</h3>' +
                            '<p>' + (project.svg ? '📄 SVG Package Available' : '📁 Files Only') + '</p>' +
                            (project.svg ? 
                                '<a href="/files/projects/' + encodeURIComponent(project.name) + '/' + encodeURIComponent(project.svg) + '" target="_blank" class="btn">📄 Open SVG</a>' : 
                                ''
                            ) +
                            '<a href="/files/projects/' + encodeURIComponent(project.name) + '/" target="_blank" class="btn">📂 Browse Files</a>' +
                        '</div>'
                    ).join('') + 
                '</div>';
            } else {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>📝 No projects found yet.</p><p>Create your first project to get started!</p></div>';
            }
        } catch (e) {
            console.error('Failed to load projects:', e);
            document.getElementById('projectsList').innerHTML = '<div style="color: #dc3545; padding: 20px; text-align: center;">❌ Error loading projects: ' + escapeHtml(e.message) + '</div>';
        }
    }
    
    function showCreateForm() {
        document.getElementById('createForm').classList.remove('hidden');
        document.getElementById('createBtn').classList.add('hidden');
        document.getElementById('projectName').focus();
        formVisible = true;
    }
    
    function cancelForm() {
        document.getElementById('createForm').classList.add('hidden');
        document.getElementById('createBtn').classList.remove('hidden');
        clearForm();
        formVisible = false;
    }
    
    function clearForm() {
        document.getElementById('projectName').value = '';
        document.getElementById('projectDesc').value = '';
        clearErrors();
    }
    
    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.form-input').forEach(el => el.classList.remove('error'));
    }
    
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorEl = document.getElementById(fieldId.replace('project', '').toLowerCase() + 'Error');
        field.classList.add('error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    }
    
    function validateForm() {
        clearErrors();
        let isValid = true;
        
        const name = document.getElementById('projectName').value.trim();
        const desc = document.getElementById('projectDesc').value.trim();
        
        if (!name) {
            showError('projectName', 'Project name is required');
            isValid = false;
        } else if (name.length < 3) {
            showError('projectName', 'Project name must be at least 3 characters');
            isValid = false;
        } else if (!/^[a-zA-Z0-9_-]+$/.test(name)) {
            showError('projectName', 'Only letters, numbers, underscores and hyphens allowed');
            isValid = false;
        }
        
        if (desc && desc.length < 10) {
            showError('projectDesc', 'Description should be at least 10 characters');
            isValid = false;
        }
        
        return isValid;
    }
    
    // Real-time validation
    document.getElementById('projectName').addEventListener('input', function() {
        if (this.value.trim()) {
            validateForm();
        }
    });
    
    document.getElementById('projectDesc').addEventListener('input', function() {
        if (this.value.trim()) {
            validateForm();
        }
    });
    
    // Form submission
    document.getElementById('projectForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        const name = document.getElementById('projectName').value.trim();
        const desc = document.getElementById('projectDesc').value.trim();
        
        try {
            const formData = new FormData();
            formData.append('project', name);
            if (desc) formData.append('description', desc);
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('✅ Project "' + escapeHtml(name) + '" created successfully!', 'success');
                cancelForm();
                loadProjects(); // Refresh project list
            } else {
                showMessage('❌ Error: ' + escapeHtml(result.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            showMessage('❌ Network error: ' + escapeHtml(error.message), 'error');
        }
    });
    
    function showMessage(text, type) {
        const messagesEl = document.getElementById('messages');
        messagesEl.innerHTML = '<div class="' + (type === 'success' ? 'success-message' : 'error-message') + '" style="display: block; padding: 15px; border-radius: 6px; margin: 15px 0;">' + text + '</div>';
        setTimeout(() => messagesEl.innerHTML = '', 5000);
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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

@app.route('/static/js/web_gui.js')
def serve_web_gui_js():
    """Serve web GUI JavaScript (fallback for external JS requests)."""
    js_content = """// YTLite Web GUI JavaScript - Fallback handler
console.log("YTLite Web GUI JavaScript loaded successfully");

// This is a fallback route - main functionality is inline in HTML
// Added to prevent 500 errors from external JS requests

function initFallbackJS() {
    console.log("Fallback JavaScript initialized");
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFallbackJS);
} else {
    initFallbackJS();
}
"""
    return js_content, 200, {'Content-Type': 'application/javascript'}

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    print("🚀 Starting YTLite Web GUI on http://localhost:5000")
    print("📁 Projects directory: output/projects/")
    
    # Ensure output directories exist
    Path('output/projects').mkdir(parents=True, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
