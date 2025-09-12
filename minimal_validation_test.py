#!/usr/bin/env python3
"""Minimal validation test server"""
import sys
import os
sys.path.insert(0, 'src')

from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Inline HTML with validation features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .field-error { color: #dc3545; font-size: 12px; margin-top: 4px; display: none; }
        .field-error.show { display: block; }
        .validation-errors { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 6px; padding: 12px; margin-bottom: 16px; display: none; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .project-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .edit-form { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <h1>🧪 YTLite Form Validation Test</h1>
    
    <div id="messages"></div>
    
    <h2>📝 Create New Project</h2>
    <div id="createForm">
        <div id="validationErrors" class="validation-errors"></div>
        
        <div class="form-group">
            <label for="project">Project Name:</label>
            <input type="text" id="project" name="project" placeholder="my-awesome-project" onblur="validateField('project')">
            <div id="project-error" class="field-error"></div>
        </div>
        
        <div class="form-group">
            <label for="content">Content (Markdown):</label>
            <textarea id="content" name="content" rows="6" placeholder="title: My Project&#10;date: 2025-01-15&#10;&#10;# My Title&#10;&#10;This is my content." onblur="validateField('content')"></textarea>
            <div id="content-error" class="field-error"></div>
        </div>
        
        <button onclick="generateProject()">🚀 Generate Project</button>
    </div>
    
    <h2>📂 Test Projects</h2>
    <div id="projectsList"></div>
    
    <div id="editForm" class="edit-form">
        <h3>✏️ Edit Project</h3>
        <div id="editValidationErrors" class="validation-errors"></div>
        
        <div class="form-group">
            <label for="editProject">Project Name:</label>
            <input type="text" id="editProject" name="editProject" readonly>
        </div>
        
        <div class="form-group">
            <label for="editContent">Content (Markdown):</label>
            <textarea id="editContent" name="editContent" rows="6" onblur="validateEditField('editContent')"></textarea>
            <div id="editContent-error" class="field-error"></div>
        </div>
        
        <button onclick="updateProject()">💾 Update Project</button>
        <button onclick="hideEditForm()">Cancel</button>
    </div>

    <script>
        // Validation functions
        function validateField(fieldName) {
            const field = document.getElementById(fieldName);
            const errorDiv = document.getElementById(fieldName + '-error');
            const value = field.value.trim();
            
            let isValid = true;
            let errorMessage = '';
            
            switch (fieldName) {
                case 'project':
                    if (!value) {
                        isValid = false;
                        errorMessage = 'Project name is required';
                    } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
                        isValid = false;
                        errorMessage = 'Project name can only contain letters, numbers, hyphens, and underscores';
                    } else if (value.length < 3) {
                        isValid = false;
                        errorMessage = 'Project name must be at least 3 characters long';
                    } else if (value.length > 50) {
                        isValid = false;
                        errorMessage = 'Project name must be less than 50 characters';
                    }
                    break;
                    
                case 'content':
                    if (!value) {
                        isValid = false;
                        errorMessage = 'Content is required';
                    } else if (value.length < 10) {
                        isValid = false;
                        errorMessage = 'Content must be at least 10 characters long';
                    }
                    break;
            }
            
            if (isValid) {
                field.style.borderColor = '#ccc';
                errorDiv.classList.remove('show');
                errorDiv.textContent = '';
            } else {
                field.style.borderColor = '#dc3545';
                errorDiv.classList.add('show');
                errorDiv.textContent = errorMessage;
            }
            
            return isValid;
        }
        
        function validateEditField(fieldName) {
            const field = document.getElementById(fieldName);
            const errorDiv = document.getElementById(fieldName + '-error');
            const value = field.value.trim();
            
            let isValid = true;
            let errorMessage = '';
            
            if (fieldName === 'editContent') {
                if (!value) {
                    isValid = false;
                    errorMessage = 'Content is required';
                } else if (value.length < 10) {
                    isValid = false;
                    errorMessage = 'Content must be at least 10 characters long';
                }
            }
            
            if (isValid) {
                field.style.borderColor = '#ccc';
                errorDiv.classList.remove('show');
                errorDiv.textContent = '';
            } else {
                field.style.borderColor = '#dc3545';
                errorDiv.classList.add('show');
                errorDiv.textContent = errorMessage;
            }
            
            return isValid;
        }

        function validateAllFields() {
            const projectValid = validateField('project');
            const contentValid = validateField('content');
            return projectValid && contentValid;
        }

        function showValidationErrors(errors) {
            const errorsDiv = document.getElementById('validationErrors');
            if (errors && errors.length > 0) {
                errorsDiv.innerHTML = '<strong>Please fix these errors:</strong><ul>' + 
                    errors.map(error => `<li>${error}</li>`).join('') + '</ul>';
                errorsDiv.style.display = 'block';
            } else {
                errorsDiv.style.display = 'none';
            }
        }

        function showEditValidationErrors(errors) {
            const errorsDiv = document.getElementById('editValidationErrors');
            if (errors && errors.length > 0) {
                errorsDiv.innerHTML = '<strong>Please fix these errors:</strong><ul>' + 
                    errors.map(error => `<li>${error}</li>`).join('') + '</ul>';
                errorsDiv.style.display = 'block';
            } else {
                errorsDiv.style.display = 'none';
            }
        }

        function showMessage(message, type) {
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
            setTimeout(() => messagesDiv.innerHTML = '', 5000);
        }

        // Generate project function
        async function generateProject() {
            showValidationErrors([]);
            
            if (!validateAllFields()) {
                showMessage('Please fix the validation errors before generating', 'error');
                return;
            }
            
            const project = document.getElementById('project').value.trim();
            const content = document.getElementById('content').value;
            
            const formData = new FormData();
            formData.append('project', project);
            formData.append('markdown', content);
            
            showMessage('🚀 Generating project...', 'info');
            
            try {
                const res = await fetch('/api/generate', { method: 'POST', body: formData });
                const data = await res.json();
                
                if (res.ok) {
                    showMessage(`✅ Project "${project}" generated successfully`, 'success');
                    document.getElementById('project').value = '';
                    document.getElementById('content').value = '';
                    loadProjects();
                } else {
                    if (data.validation_errors) {
                        showValidationErrors(data.validation_errors);
                    }
                    showMessage(`❌ Generation failed: ${data.error}`, 'error');
                }
            } catch (e) {
                showMessage(`❌ Generation error: ${e.message}`, 'error');
            }
        }

        // Load and display projects
        async function loadProjects() {
            try {
                const res = await fetch('/api/projects');
                const data = await res.json();
                const container = document.getElementById('projectsList');
                
                if (data.projects && data.projects.length > 0) {
                    container.innerHTML = data.projects.map(project => `
                        <div class="project-card">
                            <h4>${project.name}</h4>
                            <p>Type: ${project.type} | Status: ${project.svg_valid ? 'Valid' : 'Invalid'}</p>
                            <button onclick="editProject('${project.name}')">✏️ Edit</button>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<p>No projects found.</p>';
                }
            } catch (e) {
                console.error('Failed to load projects:', e);
            }
        }

        // Edit project functions
        async function editProject(name) {
            try {
                const res = await fetch(`/api/svg_meta?project=${name}`);
                if (res.ok) {
                    const meta = await res.json();
                    populateEditForm(name, meta);
                    showEditForm();
                }
            } catch (e) {
                showMessage('Failed to load project metadata', 'error');
            }
        }

        function populateEditForm(name, meta) {
            document.getElementById('editProject').value = name;
            
            // Try multiple possible field names for content
            const content = meta.markdown_content || meta.markdown || meta.content || meta.description || '';
            document.getElementById('editContent').value = content;
            
            // Debug logging
            if (!content) {
                console.warn('No content found for project', name, 'Available meta fields:', Object.keys(meta));
                showMessage(`⚠️ No content found for ${name}. Available fields: ${Object.keys(meta).join(', ')}`, 'error');
            } else {
                console.log(`✓ Content loaded for ${name}: ${content.length} characters`);
            }
        }

        function showEditForm() {
            document.getElementById('editForm').style.display = 'block';
        }

        function hideEditForm() {
            document.getElementById('editForm').style.display = 'none';
            showEditValidationErrors([]);
        }

        async function updateProject() {
            showEditValidationErrors([]);
            
            if (!validateEditField('editContent')) {
                showMessage('Please fix the validation errors before updating', 'error');
                return;
            }
            
            const project = document.getElementById('editProject').value.trim();
            const content = document.getElementById('editContent').value;
            
            const formData = new FormData();
            formData.append('project', project);
            formData.append('markdown', content);
            
            showMessage('💾 Updating project...', 'info');
            
            try {
                const res = await fetch('/api/generate', { method: 'POST', body: formData });
                const data = await res.json();
                
                if (res.ok) {
                    showMessage(`✅ Project "${project}" updated successfully`, 'success');
                    hideEditForm();
                    loadProjects();
                } else {
                    if (data.validation_errors) {
                        showEditValidationErrors(data.validation_errors);
                    }
                    showMessage(`❌ Update failed: ${data.error}`, 'error');
                }
            } catch (e) {
                showMessage(`❌ Update error: ${e.message}`, 'error');
            }
        }

        // Load projects on page load
        window.addEventListener('load', loadProjects);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/projects')
def api_projects():
    return jsonify({
        'projects': [
            {
                'name': 'test-project-1',
                'type': 'svg', 
                'svg_valid': True,
                'created': '2025-01-15'
            },
            {
                'name': 'example-with-content',
                'type': 'svg',
                'svg_valid': True,
                'created': '2025-01-14'
            },
            {
                'name': 'empty-content-test',
                'type': 'svg',
                'svg_valid': False,
                'created': '2025-01-13'
            }
        ]
    })

@app.route('/api/svg_meta')
def api_svg_meta():
    project = request.args.get('project', '')
    
    # Test different content field scenarios
    if project == 'test-project-1':
        return jsonify({
            'title': 'Test Project One',
            'markdown_content': 'title: Test Project One\ndate: 2025-01-15\ntheme: wetware\n\n# Test Content\n\nThis project uses **markdown_content** field.',
            'theme': 'wetware'
        })
    elif project == 'example-with-content':
        return jsonify({
            'title': 'Example Project',
            'markdown': 'title: Example Project\n\n# Example\n\nThis project uses **markdown** field.',
            'theme': 'default'
        })
    elif project == 'empty-content-test':
        return jsonify({
            'title': 'Empty Content Test',
            'theme': 'default'
            # Intentionally no content fields to test the debug logging
        })
    
    return jsonify({'error': 'Project not found'}), 404

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.form
    project = data.get('project', '')
    markdown = data.get('markdown', '')
    
    # Server-side validation
    errors = []
    
    if not project:
        errors.append('Project name is required')
    elif len(project) < 3:
        errors.append('Project name must be at least 3 characters long')
    
    if not markdown:
        errors.append('Content is required')
    elif len(markdown) < 10:
        errors.append('Content must be at least 10 characters long')
    
    if errors:
        return jsonify({
            'error': 'Validation failed',
            'validation_errors': errors
        }), 400
    
    return jsonify({
        'message': f'Project "{project}" processed successfully',
        'project': project
    })

if __name__ == '__main__':
    print("🧪 Starting validation test server on http://localhost:5000")
    print("\nTest scenarios:")
    print("1. Try creating project with name 'ab' (too short)")
    print("2. Try creating project with empty content")
    print("3. Edit 'test-project-1' - should populate with markdown_content")
    print("4. Edit 'example-with-content' - should populate with markdown") 
    print("5. Edit 'empty-content-test' - should show debug message about missing content")
    print("6. Test real-time validation on blur events")
    app.run(host='0.0.0.0', port=5000, debug=False)
