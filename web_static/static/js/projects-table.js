'use strict';

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

function renderProjectTableRow(project) {
  const statusText = project.type === 'svg' ? '📄 SVG Project' : '📁 Directory';
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
    <td id="project-date-${project.name}">...</td>
    <td onclick="event.stopPropagation()">${actions}</td>
  </tr>`;
}
