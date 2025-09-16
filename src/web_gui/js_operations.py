#!/usr/bin/env python3
"""
JavaScript Operations Module for YTLite Web GUI
"""

def get_operations_js():
    """Return JavaScript code for project operations functionality."""
    return """
// Project generation
async function generateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const fontSizeEl = document.getElementById('font_size');
  const fontSize = fontSizeEl ? fontSizeEl.value : 'medium';
  const lang = document.getElementById('lang').value;
  const forceRegenerate = document.getElementById('force_regenerate') ? document.getElementById('force_regenerate').checked : false;

  if (!validateAllFields()) {
    showMessage('❌ Please fix validation errors before generating', 'error');
    return;
  }

  const btn = document.getElementById('generateBtn');
  const originalText = btn.textContent;
  btn.textContent = '⏳ Generating...';
  btn.disabled = true;

  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  formData.append('font_size', fontSize);
  formData.append('lang', lang);
  formData.append('force_regenerate', forceRegenerate);

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Project "${project}" generated successfully!`, 'success');
      hideProjectForm();
      loadProjects();
      logEvent(`Project generated: ${project}`, 'success', result);
    } else {
      showMessage(`❌ Generation failed: ${result.message}`, 'error');
      logEvent(`Generation failed for ${project}`, 'error', result);
    }
  } catch (error) {
    showMessage(`❌ Generation error: ${error.message}`, 'error');
    logEvent(`Generation error for ${project}`, 'error', {error: error.message});
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

async function updateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const fontSizeEl = document.getElementById('font_size');
  const fontSize = fontSizeEl ? fontSizeEl.value : 'medium';
  const lang = document.getElementById('lang').value;
  const forceRegenerate = true;

  if (!validateAllFields()) {
    showMessage('❌ Please fix validation errors before updating', 'error');
    return;
  }

  const btn = document.getElementById('updateBtn');
  const originalText = btn.textContent;
  btn.textContent = '⏳ Updating...';
  btn.disabled = true;

  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  formData.append('font_size', fontSize);
  formData.append('lang', lang);
  formData.append('force_regenerate', forceRegenerate);

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Project "${project}" updated successfully!`, 'success');
      hideProjectForm();
      loadProjects();
      logEvent(`Project updated: ${project}`, 'success', result);
    } else {
      showMessage(`❌ Update failed: ${result.message}`, 'error');
      logEvent(`Update failed for ${project}`, 'error', result);
    }
  } catch (error) {
    showMessage(`❌ Update error: ${error.message}`, 'error');
    logEvent(`Update error for ${project}`, 'error', {error: error.message});
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

async function deleteProject(projectName, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  if (!confirm(`Are you sure you want to delete project "${projectName}"?`)) {
    return;
  }

  try {
    const response = await fetch('/api/delete_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName })
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Project "${projectName}" deleted successfully!`, 'success');
      loadProjects();
      logEvent(`Project deleted: ${projectName}`, 'info');
    } else {
      showMessage(`❌ Delete failed: ${result.message}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ Delete error: ${error.message}`, 'error');
  }
}

async function validateProject(projectName, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  try {
    const response = await fetch('/api/validate_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName })
    });

    const result = await response.json();
    if (response.ok) {
      const status = result.valid ? 'valid' : 'has issues';
      const type = result.valid ? 'success' : 'warning';
      showMessage(`✅ Project "${projectName}" validation: ${status}`, type);
      logEvent(`Project validation: ${projectName}`, type, result);
    } else {
      showMessage(`❌ Validation failed: ${result.message}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ Validation error: ${error.message}`, 'error');
  }
}

async function fetchProjectMarkdown(name) {
  try {
    const tryPaths = [
      `/files/projects/${name}/${name}.md`,
      `/files/projects/${name}/description.md`,
      `/files/projects/${name}/source.md`
    ];
    
    for (const path of tryPaths) {
      try {
        const res = await fetch(path, { cache: 'no-store' });
        if (res.ok) {
          return await res.text();
        }
      } catch (e) {
        continue;
      }
    }
    
    return null;
  } catch (error) {
    logEvent(`Failed to fetch markdown for ${name}: ${error.message}`, 'error');
    return null;
  }
}

window.generateProject = generateProject;
window.updateProject = updateProject;
window.deleteProject = deleteProject;
window.validateProject = validateProject;
window.fetchProjectMarkdown = fetchProjectMarkdown;
"""
