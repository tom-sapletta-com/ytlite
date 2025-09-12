#!/usr/bin/env python3
"""
JavaScript code for YTLite Web GUI
Extracted from web_gui.py for better modularity
"""

JAVASCRIPT_CODE = """
// Load existing projects on page load
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
  document.getElementById('createForm').style.display = 'block';
  document.getElementById('createForm').scrollIntoView({behavior: 'smooth'});
}

function hideCreateForm() {
  document.getElementById('createForm').style.display = 'none';
}

function showEditForm() {
  document.getElementById('editForm').style.display = 'block';
  document.getElementById('editForm').scrollIntoView({behavior: 'smooth'});
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
    statusBadge = project.svg_valid ? 
      '<span class="status-badge status-success">✓ SVG Project</span>' : 
      '<span class="status-badge status-warning">⚠ Invalid SVG</span>';
    projectPath = `/files/svg_projects/${project.svg}`;
    openAction = `<a href="${projectPath}" target="_blank" class="btn btn-primary" onclick="openSVGWithAutoplay('${projectPath}', event)">🎬 Open SVG</a>`;
    typeIcon = '📄';
    
    // Add video preview if available
    videoPreview = project.has_video ? 
      `<div><video class="video-preview" src="/files/projects/${project.name}/video.mp4" muted preload="metadata"></video></div>` : '';
    
    // Show metadata if available
    const metaInfo = project.title && project.title !== project.name ? 
      `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${project.title}</div>` : '';
    const dateInfo = project.created ? 
      `<div style="font-size: 11px; color: var(--text-muted);">📅 ${new Date(project.created).toLocaleDateString()}</div>` : '';
    
    return `<div class="project-card" onclick="selectProject('${project.name}')">
      <div class="project-title">${typeIcon} ${project.name}</div>
      <div class="project-meta">${statusBadge}${metaInfo}${dateInfo}</div>
      ${videoPreview || ''}
      <div class="project-actions">
        ${openAction}
        <button onclick="editSVGProject('${project.name}')" class="btn">✏️ Edit</button>
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
        <button onclick="editProject('${project.name}')" class="btn">✏️ Edit</button>
        ${project.versions && project.versions > 1 ? `<button onclick="showVersionHistory('${project.name}')" class="btn">📜 History</button>` : ''}
        <button onclick="publishToYoutube('${project.name}', event)" class="btn" style="background: #ff4444; color: white;">📺 YouTube</button>
        <button onclick="publishToWordPress('${project.name}', event)" class="btn" style="background: #21759b; color: white;">📝 WordPress</button>
        <button onclick="deleteProject('${project.name}', event)" class="btn btn-danger" style="margin-left: 8px;">🗑️ Delete</button>
      </div>
    </div>`;
  }
}

function renderProjectTableRow(project) {
  const statusText = project.type === 'svg' ? 
    (project.svg_valid ? '✓ SVG Project' : '⚠ Invalid SVG') :
    (project.svg ? '✓ Valid SVG' : '⚠ No SVG');
  
  const createdDate = project.created ? new Date(project.created).toLocaleDateString() : 'N/A';
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
  
  return `<tr onclick="selectProject('${project.name}')" style="cursor: pointer;">
    <td><strong>${project.name}</strong></td>
    <td>${projectType}</td>
    <td>${statusText}</td>
    <td>${createdDate}</td>
    <td onclick="event.stopPropagation()">${actions}</td>
  </tr>`;
}

// Project editing functions
async function editProject(name) {
  try {
    const res = await fetch(`/api/svg_meta?project=${name}`);
    if (res.ok) {
      const meta = await res.json();
      populateEditForm(name, meta);
      showEditForm();
    }
  } catch (e) {
    console.error('Failed to load project metadata:', e);
    showMessage('Failed to load project metadata', 'error');
  }
}

async function editSVGProject(name) {
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
  document.getElementById('editContent').value = meta.markdown_content || meta.markdown || '';
  if (meta.voice) document.getElementById('editVoice').value = meta.voice;
  if (meta.theme) document.getElementById('editTheme').value = meta.theme;
  if (meta.template) document.getElementById('editTemplate').value = meta.template;
  if (meta.font_size) document.getElementById('editFontSize').value = meta.font_size;
}

// Project generation
async function generateProject() {
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value;
  
  if (!project) { 
    showMessage('Please enter a project name', 'error'); 
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
      showMessage(`❌ Generation failed: ${data.message}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Generation error: ${e.message}`, 'error');
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
      showMessage(`❌ Update failed: ${data.message}`, 'error');
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
"""
