#!/usr/bin/env python3
"""
JavaScript Projects Module for YTLite Web GUI
"""

def get_projects_js():
    """Return JavaScript code for projects functionality."""
    return """
// Project view toggle functionality
let currentProjectView = 'grid';

function switchProjectView(view) {
  currentProjectView = view;
  const gridBtn = document.getElementById('grid-btn');
  const tableBtn = document.getElementById('table-btn');
  const gridContainer = document.getElementById('projects-grid');
  const tableContainer = document.getElementById('projects-table');
  
  if (view === 'grid') {
    if (gridBtn) gridBtn.classList.add('active');
    if (tableBtn) tableBtn.classList.remove('active');
    if (gridContainer) gridContainer.style.display = 'grid';
    if (tableContainer) tableContainer.style.display = 'none';
    loadProjects();
  } else {
    if (tableBtn) tableBtn.classList.add('active');
    if (gridBtn) gridBtn.classList.remove('active');
    if (tableContainer) tableContainer.style.display = 'block';
    if (gridContainer) gridContainer.style.display = 'none';
    loadProjectsTable();
  }
}

// Project loading functions
async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const container = document.getElementById('projects-grid');
    if (!container) return;
    
    if (!data.projects || data.projects.length === 0) {
      container.innerHTML = '<div class="no-projects">No projects found. Create your first project!</div>';
      return;
    }
    
    container.innerHTML = data.projects.map(renderProjectCard).join('');
    logEvent(`Loaded ${data.projects.length} projects`, 'info');
  } catch (error) {
    logEvent(`Failed to load projects: ${error.message}`, 'error');
    const container = document.getElementById('projects-grid');
    if (container) container.innerHTML = '<div class="error">Failed to load projects</div>';
  }
}

async function loadProjectsTable() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const tbody = document.querySelector('#projects-table tbody');
    if (!tbody) return;
    
    if (!data.projects || data.projects.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5">No projects found</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.projects.map(renderProjectTableRow).join('');
  } catch (error) {
    logEvent(`Failed to load projects table: ${error.message}`, 'error');
  }
}

function renderProjectCard(project) {
  let statusBadge, projectPath, openAction, typeIcon, videoPreview;
  
  if (project.type === 'svg') {
    statusBadge = '<span class="status-badge svg">📄 SVG</span>';
    projectPath = `svg_projects/${project.name}.svg`;
    openAction = `openSVGWithAutoplay('${projectPath}', event)`;
    typeIcon = '📄';
    videoPreview = '';
  } else {
    statusBadge = '<span class="status-badge directory">📁 Directory</span>';
    projectPath = `projects/${project.name}`;
    openAction = `editProject('${project.name}', event)`;
    typeIcon = '📁';
    
    // Add video preview if available
    const videoExists = project.video_exists || false;
    if (videoExists) {
      videoPreview = `
        <div class="video-preview">
          <video class="project-video" poster="/files/thumbnails/${project.name}.jpg" onclick="this.play()">
            <source src="/files/videos/${project.name}.mp4" type="video/mp4">
          </video>
        </div>`;
    } else {
      videoPreview = `
        <div class="video-placeholder" onclick="${openAction}">
          <div class="placeholder-content">
            <div class="placeholder-icon">${typeIcon}</div>
            <div class="placeholder-text">Click to ${project.type === 'svg' ? 'open' : 'edit'}</div>
          </div>
        </div>`;
    }
  }
  
  return `
  <div class="project-card" onclick="${openAction}">
    <div class="project-header">
      <h3 class="project-title">${project.name}</h3>
      ${statusBadge}
    </div>
    ${videoPreview}
    <div class="project-actions">
      <button onclick="editProject('${project.name}', event)" class="btn-small">✏️ Edit</button>
      <button onclick="deleteProject('${project.name}', event)" class="btn-small btn-danger">🗑️ Delete</button>
      <button onclick="validateProject('${project.name}', event)" class="btn-small">✅ Validate</button>
    </div>
  </div>`;
}

function renderProjectTableRow(project) {
  const statusText = project.type === 'svg' ? '📄 SVG Project' : '📁 Directory';
  const createdDate = '...'; // Placeholder
  const projectType = project.type === 'svg' ? '📄 SVG' : '📁 Directory';
  
  return `
  <tr onclick="editProject('${project.name}', event)" style="cursor: pointer;">
    <td><strong>${project.name}</strong></td>
    <td>${statusText}</td>
    <td>${createdDate}</td>
    <td>${projectType}</td>
    <td class="actions-cell">
      <button onclick="editProject('${project.name}', event)" class="btn-small">✏️</button>
      <button onclick="deleteProject('${project.name}', event)" class="btn-small btn-danger">🗑️</button>
      <button onclick="validateProject('${project.name}', event)" class="btn-small">✅</button>
      <button onclick="publishToYoutube('${project.name}', event)" class="btn-small">📺</button>
      <button onclick="publishToWordPress('${project.name}', event)" class="btn-small">📝</button>
      <button onclick="showVersionHistory('${project.name}', event)" class="btn-small">📚</button>
    </td>
  </tr>`;
}

function selectProject(name) {
  editProject(name);
}

async function loadProjectMetadata(projectName) {
  try {
    const res = await fetch(`/api/svg_meta?project=${projectName}`);
    if (!res.ok) return;
    const meta = await res.json();
    
    if (meta.title) {
      document.getElementById('project-title').textContent = meta.title;
    }
    
    // Show metadata in a nice format
    const metaContainer = document.getElementById('project-metadata');
    if (metaContainer && meta) {
      const metaHtml = Object.entries(meta)
        .filter(([key, value]) => value && key !== 'markdown_content')
        .map(([key, value]) => `<div><strong>${key}:</strong> ${value}</div>`)
        .join('');
      metaContainer.innerHTML = metaHtml;
    }
    
    return meta;
  } catch (error) {
    logEvent(`Failed to load metadata for ${projectName}: ${error.message}`, 'error');
    return null;
  }
}

window.switchProjectView = switchProjectView;
window.loadProjects = loadProjects;
window.loadProjectsTable = loadProjectsTable;
window.renderProjectCard = renderProjectCard;
window.renderProjectTableRow = renderProjectTableRow;
window.selectProject = selectProject;
window.loadProjectMetadata = loadProjectMetadata;
"""
