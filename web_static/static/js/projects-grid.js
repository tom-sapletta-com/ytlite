'use strict';

async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const container = document.getElementById('projectsContainer');
    
    if (data.projects && data.projects.length > 0) {
      container.innerHTML = '<div class="projects-grid">' + 
        data.projects.map(project => renderProjectCard(project)).join('') + '</div>';
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

function renderProjectCard(project) {
  if (project.type === 'svg') {
    const statusBadge = '<span class="status-badge">📄 SVG Project</span>';
    const projectPath = `/files/svg_projects/${project.svg}`;
    const openAction = `<a href="${projectPath}" target="_blank" class="btn btn-primary" onclick="openSVGWithAutoplay('${projectPath}', event)">🎬 Open SVG</a>`;
    const typeIcon = '📄';
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
    const statusBadge = project.svg ? '<span class="status-badge status-success">✓ Valid SVG</span>' : '<span class="status-badge status-warning">⚠ No SVG</span>';
    const versionInfo = project.versions && project.versions > 1 ? `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${project.versions} versions</div>` : '';
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
