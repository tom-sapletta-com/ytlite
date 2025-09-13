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
    initLogger();
    loadTheme();
    loadProjects();
  });

// Project view toggle functionality
let currentProjectView = 'grid';
let ws = null; // optional raw WebSocket logger
let wsReady = false;
let mqttClient = null; // optional MQTT logger
let mqttReady = false;
let mqttTopic = 'ytlite/logs';
let formHandlersAttached = false;

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

// --- Media Preview ---
async function urlExists(url) {
  try {
    const res = await fetch(url, { method: 'HEAD', cache: 'no-store' });
    return res.ok;
  } catch (e) {
    return false;
  }
}

async function updateMediaPreview(projectName) {
  const container = document.getElementById('mediaPreview');
  const body = document.getElementById('mediaPreviewBody');
  if (!container || !body) return;
  container.style.display = 'block';
  body.innerHTML = '<div>Loading preview…</div>';

  const items = [
    { key: 'thumb', label: 'Thumbnail', url: `/files/thumbnails/${projectName}.jpg` },
    { key: 'video', label: 'Video', url: `/files/videos/${projectName}.mp4` },
    { key: 'audio', label: 'Audio', url: `/files/audio/${projectName}.mp3` },
    { key: 'svg', label: 'SVG', url: `/files/svg_projects/${projectName}.svg` },
  ];

  const blocks = [];
  for (const it of items) {
    const ok = await urlExists(it.url);
    if (!ok) continue;
    if (it.key === 'thumb') {
      blocks.push(`<div class="media-item"><h4>🖼️ ${it.label}</h4><img class="thumb" src="${it.url}" alt="thumbnail"></div>`);
    } else if (it.key === 'video') {
      blocks.push(`<div class="media-item"><h4>🎬 ${it.label}</h4><video class="thumb" src="${it.url}" controls></video></div>`);
    } else if (it.key === 'audio') {
      blocks.push(`<div class="media-item"><h4>🔊 ${it.label}</h4><audio src="${it.url}" controls></audio></div>`);
    } else if (it.key === 'svg') {
      blocks.push(`<div class="media-item"><h4>📄 ${it.label}</h4><a href="${it.url}" target="_blank" class="btn">Open SVG</a></div>`);
    }
  }

  if (blocks.length === 0) {
    body.innerHTML = `
      <div>No media files found for this project yet.</div>
      <button onclick="generateMedia('${projectName}')" class="btn btn-primary" style="margin-top:10px;">
        🎬 Generate Missing Media
      </button>
    `;
    logEvent(`Media preview: no files found for ${projectName}`, 'warn');
  } else {
    body.innerHTML = blocks.join('');
    logEvent(`Media preview updated for ${projectName}`, 'info', {count: blocks.length});
  }
}

// Expose immediately after definition to avoid scope issues
window.updateMediaPreview = updateMediaPreview;

function loadMqttLib() {
  return new Promise((resolve, reject) => {
    if (window.mqtt) return resolve();
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/mqtt/dist/mqtt.min.js';
    s.onload = () => resolve();
    s.onerror = () => reject(new Error('Failed to load mqtt.js'));
    document.head.appendChild(s);
  });
}

function tryOpenMqtt(url, topic) {
  try {
    if (!window.mqtt) throw new Error('mqtt lib not loaded');
    mqttClient = window.mqtt.connect(url);
    mqttClient.on('connect', () => { mqttReady = true; logEvent(`MQTT connected to ${url}`, 'info', {topic}); });
    mqttClient.on('error', () => { mqttReady = false; logEvent('MQTT error (non-fatal)', 'warn'); });
    mqttClient.on('close', () => { mqttReady = false; logEvent('MQTT closed', 'warn'); });
  } catch (e) {
    logEvent('MQTT init failed', 'warn');
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

// --- Lightweight logging panel and optional WS publisher ---
function initLogger() {
  try {
    // Create log panel
    if (!document.getElementById('logPanel')) {
      const panel = document.createElement('div');
      panel.id = 'logPanel';
      panel.style.cssText = `
        position: fixed; bottom: 10px; left: 10px; z-index: 999;
        width: 420px; max-height: 180px; overflow:auto; font-size: 12px;
        background: rgba(0,0,0,0.6); color: #fff; padding: 8px 10px; border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      `;
      panel.innerHTML = '<div style="font-weight:600; margin-bottom:4px;">Logs</div><div id="logPanelBody"></div>';
      document.body.appendChild(panel);
    }

    // Try to fetch config for optional WS
    fetch('/api/config').then(r => r.json()).then(cfg => {
      if (cfg && cfg.mqtt_ws_url) {
        mqttTopic = cfg.mqtt_ws_topic || 'ytlite/logs';
        // Try MQTT first (via CDN), then fallback to raw WS if MQTT lib fails
        loadMqttLib().then(() => {
          tryOpenMqtt(cfg.mqtt_ws_url, mqttTopic);
        }).catch(() => {
          tryOpenWs(cfg.mqtt_ws_url, mqttTopic);
        });
      }
    }).catch(() => {/* ignore */});
  } catch (e) {
    console.warn('Logger init failed', e);
  }
}

function logEvent(message, level = 'info', context = {}) {
  const body = document.getElementById('logPanelBody');
  const ts = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  line.textContent = `[${ts}] ${level.toUpperCase()}: ${message}`;
  body && body.appendChild(line);
  if (body) body.scrollTop = body.scrollHeight;
  // try publish to MQTT if connected
  if (mqttReady && mqttClient) {
    try {
      const payload = JSON.stringify({t: Date.now(), level, message, context});
      mqttClient.publish(mqttTopic, payload);
    } catch (e) { /* ignore */ }
  }
  // else try raw WS if connected
  if (wsReady && ws) {
    try {
      const payload = JSON.stringify({t: Date.now(), level, message, context});
      ws.send(payload);
    } catch (e) { /* ignore */ }
  }
}

function tryOpenWs(url, topic) {
  try {
    ws = new WebSocket(url);
    ws.onopen = () => { wsReady = true; logEvent(`WS connected to ${url}`, 'info', {topic}); };
    ws.onerror = (e) => { logEvent('WS error (non-fatal, proceeding without WS)', 'warn'); };
    ws.onclose = () => { wsReady = false; logEvent('WS closed', 'warn'); };
  } catch (e) {
    logEvent('WS init failed', 'warn');
  }
}

// Ensure a select element contains a given value; if not, append a temporary option and select it
function ensureSelectValue(selectId, value) {
  const sel = document.getElementById(selectId);
  if (!sel || value == null) return;
  const strVal = String(value);
  const existing = Array.from(sel.options).find(o => o.value === strVal);
  if (!existing) {
    const opt = document.createElement('option');
    opt.value = strVal;
    opt.textContent = strVal;
    opt.setAttribute('data-custom', '1');
    sel.appendChild(opt);
    logEvent(`Added custom option to #${selectId}: ${strVal}`, 'warn');
  }
  sel.value = strVal;
}

// Form management
function showProjectForm() {
  const form = document.getElementById('projectForm');
  form.style.display = 'block';
  form.scrollIntoView({behavior: 'smooth'});
  if (!formHandlersAttached) {
    const contentEl = document.getElementById('content');
    contentEl.addEventListener('input', () => {
      const proj = document.getElementById('project').value.trim();
      if (proj) {
        localStorage.setItem(`ytlite:content:${proj}`, contentEl.value);
      }
    });
    formHandlersAttached = true;
  }
}

function hideProjectForm() {
  document.getElementById('projectForm').style.display = 'none';
  const mp = document.getElementById('mediaPreview');
  if (mp) mp.style.display = 'none';
}

function showFormForCreate() {
  document.getElementById('form-title').textContent = '📝 Create New Project';
  document.getElementById('project').readOnly = false;
  document.getElementById('project').value = '';
  document.getElementById('content').value = '';
  document.getElementById('generateBtn').style.display = 'inline-flex';
  document.getElementById('updateBtn').style.display = 'none';
  showProjectForm();
  const mp = document.getElementById('mediaPreview');
  const mpb = document.getElementById('mediaPreviewBody');
  if (mp) mp.style.display = 'none';
  if (mpb) mpb.innerHTML = '';
  // Set defaults for selects
  const theme = document.getElementById('theme');
  const template = document.getElementById('template');
  const voice = document.getElementById('voice');
  const fontSize = document.getElementById('font_size');
  if (theme) theme.value = 'default';
  if (template) template.value = 'simple';
  if (voice) voice.value = 'en-US';
  if (fontSize) fontSize.value = 'medium';
}

function showFormForEdit() {
  document.getElementById('form-title').textContent = '✏️ Edit Project';
  document.getElementById('project').readOnly = true;
  document.getElementById('generateBtn').style.display = 'none';
  document.getElementById('updateBtn').style.display = 'inline-flex';
  showProjectForm();
}

function selectProject(name) {
  // When a project card is clicked, open the form in edit mode for that project.
  editProject(name);
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
  
  // Show form immediately with loading state
  showFormForEdit();
  document.getElementById('project').value = name;
  document.getElementById('content').value = 'Loading...';
  window.updateMediaPreview && window.updateMediaPreview(name);

  try {
    const res = await fetch(`/api/svg_metadata?project=${name}`);
    if (res.ok) {
      const data = await res.json();
      const metaData = data.metadata || data;
      logEvent(`Loaded metadata for ${name}`, 'info', {fields: Object.keys(metaData || {})});
      populateProjectForm(name, metaData);
      const contentEl = document.getElementById('content');
      // Fallback if content still missing
      if (!contentEl.value || contentEl.value === 'Loading...') {
        await fetchProjectMarkdown(name);
      }
      // Refresh preview just in case files changed
      window.updateMediaPreview && window.updateMediaPreview(name);
    } else {
        document.getElementById('content').value = 'Error: Failed to load project data.';
        showMessage('Failed to load project metadata', 'error');
    }
  } catch (e) {
    console.error('Failed to load project metadata:', e);
    document.getElementById('content').value = 'Error: Failed to load project data.';
    showMessage('Failed to load project metadata', 'error');
  }
}

// editSVGProject is now an alias for editProject
const editSVGProject = editProject;

function populateProjectForm(name, meta) {
  document.getElementById('project').value = name;
  
  const candidate = meta.markdown_content || meta.markdown || meta.content || meta.description;
  if (candidate && String(candidate).trim().length > 0) {
    document.getElementById('content').value = candidate;
    localStorage.setItem(`ytlite:content:${name}`, candidate);
    logEvent(`Content loaded from metadata for ${name} (${candidate.length} chars)`, 'info');
  } else {
    // Try cached content
    const cached = localStorage.getItem(`ytlite:content:${name}`) || '';
    if (cached) {
      document.getElementById('content').value = cached;
      logEvent(`Content restored from cache for ${name} (${cached.length} chars)`, 'warn');
    } else {
      logEvent(`No content found in metadata for ${name}`, 'warn', {available: Object.keys(meta)});
    }
  }
  
  if (meta.voice) ensureSelectValue('voice', meta.voice);
  if (meta.theme) ensureSelectValue('theme', meta.theme);
  if (meta.template) ensureSelectValue('template', meta.template);
  if (meta.font_size) ensureSelectValue('font_size', meta.font_size);
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
  logEvent(`Generate start for ${project}`, 'info');
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      let successMsg = `✅ Project "${project}" generated successfully.`;
      if (data.validation && data.validation.message) {
        successMsg += ` ${data.validation.message}`;
      }
      showMessage(successMsg, data.validation && data.validation.valid ? 'success' : 'warning');
      localStorage.setItem(`ytlite:content:${project}`, content);
      logEvent(`Generate done for ${project}`, 'success', {validation: data.validation || null});
      // Refresh media preview to show new files
      window.updateMediaPreview && window.updateMediaPreview(project);
      hideProjectForm();
      await loadProjects();
    } else {
      // Check if server returned validation errors
      if (data.validation_errors) {
        showValidationErrors(data.validation_errors);
      }
      showMessage(`❌ Generation failed: ${data.message || data.error}`, 'error');
      logEvent(`Generate failed for ${project}: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Generation error: ${e.message}`, 'error');
    logEvent(`Generate error for ${project}: ${e.message}`, 'error');
  }
}


async function updateProject() {
  // This function now reads from the main unified form
  const project = document.getElementById('project').value.trim();
  const content = document.getElementById('content').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value;
  const force_regenerate = document.getElementById('force_regenerate').checked;
  
  if (!project) return;
  
  // Clear previous errors
  showValidationErrors([]);

  // Re-use the main validation logic
  if (!validateAllFields()) {
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
  formData.append('force_regenerate', force_regenerate);
  
  showMessage('💾 Updating project...', 'info');
  logEvent(`Update start for ${project}`, 'info');
  
  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (res.ok) {
      let successMsg = `✅ Project "${project}" updated successfully.`;
      if (data.validation && data.validation.message) {
        successMsg += ` ${data.validation.message}`;
      }
      showMessage(successMsg, data.validation && data.validation.valid ? 'success' : 'warning');
      localStorage.setItem(`ytlite:content:${project}`, content);
      logEvent(`Update done for ${project}`, 'success', {validation: data.validation || null});
      // Refresh media preview to show new files
      window.updateMediaPreview && window.updateMediaPreview(project);
      hideProjectForm();
      await loadProjects();
    } else {
      // Check if server returned validation errors
      if (data.validation_errors) {
        showValidationErrors(data.validation_errors);
      }
      showMessage(`❌ Update failed: ${data.message || data.error}`, 'error');
      logEvent(`Update failed for ${project}: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Update error: ${e.message}`, 'error');
    logEvent(`Update error for ${project}: ${e.message}`, 'error');
  }
}

async function fetchProjectMarkdown(name) {
  try {
    // Try primary .md then fallback to description.md
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
          logEvent(`Content loaded from ${p} for ${name} (${text.length} chars)`, 'info');
          return true;
        }
      }
    }
    logEvent(`No markdown file found for ${name}`, 'warn');
    return false;
  } catch (e) {
    logEvent(`Failed to fetch markdown for ${name}: ${e.message}`, 'error');
    return false;
  }
}

async function generateMedia(projectName) {
  if (!projectName) return;
  showMessage(`🎬 Generating media for ${projectName}...`, 'info');
  logEvent(`Media generation start for ${projectName}`, 'info');
  try {
    const res = await fetch('/api/generate_media', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ project: projectName })
    });
    const data = await res.json();
    if (res.ok) {
      showMessage(`✅ Media for "${projectName}" generated successfully.`, 'success');
      logEvent(`Media generation done for ${projectName}`, 'success', { files: data.files_generated });
      // Refresh the preview to show the new files
      updateMediaPreview(projectName);
    } else {
      showMessage(`❌ Media generation failed: ${data.message || data.error}`, 'error');
      logEvent(`Media generation failed for ${projectName}: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Media generation error: ${e.message}`, 'error');
    logEvent(`Media generation error for ${projectName}: ${e.message}`, 'error');
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
  // Also pipe to log panel
  logEvent(text, type);
  
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
  window.showFormForCreate = showFormForCreate;
  window.hideProjectForm = hideProjectForm;
  window.generateProject = generateProject;
  window.updateProject = updateProject;
  window.deleteProject = deleteProject;
  window.validateProject = validateProject;
  window.publishToYoutube = publishToYoutube;
  window.publishToWordPress = publishToWordPress;
  window.showVersionHistory = showVersionHistory;
  window.restoreVersion = restoreVersion;
  window.openSVGWithAutoplay = openSVGWithAutoplay;
  window.selectProject = selectProject;
  // Expose validators and edit handlers used by inline HTML attributes
  window.validateField = validateField;
  window.validateAllFields = validateAllFields;
  window.editProject = editProject;
  window.editSVGProject = editSVGProject;
  window.generateMedia = generateMedia;

})();
"""

JAVASCRIPT_CODE = get_javascript_content()
