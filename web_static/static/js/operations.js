'use strict';

async function generateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value;
  
  // Clear previous errors
  if (typeof showValidationErrors === 'function') showValidationErrors([]);
  
  // Validate all fields
  if (typeof validateAllFields === 'function' && !validateAllFields()) {
    if (typeof showMessage === 'function') showMessage('Please fix the validation errors before generating', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  if (font_size) formData.append('font_size', font_size);
  
  if (typeof showMessage === 'function') showMessage('🚀 Generating project...', 'info');
  if (typeof logEvent === 'function') { try { logEvent(`Generate start for ${project}`, 'info'); } catch (_) {} }
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      let successMsg = `✅ Project "${project}" generated successfully.`;
      if (data.validation && data.validation.message) {
        successMsg += ` ${data.validation.message}`;
      }
      if (typeof showMessage === 'function') showMessage(successMsg, data.validation && data.validation.valid ? 'success' : 'warning');
      localStorage.setItem(`ytlite:content:${project}`, content);
      if (typeof logEvent === 'function') { try { logEvent(`Generate done for ${project}`, 'success', {validation: data.validation || null}); } catch (_) {} }
      if (typeof window.updateMediaPreview === 'function') window.updateMediaPreview(project);
      if (typeof hideProjectForm === 'function') hideProjectForm();
      if (typeof loadProjects === 'function') await loadProjects();
    } else {
      if (data.validation_errors && typeof showValidationErrors === 'function') {
        showValidationErrors(data.validation_errors);
      }
      if (typeof showMessage === 'function') showMessage(`❌ Generation failed: ${data.message || data.error}`, 'error');
      if (typeof logEvent === 'function') { try { logEvent(`Generate failed for ${project}: ${data.message || data.error}`, 'error'); } catch (_) {} }
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Generation error: ${e.message}`, 'error');
    if (typeof logEvent === 'function') { try { logEvent(`Generate error for ${project}: ${e.message}`, 'error'); } catch (_) {} }
  }
}

async function updateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value;
  const force_regenerate = document.getElementById('force_regenerate').checked;
  
  if (!project) return;
  
  if (typeof showValidationErrors === 'function') showValidationErrors([]);
  if (typeof validateAllFields === 'function' && !validateAllFields()) {
    if (typeof showMessage === 'function') showMessage('Please fix the validation errors before updating', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  if (font_size) formData.append('font_size', font_size);
  formData.append('force_regenerate', force_regenerate);
  
  if (typeof showMessage === 'function') showMessage('💾 Updating project...', 'info');
  if (typeof logEvent === 'function') { try { logEvent(`Update start for ${project}`, 'info'); } catch (_) {} }
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      let successMsg = `✅ Project "${project}" updated successfully.`;
      if (data.validation && data.validation.message) {
        successMsg += ` ${data.validation.message}`;
      }
      if (typeof showMessage === 'function') showMessage(successMsg, data.validation && data.validation.valid ? 'success' : 'warning');
      localStorage.setItem(`ytlite:content:${project}`, content);
      if (typeof logEvent === 'function') { try { logEvent(`Update done for ${project}`, 'success', {validation: data.validation || null}); } catch (_) {} }
      if (typeof window.updateMediaPreview === 'function') window.updateMediaPreview(project);
      if (typeof hideProjectForm === 'function') hideProjectForm();
      if (typeof loadProjects === 'function') await loadProjects();
    } else {
      if (data.validation_errors && typeof showValidationErrors === 'function') {
        showValidationErrors(data.validation_errors);
      }
      if (typeof showMessage === 'function') showMessage(`❌ Update failed: ${data.message || data.error}`, 'error');
      if (typeof logEvent === 'function') { try { logEvent(`Update failed for ${project}: ${data.message || data.error}`, 'error'); } catch (_) {} }
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Update error: ${e.message}`, 'error');
    if (typeof logEvent === 'function') { try { logEvent(`Update error for ${project}: ${e.message}`, 'error'); } catch (_) {} }
  }
}

async function fetchProjectMarkdown(name) {
  try {
    const tryPaths = [
      `/files/projects/${name}/${name}.md`,
      `/files/projects/${name}/description.md`
    ];
    for (const p of tryPaths) {
      const res = await fetch(p);
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim().length > 0) {
          document.getElementById('content').value = text;
          localStorage.setItem(`ytlite:content:${name}`, text);
          if (typeof logEvent === 'function') { try { logEvent(`Content loaded from ${p} for ${name} (${text.length} chars)`, 'info'); } catch (_) {} }
          return true;
        }
      }
    }
    if (typeof logEvent === 'function') { try { logEvent(`No markdown file found for ${name}`, 'warn'); } catch (_) {} }
    return false;
  } catch (e) {
    if (typeof logEvent === 'function') { try { logEvent(`Failed to fetch markdown for ${name}: ${e.message}`, 'error'); } catch (_) {} }
    return false;
  }
}

// moved to media.js

async function deleteProject(projectName, event) {
  if (event) event.stopPropagation();
  if (typeof showMessage === 'function') showMessage(`🗑️ Deleting "${projectName}"...`, 'info');
  try {
    const response = await fetch('/api/delete_project', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    const data = await response.json();
    if (response.ok) {
      if (typeof showMessage === 'function') showMessage(`✅ Project "${projectName}" deleted successfully`, 'success');
      if (typeof loadProjects === 'function') await loadProjects();
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ Error: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Failed to delete project: ${e.message}`, 'error');
  }
}

// moved to publish.js

// moved to history.js and media.js

async function validateProject(projectName, event) {
  if (event) event.stopPropagation();
  if (typeof showMessage === 'function') showMessage(`🔍 Validating "${projectName}"...`, 'info');
  try {
    const response = await fetch(`/api/validate_project?project=${encodeURIComponent(projectName)}`);
    const data = await response.json();
    if (response.ok) {
      const isValid = data.valid;
      const errors = data.errors || [];
      const warnings = data.warnings || [];
      let message = `Project "${projectName}" validation: `;
      let type = 'success';
      if (!isValid && errors.length > 0) {
        message += `❌ ${errors.length} error(s) found`;
        type = 'error';
      } else if (warnings.length > 0) {
        message += `⚠️ ${warnings.length} warning(s) found`;
        type = 'warning';
      } else {
        message += '✅ All checks passed';
        type = 'success';
      }
      if (typeof showMessage === 'function') showMessage(message, type);
      if (errors.length > 0 || warnings.length > 0) {
        setTimeout(() => {
          const details = [...errors, ...warnings].join('\n');
          if (typeof showMessage === 'function') showMessage(`Validation details:\n${details}`, type);
        }, 1000);
      }
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ Validation failed: ${data.error || data.message}`, 'error');
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Validation error: ${e.message}`, 'error');
  }
}

async function editProject(name, evt) {
  if (evt) { evt.preventDefault(); evt.stopPropagation(); }
  if (typeof showFormForEdit === 'function') showFormForEdit();
  document.getElementById('project').value = name;
  document.getElementById('content').value = 'Loading...';
  if (typeof window.updateMediaPreview === 'function') window.updateMediaPreview(name);
  try {
    const res = await fetch(`/api/svg_metadata?project=${name}`);
    if (res.ok) {
      const data = await res.json();
      const metaData = data.metadata || data;
      if (typeof logEvent === 'function') { try { logEvent(`Loaded metadata for ${name}`, 'info', {fields: Object.keys(metaData || {})}); } catch (_) {} }
      if (typeof populateProjectForm === 'function') populateProjectForm(name, metaData);
      const contentEl = document.getElementById('content');
      if (!contentEl.value || contentEl.value === 'Loading...') {
        await fetchProjectMarkdown(name);
      }
      if (typeof window.updateMediaPreview === 'function') window.updateMediaPreview(name);
    } else {
      document.getElementById('content').value = 'Error: Failed to load project data.';
      if (typeof showMessage === 'function') showMessage('Failed to load project metadata', 'error');
    }
  } catch (e) {
    console.error('Failed to load project metadata:', e);
    document.getElementById('content').value = 'Error: Failed to load project data.';
    if (typeof showMessage === 'function') showMessage('Failed to load project metadata', 'error');
  }
}

function editSVGProject(name, evt) {
  return editProject(name, evt);
}
