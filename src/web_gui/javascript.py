#!/usr/bin/env python3
"""
JavaScript code for YTLite Web GUI
Extracted from web_gui.py for better modularity
"""

def get_javascript_content():
    """Return the JavaScript content for the web GUI."""
    return """
(function() {
  "use strict";

  document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadProjects();
  });

// Project view toggle functionality
let currentProjectView = 'grid';

function switchProjectView(view) {
  currentProjectView = view;
  const gridBtn = document.getElementById('grid-btn');
  const tableBtn = document.getElementById('table-btn');
  const projectsContainer = document.getElementById('projectsContainer');
  const projectsTable = document.getElementById('projectsTable');
  
  if (view === 'table') {
    gridBtn.classList.remove('active');
    tableBtn.classList.add('active');
    projectsContainer.style.display = 'none';
    projectsTable.classList.add('active');
    loadProjectsTable();
  } else {
    tableBtn.classList.remove('active');
    gridBtn.classList.add('active');
    projectsContainer.style.display = 'block';
    projectsTable.classList.remove('active');
    loadProjects(); // Reload grid view
  }
}

// Theme management
function toggleTheme() {
  const body = document.body;
  const themeIcon = document.getElementById('theme-icon');
  const themeText = document.getElementById('theme-text');
  
  if (body.getAttribute('data-theme') === 'dark') {
    body.removeAttribute('data-theme');
    themeIcon.textContent = '🌙';
    themeText.textContent = 'Dark Mode';
    localStorage.setItem('ytlite-theme', 'light');
  } else {
    body.setAttribute('data-theme', 'dark');
    themeIcon.textContent = '☀️';
    themeText.textContent = 'Light Mode';
    localStorage.setItem('ytlite-theme', 'dark');
  }
}

// Load saved theme on page load
function loadTheme() {
  const savedTheme = localStorage.getItem('ytlite-theme');
  if (savedTheme === 'dark') {
    document.body.setAttribute('data-theme', 'dark');
    document.getElementById('theme-icon').textContent = '☀️';
    document.getElementById('theme-text').textContent = 'Light Mode';
  }
}

// Form management
function showCreateForm() {
  // Show create form, hide edit form to avoid confusion
  const createForm = document.getElementById('createForm');
  const editForm = document.getElementById('editForm');
  if (editForm) editForm.style.display = 'none';
  if (createForm) {
    createForm.style.display = 'block';
    createForm.scrollIntoView({behavior: 'smooth'});
  }
}

function hideCreateForm() {
  document.getElementById('createForm').style.display = 'none';
}

function showEditForm() {
  // Show edit form, hide create form to avoid confusion
  const editForm = document.getElementById('editForm');
  const createForm = document.getElementById('createForm');
  if (createForm) createForm.style.display = 'none';
  if (editForm) {
    editForm.style.display = 'block';
    editForm.scrollIntoView({behavior: 'smooth'});
  }
}

function hideEditForm() {
  document.getElementById('editForm').style.display = 'none';
}

function selectProject(name) {
  document.getElementById('project').value = name;
  showCreateForm();
}

// Project loading functions
async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const container = document.getElementById('projectsContainer');
    
    if (data.projects && data.projects.length > 0) {
      container.innerHTML = '<div class="projects-grid">' + 
        data.projects.map(project => renderProjectCard(project)).join('') + '</div>';
      
      // After rendering the basic cards, fetch metadata for each SVG project
      data.projects.forEach(project => {
        if (project.type === 'svg') {
          loadProjectMetadata(project.name);
        }
      });
    } else {
      container.innerHTML = '<p>No projects found. Create your first project!</p>';
    }
  } catch (e) {
    console.error('Failed to load projects:', e);
    document.getElementById('projectsContainer').innerHTML = '<p>Error loading projects.</p>';
  }
}

async function loadProjectsTable() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const tbody = document.getElementById('projectsTableBody');
    
    if (data.projects && data.projects.length > 0) {
      tbody.innerHTML = data.projects.map(project => renderProjectTableRow(project)).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="5">No projects found. Create your first project!</td></tr>';
    }
  } catch (e) {
    console.error('Failed to load projects:', e);
    tbody.innerHTML = '<tr><td colspan="5">Error loading projects.</td></tr>';
  }
}

function renderProjectCard(project) {
  let statusBadge, projectPath, openAction, typeIcon, videoPreview;
  
  if (project.type === 'svg') {
    statusBadge = '<span class="status-badge">📄 SVG Project</span>'; // Placeholder
    projectPath = `/files/svg_projects/${project.svg}`;
    openAction = `<a href="${projectPath}" target="_blank" class="btn btn-primary" onclick="openSVGWithAutoplay('${projectPath}', event)">🎬 Open SVG</a>`;
    typeIcon = '📄';
    
    return `<div class="project-card" id="project-card-${project.name}" onclick="selectProject('${project.name}')">
      <div class="project-title">${typeIcon} ${project.name}</div>
      <div class="project-meta" id="project-meta-${project.name}">${statusBadge}</div>
      <div class="project-actions">
        ${openAction}
        <button onclick="editSVGProject('${project.name}', event)" class="btn">✏️ Edit</button>
        <button onclick="validateProject('${project.name}', event)" class="btn" style="background: #28a745; color: white;">✓ Validate</button>
        <button onclick="publishToYoutube('${project.name}', event)" class="btn" style="background: #ff4444; color: white;">📺 YouTube</button>
        <button onclick="publishToWordPress('${project.name}', event)" class="btn" style="background: #21759b; color: white;">📝 WordPress</button>
        <button onclick="deleteProject('${project.name}', event)" class="btn btn-danger" style="margin-left: 8px;">🗑️ Delete</button>
      </div>
    </div>`;
  } else {
    // Legacy directory projects
    statusBadge = project.svg ? 
      '<span class="status-badge status-success">✓ Valid SVG</span>' : 
      '<span class="status-badge status-warning">⚠ No SVG</span>';
    
    const versionInfo = project.versions && project.versions > 1 ? 
      `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${project.versions} versions</div>` : '';
    
    return `<div class="project-card" onclick="selectProject('${project.name}')">
      <div class="project-title">📁 ${project.name}</div>
      <div class="project-meta">${statusBadge}${versionInfo}</div>
      <div class="project-actions">
        ${project.svg ? `<a href="/files/projects/${project.name}/${project.svg}" target="_blank" class="btn btn-primary">📄 Open SVG</a>` : ''}
        <a href="/files/projects/${project.name}/" target="_blank" class="btn">📂 Files</a>
        <button onclick="editProject('${project.name}', event)" class="btn">✏️ Edit</button>
        ${project.versions && project.versions > 1 ? `<button onclick="showVersionHistory('${project.name}')" class="btn">📜 History</button>` : ''}
        <button onclick="publishToYoutube('${project.name}', event)" class="btn" style="background: #ff4444; color: white;">📺 YouTube</button>
        <button onclick="publishToWordPress('${project.name}', event)" class="btn" style="background: #21759b; color: white;">📝 WordPress</button>
        <button onclick="deleteProject('${project.name}', event)" class="btn btn-danger" style="margin-left: 8px;">🗑️ Delete</button>
      </div>
    </div>`;
  }
}

function renderProjectTableRow(project) {
  const statusText = project.type === 'svg' ? '📄 SVG Project' : '📁 Directory';
  const createdDate = '...'; // Placeholder
  const projectType = project.type === 'svg' ? '📄 SVG' : '📁 Directory';
  
  const actions = `
    <div style="display: flex; gap: 4px; flex-wrap: wrap;">
      ${project.type === 'svg' ? 
        `<a href="/files/svg_projects/${project.svg}" target="_blank" class="btn" style="font-size: 12px; padding: 4px 8px;">🎬 Open</a>` :
        `<a href="/files/projects/${project.name}/" target="_blank" class="btn" style="font-size: 12px; padding: 4px 8px;">📂 Files</a>`
      }
      <button onclick="publishToYoutube('${project.name}', event)" class="btn" style="background: #ff4444; color: white; font-size: 12px; padding: 4px 8px;">📺</button>
      <button onclick="publishToWordPress('${project.name}', event)" class="btn" style="background: #21759b; color: white; font-size: 12px; padding: 4px 8px;">📝</button>
      <button onclick="deleteProject('${project.name}', event)" class="btn btn-danger" style="font-size: 12px; padding: 4px 8px;">🗑️</button>
    </div>
  `;
  
  return `<tr id="project-row-${project.name}" onclick="selectProject('${project.name}')" style="cursor: pointer;">
    <td><strong>${project.name}</strong></td>
    <td>${projectType}</td>
    <td id="project-status-${project.name}">${statusText}</td>
    <td id="project-date-${project.name}">${createdDate}</td>
    <td onclick="event.stopPropagation()">${actions}</td>
  </tr>`;
}

async function loadProjectMetadata(projectName) {
  try {
    const res = await fetch(`/api/svg_meta?project=${projectName}`);
    if (!res.ok) return;

    const meta = await res.json();
    if (!meta) return;

    // Update Grid View
    const metaContainer = document.getElementById(`project-meta-${projectName}`);
    if (metaContainer) {
        const metaInfo = meta.title && meta.title !== projectName ? 
            `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${meta.title}</div>` : '';
        const dateInfo = meta.created ? 
            `<div style="font-size: 11px; color: var(--text-muted);">📅 ${new Date(meta.created).toLocaleDateString()}</div>` : '';
        metaContainer.innerHTML = '<span class="status-badge status-success">✓ SVG Project</span>' + metaInfo + dateInfo;
    }

    // Update Table View
    const statusCell = document.getElementById(`project-status-${projectName}`);
    const dateCell = document.getElementById(`project-date-${projectName}`);
    if (statusCell) {
        statusCell.innerHTML = '✓ SVG Project';
    }
    if (dateCell) {
        dateCell.innerHTML = meta.created ? new Date(meta.created).toLocaleDateString() : 'N/A';
    }

  } catch (e) {
    console.error(`Failed to load metadata for ${projectName}:`, e);
  }
}

// Project editing functions
async function editProject(name, evt) {
  if (evt) { evt.preventDefault(); evt.stopPropagation(); }
  try {
    // Use single-project metadata endpoint for consistent behavior
    const res = await fetch(`/api/svg_metadata?project=${name}`);
    if (res.ok) {
      const data = await res.json();
      const metaData = data.metadata || data; // handle both formats
      populateEditForm(name, metaData);
      showEditForm();
    }
  } catch (e) {
    console.error('Failed to load project metadata:', e);
    showMessage('Failed to load project metadata', 'error');
  }
}

async function editSVGProject(name, evt) {
  if (evt) { evt.preventDefault(); evt.stopPropagation(); }
  try {
    const res = await fetch(`/api/svg_metadata?project=${name}`);
    if (res.ok) {
      const data = await res.json();
      const meta = data.metadata || {};
      populateEditForm(name, meta);
      showEditForm();
    }
  } catch (e) {
    console.error('Failed to load SVG project metadata:', e);
    showMessage('Failed to load project metadata', 'error');
  }
}

function populateEditForm(name, meta) {
  document.getElementById('editProject').value = name;
  
  // Try multiple possible field names for content
  const content = meta.markdown_content || meta.markdown || meta.content || meta.description || '';
  document.getElementById('editContent').value = content;
  
  // Debug logging to help identify missing content
  if (!content) {
    console.warn('No content found for project', name, 'Available meta fields:', Object.keys(meta));
  }
  
  if (meta.voice) document.getElementById('editVoice').value = meta.voice;
  if (meta.theme) document.getElementById('editTheme').value = meta.theme;
  if (meta.template) document.getElementById('editTemplate').value = meta.template;
  if (meta.font_size) document.getElementById('editFontSize').value = meta.font_size;
}

// Field validation
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
    field.parentNode.classList.remove('error');
    errorDiv.classList.remove('show');
    errorDiv.textContent = '';
  } else {
    field.parentNode.classList.add('error');
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

// Project generation
async function generateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value;
  
  // Clear previous errors
  showValidationErrors([]);
  
  // Validate all fields
  if (!validateAllFields()) {
    showMessage('Please fix the validation errors before generating', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  if (font_size) formData.append('font_size', font_size);
  
  showMessage('🚀 Generating project...', 'info');
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      showMessage(`✅ Project "${project}" generated successfully`, 'success');
      hideCreateForm();
      await loadProjects();
    } else {
      // Check if server returned validation errors
      if (data.validation_errors) {
        showValidationErrors(data.validation_errors);
      }
      showMessage(`❌ Generation failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Generation error: ${e.message}`, 'error');
  }
}

// Edit form validation
function validateEditField(fieldName) {
  const field = document.getElementById(fieldName);
  const errorDiv = document.getElementById(fieldName + '-error');
  const value = field.value.trim();
  
  let isValid = true;
  let errorMessage = '';
  
  switch (fieldName) {
    case 'editContent':
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
    field.parentNode.classList.remove('error');
    errorDiv.classList.remove('show');
    errorDiv.textContent = '';
  } else {
    field.parentNode.classList.add('error');
    errorDiv.classList.add('show');
    errorDiv.textContent = errorMessage;
  }
  
  return isValid;
}

function validateEditForm() {
  const contentValid = validateEditField('editContent');
  return contentValid;
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

async function updateProject() {
  const project = document.getElementById('editProject').value.trim();
  const content = document.getElementById('editContent').value;
  const voice = document.getElementById('editVoice').value;
  const theme = document.getElementById('editTheme').value;
  const template = document.getElementById('editTemplate').value;
  const font_size = document.getElementById('editFontSize').value;
  
  if (!project) return;
  
  // Clear previous errors
  showEditValidationErrors([]);
  
  // Validate edit form
  if (!validateEditForm()) {
    showMessage('Please fix the validation errors before updating', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('project', project);
  formData.append('markdown', content);
  formData.append('voice', voice);
  formData.append('theme', theme);
  formData.append('template', template);
  if (font_size) formData.append('font_size', font_size);
  
  showMessage('💾 Updating project...', 'info');
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      showMessage(`✅ Project "${project}" updated successfully`, 'success');
      hideEditForm();
      await loadProjects();
    } else {
      // Check if server returned validation errors
      if (data.validation_errors) {
        showEditValidationErrors(data.validation_errors);
      }
      showMessage(`❌ Update failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Update error: ${e.message}`, 'error');
  }
}

// Project deletion
async function deleteProject(projectName, event) {
  if (event) event.stopPropagation();
  
  showMessage(`🗑️ Deleting "${projectName}"...`, 'info');
  
  try {
    const response = await fetch('/api/delete_project', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showMessage(`✅ Project "${projectName}" deleted successfully`, 'success');
      await loadProjects();
    } else {
      showMessage(`❌ Error: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Failed to delete project: ${e.message}`, 'error');
  }
}

// Publishing functions
async function publishToYoutube(projectName, event) {
  if (event) event.stopPropagation();
  
  showMessage('📺 Publishing to YouTube...', 'info');
  
  try {
    const response = await fetch('/api/publish/youtube', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showMessage(`✅ Published "${projectName}" to YouTube successfully`, 'success');
    } else {
      showMessage(`❌ YouTube publish failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ YouTube publish error: ${e.message}`, 'error');
  }
}

async function publishToWordPress(projectName, event) {
  if (event) event.stopPropagation();
  
  showMessage('📝 Publishing to WordPress...', 'info');
  
  try {
    const response = await fetch('/api/publish/wordpress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showMessage(`✅ Published "${projectName}" to WordPress successfully`, 'success');
    } else {
      showMessage(`❌ WordPress publish failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ WordPress publish error: ${e.message}`, 'error');
  }
}

// Version history
async function showVersionHistory(projectName) {
  try {
    const response = await fetch(`/api/project_history?project=${encodeURIComponent(projectName)}`);
    const data = await response.json();
    
    if (response.ok && data.versions) {
      const modal = document.getElementById('versionModal');
      const content = document.getElementById('versionContent');
      
      let html = `<h3>📜 Version History for "${projectName}"</h3>`;
      
      if (data.versions.length === 0) {
        html += '<p>No version history available for this project.</p>';
      } else {
        html += '<div style="max-height: 400px; overflow-y: auto;">';
        data.versions.forEach((version, index) => {
          html += `
            <div style="border: 1px solid var(--border-color); padding: 12px; margin: 8px 0; border-radius: 6px;">
              <strong>Version ${version.version || index + 1}</strong>
              <br><small>Created: ${version.created || 'Unknown'}</small>
              ${version.size ? `<br><small>Size: ${version.size} bytes</small>` : ''}
              <br>
              <button onclick="restoreVersion('${projectName}', '${version.file}')" class="btn" style="margin-top: 8px;">
                🔄 Restore This Version
              </button>
            </div>
          `;
        });
        html += '</div>';
      }
      
      content.innerHTML = html;
      modal.style.display = 'block';
    } else {
      showMessage('Failed to load version history', 'error');
    }
  } catch (e) {
    console.error('Failed to load version history:', e);
    showMessage('Failed to load version history', 'error');
  }
}

async function restoreVersion(projectName, versionFile) {
  try {
    const response = await fetch('/api/restore_version', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        project: projectName,
        version_file: versionFile
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showMessage(`✅ Restored version for "${projectName}"`, 'success');
      document.getElementById('versionModal').style.display = 'none';
      await loadProjects();
    } else {
      showMessage(`❌ Restore failed: ${data.message}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Restore error: ${e.message}`, 'error');
  }
}

// SVG auto-play functionality
function openSVGWithAutoplay(svgPath, event) {
  if (event) event.preventDefault();
  
  // Open SVG in new window with auto-play script
  const newWindow = window.open(svgPath, '_blank');
  
  // Inject auto-play script after the SVG loads
  newWindow.addEventListener('load', function() {
    const script = newWindow.document.createElement('script');
    script.textContent = `
      // Auto-play video elements in SVG
      document.addEventListener('DOMContentLoaded', function() {
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
          video.autoplay = true;
          video.play().catch(e => console.log('Auto-play prevented:', e));
        });
        
        // Also try to play videos embedded as data URIs
        const videoElements = document.querySelectorAll('[href*="data:video"]');
        videoElements.forEach(elem => {
          if (elem.tagName === 'video') {
            elem.autoplay = true;
            elem.play().catch(e => console.log('Auto-play prevented:', e));
          }
        });
      });
    `;
    newWindow.document.head.appendChild(script);
  });
}

// Project validation
async function validateProject(projectName, event) {
  if (event) event.stopPropagation();
  
  showMessage(`🔍 Validating "${projectName}"...`, 'info');
  
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
      
      showMessage(message, type);
      
      // Show detailed validation results
      if (errors.length > 0 || warnings.length > 0) {
        setTimeout(() => {
          const details = [...errors, ...warnings].join('\\n');
          showMessage(`Validation details:\\n${details}`, type);
        }, 1000);
      }
    } else {
      showMessage(`❌ Validation failed: ${data.error || data.message}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Validation error: ${e.message}`, 'error');
  }
}

// Real-time validation during editing
function validateContentRealtime(content) {
  const validationDiv = document.getElementById('validationStatus');
  if (!validationDiv) return;
  
  const errors = [];
  const warnings = [];
  
  // Basic markdown validation
  if (!content.trim()) {
    warnings.push('Content is empty');
  }
  
  // Check for basic markdown structure
  if (!content.includes('#')) {
    warnings.push('No headings found in content');
  }
  
  // Check for very long lines (readability)
  const lines = content.split('\\n');
  lines.forEach((line, index) => {
    if (line.length > 200) {
      warnings.push(`Line ${index + 1} is very long (${line.length} chars)`);
    }
  });
  
  // Update validation status
  let statusClass = 'validation-valid';
  let statusText = '✅ Valid';
  
  if (errors.length > 0) {
    statusClass = 'validation-invalid';
    statusText = `❌ ${errors.length} error(s)`;
  } else if (warnings.length > 0) {
    statusClass = 'validation-warning';
    statusText = `⚠️ ${warnings.length} warning(s)`;
  }
  
  validationDiv.className = `validation-status ${statusClass}`;
  validationDiv.textContent = statusText;
}

// Status message system
function showMessage(text, type = 'info') {
  // Remove existing message
  const existingMsg = document.getElementById('statusMessage');
  if (existingMsg) {
    existingMsg.remove();
  }
  
  // Create new message
  const msgDiv = document.createElement('div');
  msgDiv.id = 'statusMessage';
  msgDiv.textContent = text;
  msgDiv.style.cssText = `
    position: fixed; top: 20px; right: 20px; z-index: 1000;
    padding: 12px 20px; border-radius: 6px; font-weight: 500;
    max-width: 400px; word-wrap: break-word;
    background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
    color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
    border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  `;
  
  document.body.appendChild(msgDiv);
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    if (msgDiv.parentNode) {
      msgDiv.remove();
    }
  }, 3000);
}

  // Attach functions to window object to make them accessible from HTML
  window.toggleTheme = toggleTheme;
  window.switchProjectView = switchProjectView;
  window.showCreateForm = showCreateForm;
  window.hideCreateForm = hideCreateForm;
  window.showEditForm = showEditForm;
  window.hideEditForm = hideEditForm;
  window.generateProject = generateProject;
  window.editSVGProject = editSVGProject;
  window.editProject = editProject;
  window.updateProject = updateProject;
  window.deleteProject = deleteProject;
  window.validateProject = validateProject;
  window.publishToYoutube = publishToYoutube;
  window.publishToWordPress = publishToWordPress;
  window.showVersionHistory = showVersionHistory;
  window.restoreVersion = restoreVersion;
  window.openSVGWithAutoplay = openSVGWithAutoplay;
  window.selectProject = selectProject;

})();
"""

JAVASCRIPT_CODE = get_javascript_content()
