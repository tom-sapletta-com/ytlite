#!/usr/bin/env python3
"""
YTLite Web GUI
- Generate a single project in real time with preview
- Load per-project .env (uploaded or existing in output/projects/<name>/.env)
- Publish project to WordPress
- Fetch content from Nextcloud

Run: python3 -u src/web_gui.py
Open: http://localhost:5000
Optionally also run: make preview (serves /output over nginx)
"""
from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from dotenv import load_dotenv
from rich.console import Console

from dependencies import verify_dependencies
from ytlite_main import YTLite
from wordpress_publisher import WordPressPublisher
from storage_nextcloud import NextcloudClient
from logging_setup import get_logger
from progress import load_progress
from svg_packager import parse_svg_meta, update_svg_media
from svg_datauri_packager import SVGDataURIPackager, create_svg_project

console = Console()
app = Flask(__name__)
logger = get_logger("web_gui")
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'output'

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <title>YTLite Web GUI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg-primary: #ffffff;
      --bg-secondary: #f8f9fa;
      --bg-accent: #f5f5f5;
      --text-primary: #212529;
      --text-secondary: #6c757d;
      --text-muted: #adb5bd;
      --border-color: #dee2e6;
      --border-hover: #00ff88;
      --shadow: rgba(0, 0, 0, 0.1);
      --shadow-hover: rgba(0, 255, 136, 0.2);
      --btn-primary: #00ff88;
      --btn-primary-hover: #00cc66;
      --btn-secondary: #6c757d;
      --btn-danger: #dc3545;
      --success: #28a745;
      --warning: #ffc107;
      --danger: #dc3545;
    }
    
    [data-theme="dark"] {
      --bg-primary: #1a1a1a;
      --bg-secondary: #2d2d2d;
      --bg-accent: #343a40;
      --text-primary: #ffffff;
      --text-secondary: #adb5bd;
      --text-muted: #6c757d;
      --border-color: #495057;
      --shadow: rgba(255, 255, 255, 0.1);
      --shadow-hover: rgba(0, 255, 136, 0.3);
    }
    
    * { box-sizing: border-box; }
    
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      margin: 0; 
      padding: 20px;
      background: var(--bg-accent);
      color: var(--text-primary);
      line-height: 1.6;
      transition: all 0.3s ease;
    }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      padding: 20px 0;
    }
    
    .header h1 {
      margin: 0;
      background: linear-gradient(45deg, #00ff88, #007acc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-size: 2.5rem;
      font-weight: 700;
    }
    
    .theme-toggle {
      padding: 10px 16px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      color: var(--text-primary);
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .theme-toggle:hover {
      background: var(--bg-primary);
      border-color: var(--border-hover);
    }
    
    .box { 
      border: 1px solid var(--border-color); 
      padding: 24px; 
      margin-bottom: 24px; 
      border-radius: 12px; 
      background: var(--bg-primary);
      box-shadow: 0 2px 8px var(--shadow);
      transition: all 0.2s;
    }
    
    .box:hover {
      box-shadow: 0 4px 16px var(--shadow);
    }
    
    .box h2 {
      margin-top: 0;
      margin-bottom: 20px;
      color: var(--text-primary);
      font-size: 1.5rem;
      font-weight: 600;
    }
    
    label { 
      display: block; 
      margin-top: 16px; 
      margin-bottom: 6px;
      font-weight: 600; 
      color: var(--text-primary);
      font-size: 14px;
    }
    
    textarea, input[type=text], select { 
      width: 100%; 
      padding: 12px 16px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      background: var(--bg-secondary);
      color: var(--text-primary);
      font-size: 14px;
      transition: all 0.2s;
      font-family: inherit;
    }
    
    textarea { height: 200px; resize: vertical; }
    
    textarea:focus, input[type=text]:focus, select:focus {
      outline: none;
      border-color: var(--border-hover);
      box-shadow: 0 0 0 3px var(--shadow-hover);
    }
    
    .row { display: flex; gap: 20px; margin-top: 16px; }
    .col { flex: 1; }
    
    .projects-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
      gap: 20px; 
      margin-top: 24px; 
    }
    
    .project-card { 
      border: 1px solid var(--border-color); 
      border-radius: 12px; 
      padding: 20px; 
      background: var(--bg-primary); 
      cursor: pointer; 
      transition: all 0.2s;
      position: relative;
      overflow: hidden;
    }
    
    .project-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--btn-primary), #007acc);
      transform: translateX(-100%);
      transition: transform 0.3s ease;
    }
    
    .project-card:hover::before {
      transform: translateX(0);
    }
    
    .project-card:hover { 
      border-color: var(--border-hover); 
      box-shadow: 0 8px 24px var(--shadow-hover);
      transform: translateY(-2px);
    }
    
    .project-title { 
      font-size: 18px; 
      font-weight: 600; 
      color: var(--text-primary); 
      margin-bottom: 8px; 
    }
    
    .project-meta { 
      font-size: 14px; 
      color: var(--text-secondary); 
      margin-bottom: 16px; 
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .project-actions { 
      display: flex; 
      gap: 8px; 
      flex-wrap: wrap;
    }
    
    .btn { 
      padding: 8px 16px; 
      border: 1px solid var(--border-color); 
      background: var(--bg-secondary); 
      border-radius: 6px; 
      cursor: pointer; 
      text-decoration: none; 
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s;
      color: var(--text-primary);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    
    .btn:hover { 
      background: var(--bg-primary); 
      border-color: var(--border-hover);
      transform: translateY(-1px);
    }
    
    .btn-primary { 
      background: var(--btn-primary); 
      border-color: var(--btn-primary); 
      color: white; 
    }
    
    .btn-primary:hover { 
      background: var(--btn-primary-hover); 
      border-color: var(--btn-primary-hover);
    }
    
    .btn-danger {
      background: var(--btn-danger);
      border-color: var(--btn-danger);
      color: white;
    }
    
    .btn-danger:hover {
      background: #c82333;
      border-color: #c82333;
    }
    
    .create-new { 
      background: linear-gradient(135deg, var(--btn-primary) 0%, #007acc 100%);
      color: white; 
      padding: 30px; 
      text-align: center; 
      border-radius: 12px; 
      margin-bottom: 24px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 16px var(--shadow);
    }
    
    .create-new:hover { 
      transform: translateY(-2px);
      box-shadow: 0 8px 24px var(--shadow-hover);
    }
    
    .create-new h2 {
      margin: 0 0 12px 0;
      font-size: 1.8rem;
      font-weight: 600;
    }
    
    .create-new p {
      margin: 0;
      opacity: 0.9;
      font-size: 16px;
    }
    
    .progress-container {
      margin-top: 20px;
      padding: 16px;
      background: var(--bg-secondary);
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }
    
    progress { 
      width: 100%; 
      height: 8px; 
      border-radius: 4px;
      -webkit-appearance: none;
      appearance: none;
    }
    
    progress::-webkit-progress-bar {
      background-color: var(--bg-accent);
      border-radius: 4px;
    }
    
    progress::-webkit-progress-value {
      background: linear-gradient(90deg, var(--btn-primary), #007acc);
      border-radius: 4px;
    }
    
    .status-badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .status-success {
      background: rgba(40, 167, 69, 0.1);
      color: var(--success);
      border: 1px solid rgba(40, 167, 69, 0.2);
    }
    
    .status-warning {
      background: rgba(255, 193, 7, 0.1);  
      color: var(--warning);
      border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .version-history {
      margin-top: 12px;
    }
    
    .version-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      margin: 4px 0;
      background: var(--bg-secondary);
      border-radius: 6px;
      font-size: 13px;
    }
    
    @media (max-width: 768px) {
      body { padding: 16px; }
      .header { flex-direction: column; gap: 16px; }
      .header h1 { font-size: 2rem; }
      .row { flex-direction: column; gap: 16px; }
      .projects-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎬 YTLite Projects</h1>
    <button class="theme-toggle" onclick="toggleTheme()">
      <span id="theme-icon">🌙</span>
      <span id="theme-text">Dark Mode</span>
    </button>
  </div>
  
  <div class="create-new" onclick="showCreateForm()">
    <h2>➕ Create New Project</h2>
    <p>Generate video content with AI voice and custom themes</p>
  </div>
  
  <div id="existingProjects" class="box">
    <h2>📁 Existing Projects</h2>
    <div id="projectsList">Loading projects...</div>
  </div>

  <div id="createForm" class="box" style="display:none;">
    <h2>1) Create New Project</h2>
    <label>Project name</label>
    <input id="project" type="text" placeholder="np. my_project" />

    <label>Markdown content</label>
    <textarea id="markdown" placeholder="---\ntitle: Mój Film\ndate: 2025-01-01\n---\n\nTreść filmu...\n"></textarea>

    <div class="row">
      <div class="col">
        <label>Voice</label>
        <select id="voice">
          <option value="pl-PL-MarekNeural">pl-PL-MarekNeural</option>
          <option value="pl-PL-ZofiaNeural">pl-PL-ZofiaNeural</option>
          <option value="de-DE-KillianNeural">de-DE-KillianNeural</option>
          <option value="de-DE-KatjaNeural">de-DE-KatjaNeural</option>
          <option value="en-US-GuyNeural">en-US-GuyNeural</option>
          <option value="en-US-AriaNeural">en-US-AriaNeural</option>
        </select>
      </div>
      <div class="col">
        <label>Theme</label>
        <select id="theme">
          <option value="tech">tech</option>
          <option value="philosophy">philosophy</option>
          <option value="wetware">wetware</option>
        </select>
      </div>
      <div class="col">
        <label>Template</label>
        <select id="template">
          <option value="classic">classic</option>
          <option value="gradient">gradient</option>
          <option value="boxed">boxed</option>
          <option value="left">left</option>
        </select>
      </div>
      <div class="col">
        <label>Font size</label>
        <input id="font_size" type="text" placeholder="48" />
      </div>
      <div class="col">
        <label>Lang</label>
        <input id="lang" type="text" placeholder="pl" />
      </div>
    </div>

    <label>Upload .env (optional, per-project)</label>
    <input id="envfile" type="file" accept=".env" />

    <div class="row">
      <div class="col">
        <button onclick="generate()">Generate</button>
        <button onclick="publishWP()">Publish to WordPress</button>
      </div>
      <div class="col" style="text-align:right">
        <a href="/output-index" target="_blank">Open Output Index</a>
      </div>
    </div>
  </div>

  <div class="box">
    <h2>2) Nextcloud (optional)</h2>
    <label>Remote path (e.g. /YT/content/sample.md)</label>
    <input id="ncpath" type="text" placeholder="/path/to/file.md" />
    <button onclick="fetchNC()">Fetch to content/episodes/</button>
  </div>

  <div class="box" id="progressBox" style="display:none">
    <h2>Progress</h2>
    <div id="progmsg">Waiting...</div>
    <progress id="progbar" value="0" max="100"></progress>
  </div>

  <div class="box">
    <h2>3) WordPress (optional, multiple targets)</h2>
    <label>WordPress URL</label>
    <input id="wp_url" type="text" placeholder="https://example.com" />
    <label>Username</label>
    <input id="wp_user" type="text" />
    <label>App Password</label>
    <input id="wp_pass" type="text" />
  </div>

  <div class="box preview" id="preview" style="display:none">
    <h2>Preview</h2>
    <div id="links"></div>
    <video id="vid" controls preload="metadata" style="max-width: 100%; height: auto;">
      <p>Your browser does not support HTML video. <a href="#" id="vid-fallback">Download video</a></p>
    </video>
    <div><img id="thumb" alt="thumbnail" style="max-width:360px;margin-top:8px;"/></div>
  </div>

  <!-- Version History Modal -->
  <div id="versionModal" class="box" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); z-index:1000; max-width:600px; max-height:80vh; overflow-y:auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
    <button onclick="document.getElementById('versionModal').style.display='none'" style="float:right; background:var(--btn-danger); color:white; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">✕ Close</button>
    <div id="versionContent"></div>
  </div>

<script>
// Load existing projects on page load
document.addEventListener('DOMContentLoaded', function() {
  loadTheme();
  loadProjects();
});

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

async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const container = document.getElementById('projectsList');
    
    if (data.projects && data.projects.length > 0) {
      container.innerHTML = '<div class="projects-grid">' + 
        data.projects.map(project => {
          // Different handling for SVG vs directory projects
          let statusBadge, projectPath, openAction, typeIcon;
          
          if (project.type === 'svg') {
            statusBadge = project.svg_valid ? 
              '<span class="status-badge status-success">✓ SVG Project</span>' : 
              '<span class="status-badge status-warning">⚠ Invalid SVG</span>';
            projectPath = `/files/svg_projects/${project.svg}`;
            openAction = `<a href="${projectPath}" target="_blank" class="btn btn-primary">🎬 Open SVG</a>`;
            typeIcon = '📄';
            
            // Show metadata if available
            const metaInfo = project.title && project.title !== project.name ? 
              `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${project.title}</div>` : '';
            const dateInfo = project.created ? 
              `<div style="font-size: 11px; color: var(--text-muted);">📅 ${new Date(project.created).toLocaleDateString()}</div>` : '';
            
            return `<div class="project-card" onclick="selectProject('${project.name}')">
              <div class="project-title">${typeIcon} ${project.name}</div>
              <div class="project-meta">${statusBadge}${metaInfo}${dateInfo}</div>
              <div class="project-actions">
                ${openAction}
                <button onclick="editSVGProject('${project.name}')" class="btn">✏️ Edit</button>
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
                <button onclick="deleteProject('${project.name}', event)" class="btn btn-danger" style="margin-left: 8px;">🗑️ Delete</button>
              </div>
            </div>`;
          }
        }).join('') + '</div>';
    } else {
      container.innerHTML = '<p>No projects found. Create your first project!</p>';
    }
  } catch (e) {
    console.error('Failed to load projects:', e);
    document.getElementById('projectsList').innerHTML = '<p>Error loading projects.</p>';
  }
}

function showCreateForm() {
  document.getElementById('createForm').style.display = '';
  document.getElementById('createForm').scrollIntoView({behavior: 'smooth'});
}

function selectProject(name) {
  document.getElementById('project').value = name;
  showCreateForm();
}

async function editProject(name) {
  try {
    const res = await fetch(`/api/svg_meta?project=${name}`);
    if (res.ok) {
      const meta = await res.json();
      document.getElementById('project').value = name;
      document.getElementById('markdown').value = meta.markdown || '';
      if (meta.voice) document.getElementById('voice').value = meta.voice;
      if (meta.theme) document.getElementById('theme').value = meta.theme;
      if (meta.template) document.getElementById('template').value = meta.template;
      if (meta.font_size) document.getElementById('font_size').value = meta.font_size;
      if (meta.lang) document.getElementById('lang').value = meta.lang;
      showCreateForm();
    }
  } catch (e) {
    console.error('Failed to load project metadata:', e);
  }
}

async function editSVGProject(name) {
  try {
    const res = await fetch(`/api/svg_metadata?project=${name}`);
    if (res.ok) {
      const data = await res.json();
      const meta = data.metadata || {};
      
      document.getElementById('project').value = name;
      document.getElementById('markdown').value = meta.markdown_content || '';
      if (meta.voice) document.getElementById('voice').value = meta.voice;
      if (meta.theme) document.getElementById('theme').value = meta.theme;
      if (meta.template) document.getElementById('template').value = meta.template;
      if (meta.font_size) document.getElementById('font_size').value = meta.font_size;
      if (meta.language) document.getElementById('lang').value = meta.language;
      
      showCreateForm();
    }
  } catch (e) {
    console.error('Failed to load SVG project metadata:', e);
    alert('Failed to load project metadata');
  }
}

async function generate() {
  const project = document.getElementById('project').value.trim();
  const markdown = document.getElementById('markdown').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value.trim();
  const lang = document.getElementById('lang').value.trim();
  const envfile = document.getElementById('envfile').files[0];
  if (!project) { alert('Podaj nazwę projektu'); return; }
  const fd = new FormData();
  fd.append('project', project);
  fd.append('markdown', markdown);
  fd.append('voice', voice);
  fd.append('theme', theme);
  fd.append('template', template);
  if (font_size) fd.append('font_size', font_size);
  if (lang) fd.append('lang', lang);
  if (envfile) fd.append('env', envfile);
  document.getElementById('progressBox').style.display = '';
  const timer = setInterval(async () => {
    try {
      const pr = await fetch(`/api/progress?project=${encodeURIComponent(project)}`);
      if (pr.ok) {
        const p = await pr.json();
        document.getElementById('progmsg').textContent = p.message || p.step || '';
        document.getElementById('progbar').value = p.percent || 0;
      }
    } catch (e) {}
  }, 500);

  const res = await fetch('/api/generate', { method:'POST', body: fd });
  const data = await res.json();
  clearInterval(timer);
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  
  document.getElementById('progressBox').style.display = 'none';
  document.getElementById('progmsg').textContent = '';
  
  // Validate SVG and show detailed status
  const svgValidation = await validateProjectSVG(project);
  
  let validationDetails = '';
  if (svgValidation.valid) {
    validationDetails = '<span class="status-badge status-success">✓ All SVG files valid</span>';
    
    // Show validation details for all files if available
    if (svgValidation.all_files) {
      const fileCount = Object.keys(svgValidation.all_files).length;
      validationDetails += ` <small>(${fileCount} files checked)</small>`;
    }
  } else {
    validationDetails = '<span class="status-badge status-warning">⚠ SVG validation issues</span>';
    
    // Show specific error details
    if (svgValidation.errors && svgValidation.errors.length > 0) {
      const errorSummary = svgValidation.errors.slice(0, 2).join('; ');
      validationDetails += `<br><small style="color: #ff6b6b;">${errorSummary}</small>`;
    }
    
    // Show auto-fix status if issues were found
    validationDetails += '<br><small>🔧 Auto-fix attempted during generation</small>';
  }
  
  document.getElementById('links').innerHTML = 
    `<div style="margin-bottom: 15px;">
      <p><a href="/files/projects/${project}/" target="_blank" class="btn">📂 Project Files</a> 
         <a href="/files/projects/${project}/${project}.svg" target="_blank" class="btn btn-primary">📄 SVG Package</a></p>
      <div style="padding: 10px; background: var(--bg-secondary); border-radius: 6px;">
        ${validationDetails}
      </div>
    </div>`;
  if (data.urls && data.urls.video) {
    const videoElement = document.getElementById('vid');
    const fallbackLink = document.getElementById('vid-fallback');
    
    // Set video source and fallback download link
    videoElement.src = data.urls.video;
    fallbackLink.href = data.urls.video;
    fallbackLink.textContent = 'Download video file';
    
    // Add error handling for video loading
    videoElement.onerror = function(e) {
      console.error('Video loading error:', e);
      console.log('Video source:', videoElement.src);
    };
    
    videoElement.onloadstart = function() {
      console.log('Video loading started:', data.urls.video);
    };
    
    videoElement.oncanplay = function() {
      console.log('Video can start playing');
    };
    
    // Force reload of video element
    videoElement.load();
  }
  if (data.urls && data.urls.thumb) {
    document.getElementById('thumb').src = data.urls.thumb;
  }
  document.getElementById('preview').style.display = '';
  await loadProjects();
}

async function validateProjectSVG(projectName) {
  try {
    const res = await fetch(`/api/validate_svg?project=${encodeURIComponent(projectName)}`);
    return await res.json();
  } catch (e) {
    console.error('SVG validation failed:', e);
    return { valid: false, errors: ['Validation request failed'] };
  }
}

async function showVersionHistory(projectName) {
  try {
    const res = await fetch(`/api/project_history?project=${encodeURIComponent(projectName)}`);
    const history = await res.json();
    
    if (history.versions && history.versions.length > 0) {
      let historyHtml = `<div class="version-history">
        <h3>📜 Version History for ${projectName}</h3>`;
      
      history.versions.forEach((version, index) => {
        const isLatest = index === 0;
        const statusBadge = version.valid ? 
          '<span class="status-badge status-success">✓ Valid</span>' : 
          '<span class="status-badge status-warning">⚠ Issues</span>';
        
        historyHtml += `<div class="version-item">
          <div>
            <strong>Version ${version.version}</strong> ${isLatest ? '<em>(Latest)</em>' : ''}<br>
            <small>${new Date(version.created_at).toLocaleString()}</small>
            ${statusBadge}
          </div>
          <div>
            <a href="/files/projects/${projectName}/versions/${version.filename}" target="_blank" class="btn btn-primary">📄 View</a>
            ${!isLatest ? `<button onclick="restoreVersion('${projectName}', ${version.version})" class="btn">🔄 Restore</button>` : ''}
          </div>
        </div>`;
      });
      
      historyHtml += '</div>';
      
      // Show in modal or dedicated section
      document.getElementById('versionContent').innerHTML = historyHtml;
      document.getElementById('versionModal').style.display = 'block';
    } else {
      alert('No version history found for this project.');
    }
  } catch (e) {
    console.error('Failed to load version history:', e);
}

async function publishWP() {
  const project = document.getElementById('project').value.trim();
  if (!project) { alert('Podaj nazwę projektu'); return; }
  const wp_url = document.getElementById('wp_url').value.trim();
  const wp_user = document.getElementById('wp_user').value.trim();
  const wp_pass = document.getElementById('wp_pass').value.trim();
  const payload = { project };
  if (wp_url && wp_user && wp_pass) {
    payload.base_url = wp_url;
    payload.username = wp_user;
    payload.app_password = wp_pass;
  }
  const res = await fetch('/api/publish_wordpress', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  const data = await res.json();
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  alert('Published: '+(data.link || JSON.stringify(data)));
}

async function fetchNC() {
  const remote = document.getElementById('ncpath').value.trim();
  if (!remote) { alert('Podaj ścieżkę na Nextcloud'); return; }
  const res = await fetch('/api/fetch_nextcloud', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ remote_path: remote })});
  const data = await res.json();
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  alert('Pobrano do: '+data.local_path);
}

async function deleteProject(projectName, event) {
  // Prevent event bubbling to avoid triggering selectProject
  if (event) {
    event.stopPropagation();
  }
  
  const confirmMessage = `⚠️ WARNING: This will permanently delete the project "${projectName}" and ALL its files, including:

• SVG files
• Version history  
• Generated content
• Configuration files

This action CANNOT be undone.

Type the project name to confirm deletion:`;
  
  const userInput = prompt(confirmMessage);
  
  if (userInput !== projectName) {
    if (userInput !== null) {  // User didn't cancel
      alert('Project name does not match. Deletion cancelled.');
    }
    return;
  }
  
  try {
    const response = await fetch('/api/delete_project', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName, confirm: true})
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert('✅ ' + data.message);
      await loadProjects();
    } else {
      alert('❌ Error: ' + data.message);
    }
  } catch (e) {
    alert('❌ Failed to delete project: ' + e.message);
  }
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    logger.info("GET /")
    return render_template_string(INDEX_HTML)

@app.route('/output-index')
def output_index():
    # Serve the output README via Flask if nginx isn't running
    p = OUTPUT_DIR / 'README.md'
    if p.exists():
        logger.info("Serve output README", extra={"path": str(p)})
        return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/markdown; charset=utf-8'}
    return 'No output yet', 404

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

@app.route('/files/<path:filepath>')
def serve_files(filepath):
    """Serve files from output directory with proper MIME types and security."""
    try:
        # Security: prevent directory traversal
        if '..' in filepath or filepath.startswith('/'):
            return 'Access denied', 403
            
        file_path = OUTPUT_DIR / filepath
        
        # Check if file exists and is within output directory
        if not file_path.exists() or not str(file_path.resolve()).startswith(str(OUTPUT_DIR.resolve())):
            return 'File not found', 404
            
        # Set proper MIME type
        mime_type = None
        if filepath.endswith('.mp4'):
            mime_type = 'video/mp4'
        elif filepath.endswith('.mp3'):
            mime_type = 'audio/mpeg'
        elif filepath.endswith('.wav'):
            mime_type = 'audio/wav'
        elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif filepath.endswith('.png'):
            mime_type = 'image/png'
        elif filepath.endswith('.svg'):
            mime_type = 'image/svg+xml'
            
        return send_from_directory(OUTPUT_DIR, filepath, mimetype=mime_type)
    except Exception as e:
        logger.error(f"Error serving file {filepath}: {e}")
        return f"File not found: {filepath}", 404

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        logger.info("POST /api/generate start")
        # Skip dependency verification in FAST_TEST mode to keep tests fast/deterministic
        if os.getenv("YTLITE_FAST_TEST") != "1":
            verify_dependencies()
        # Handle both form data and JSON requests
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            project = data.get('project') if data else None
            markdown = data.get('markdown') if data else None
        else:
            project = request.form.get('project')
            markdown = request.form.get('markdown')
        if not project:
            return jsonify({'message': 'Missing project'}), 400
        project = ''.join(c for c in project if c.isalnum() or c in ('_', '-', '.')).strip()
        if not project:
            return jsonify({'message': 'Invalid project name'}), 400

        # Handle .env upload (optional)
        proj_dir = Path('output/projects')/project
        proj_dir.mkdir(parents=True, exist_ok=True)
        if 'env' in request.files:
            envfile = request.files['env']
            env_path = proj_dir/'.env'
            envfile.save(str(env_path))
            load_dotenv(env_path)
            logger.info("Per-project .env uploaded and loaded", extra={"env": str(env_path)})
        else:
            # Load existing per-project .env if present
            env_path = proj_dir/'.env'
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Per-project .env loaded", extra={"env": str(env_path)})

        # Write markdown to content/episodes
        if markdown and markdown.strip():
            md_path = Path('content/episodes')/f"{project}.md"
            md_path.parent.mkdir(parents=True, exist_ok=True)
            if not markdown.lstrip().startswith('---'):
                # Build frontmatter from selections
                fm = ["---", f"title: {project}", f"date: {datetime.now().date()}"]
                v = request.form.get('voice');    t = request.form.get('template'); th = request.form.get('theme'); fs = request.form.get('font_size'); lg = request.form.get('lang')
                if th: fm.append(f"theme: {th}")
                if t: fm.append(f"template: {t}")
                if fs: fm.append(f"font_size: {fs}")
                if v: fm.append(f"voice: {v}")
                if lg: fm.append(f"lang: {lg}")
                fm.append("---\n")
                markdown = "\n".join(fm) + "\n" + markdown
            md_path.write_text(markdown, encoding='utf-8')
            logger.info("Markdown written", extra={"path": str(md_path)})
        else:
            md_path = Path('content/episodes')/f"{project}.md"
            if not md_path.exists():
                return jsonify({'message': 'No markdown provided and file does not exist'}), 400

        # Generate
        y = YTLite()
        y.generate_video(str(md_path))

        # After generation, create single-file SVG project
        try:
            video_path = proj_dir / "video.mp4"
            audio_path = proj_dir / "audio.mp3"
            thumb_path = proj_dir / "thumbnail.jpg"
            
            # Prepare metadata
            metadata = {
                'title': project,
                'voice': v or 'en-US-AriaNeural',
                'theme': th or 'default',
                'template': t or 'simple',
                'font_size': fs or '32',
                'language': lg or 'en',
                'markdown_content': markdown,
                'generated': datetime.now().isoformat()
            }
            
            # Create SVG project directory if it doesn't exist
            svg_projects_dir = OUTPUT_DIR / 'svg_projects'
            svg_projects_dir.mkdir(parents=True, exist_ok=True)
            
            # Create single-file SVG project
            if video_path.exists():
                svg_file = create_svg_project(
                    project_name=project,
                    video_path=video_path,
                    audio_path=audio_path if audio_path.exists() else None,
                    thumbnail_path=thumb_path if thumb_path.exists() else None,
                    metadata=metadata,
                    output_dir=svg_projects_dir
                )
                logger.info(f"Created SVG project: {svg_file}")
        except Exception as e:
            logger.error(f"Failed to create SVG project: {e}")

        # Build URLs (served via Flask /files)
        urls = {
            'index': f"/files/projects/{project}/index.md",
            'video': f"/files/projects/{project}/video.mp4",
            'audio': f"/files/projects/{project}/audio.mp3",
            'thumb': f"/files/projects/{project}/thumbnail.jpg",
        }
        
        # Add SVG project URL if created
        svg_path = OUTPUT_DIR / 'svg_projects' / f"{project}.svg"
        if svg_path.exists():
            urls['svg'] = f"/files/svg_projects/{project}.svg"
            
        logger.info("POST /api/generate ok", extra={"project": project})
        return jsonify({'project': project, 'urls': urls})
    except Exception as e:
        console.print(f"[red]API generate error: {e}[/]")
        logger.error("POST /api/generate failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/publish_wordpress', methods=['POST'])
def api_publish_wordpress():
    try:
        data = request.get_json(silent=True) or {}
        project = data.get('project')
        status = data.get('status', 'draft')
        if not project:
            return jsonify({'message': 'Missing project'}), 400
        proj_dir = Path('output/projects')/project
        env_path = proj_dir/'.env'
        if env_path.exists():
            load_dotenv(env_path)
        logger.info("POST /api/publish_wordpress", extra={"project": project, "status": status})
        # Allow overriding creds via payload for multi-account publishing
        pub = WordPressPublisher(
            base_url=data.get('base_url'),
            username=data.get('username'),
            app_password=data.get('app_password'),
        )
        result = pub.publish_project(str(proj_dir), publish_status=status)
        if not result:
            logger.error("Publish failed", extra={"project": project})
            return jsonify({'message': 'Publish failed'}), 500
        logger.info("Publish ok", extra={"project": project, "id": result.get('id') if isinstance(result, dict) else None})
        return jsonify(result)
    except Exception as e:
        logger.error("POST /api/publish_wordpress failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/fetch_nextcloud', methods=['POST'])
def api_fetch_nextcloud():
    try:
        data = request.get_json(silent=True) or {}
        remote_path = data.get('remote_path')
        project = data.get('project')
        if not remote_path:
            return jsonify({'message': 'Missing remote_path'}), 400
        # Load per-project env if provided
        if project:
            proj_dir = Path('output/projects')/project
            env_path = proj_dir/'.env'
            if env_path.exists():
                load_dotenv(env_path)
        logger.info("POST /api/fetch_nextcloud", extra={"remote_path": remote_path, "project": project})
        # Download to content/episodes using original filename
        filename = Path(remote_path).name or 'download.md'
        local = Path('content/episodes')/filename
        client = NextcloudClient()
        ok = client.download_file(remote_path, str(local))
        if not ok:
            logger.error("Nextcloud download failed", extra={"remote_path": remote_path})
            return jsonify({'message': 'Download failed'}), 500
        logger.info("Nextcloud download ok", extra={"local": str(local)})
        return jsonify({'local_path': str(local)})
    except Exception as e:
        logger.error("POST /api/fetch_nextcloud failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/progress')
def api_progress():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({}), 400
    prog = load_progress(project, OUTPUT_DIR)
    return jsonify(prog or {})

@app.route('/api/projects')
def api_projects():
    """List all projects including both directory-based and SVG-based projects."""
    items = []
    
    # Directory-based projects (legacy)
    projects_root = OUTPUT_DIR / 'projects'
    if projects_root.exists():
        for p in sorted(projects_root.glob('*/')):
            name = p.name
            svg = next(p.glob('*.svg'), None)
            
            # Check for version history
            versions_dir = p / 'versions'
            version_count = len(list(versions_dir.glob('*.svg'))) if versions_dir.exists() else 0
            
            # Validate current SVG
            svg_valid = False
            if svg:
                try:
                    import subprocess
                    result = subprocess.run(['xmllint', '--noout', str(svg)], capture_output=True)
                    svg_valid = result.returncode == 0
                except:
                    svg_valid = False
            
            items.append({
                'name': name,
                'type': 'directory',
                'svg': svg.name if svg else None,
                'versions': version_count + 1 if svg else 0,
                'svg_valid': svg_valid
            })
    
    # Single-file SVG projects (new approach)
    svg_root = OUTPUT_DIR / 'svg_projects'
    if svg_root.exists():
        svg_root.mkdir(parents=True, exist_ok=True)
        
        for svg_file in sorted(svg_root.glob('*.svg')):
            name = svg_file.stem
            
            # Extract metadata from SVG
            try:
                packager = SVGDataURIPackager()
                metadata = packager.extract_metadata(svg_file)
                
                items.append({
                    'name': name,
                    'type': 'svg',
                    'svg': svg_file.name,
                    'svg_valid': True,  # Assume valid if we can read metadata
                    'metadata': metadata,
                    'title': metadata.get('title', name),
                    'created': metadata.get('created'),
                    'modified': metadata.get('modified')
                })
            except Exception as e:
                logger.error(f"Failed to read SVG project {svg_file}: {e}")
                items.append({
                    'name': name,
                    'type': 'svg',
                    'svg': svg_file.name,
                    'svg_valid': False
                })
    
    return jsonify({'projects': items})

@app.route('/api/svg_metadata')
def api_svg_metadata():
    """Get metadata from SVG project file."""
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({'error': 'Missing project name'}), 400
    
    try:
        svg_projects_dir = OUTPUT_DIR / 'svg_projects'
        svg_file = svg_projects_dir / f"{project}.svg"
        
        if not svg_file.exists():
            return jsonify({'error': 'SVG project not found'}), 404
        
        packager = SVGDataURIPackager()
        metadata = packager.extract_metadata(svg_file)
        
        return jsonify({
            'project': project,
            'metadata': metadata,
            'file_path': str(svg_file)
        })
    except Exception as e:
        logger.error(f"Failed to get SVG metadata for {project}: {e}")
        return jsonify({'error': 'Failed to read SVG metadata'}), 500

@app.route('/api/validate_svg')
def api_validate_svg():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({'valid': False, 'errors': ['Missing project name']}), 400
    
    project_dir = OUTPUT_DIR / 'projects' / project
    svg_file = next(project_dir.glob('*.svg'), None)
    
    if not svg_file:
        return jsonify({'valid': False, 'errors': ['SVG file not found']})
    
    try:
        # Use enhanced validation from svg_validator
        from svg_validator import validate_all_project_svgs
        validation_results = validate_all_project_svgs(project_dir)
        
        # Get main SVG validation result
        main_svg_name = svg_file.name
        if main_svg_name in validation_results:
            is_valid, errors = validation_results[main_svg_name]
            
            return jsonify({
                'valid': is_valid,
                'errors': errors if not is_valid else [],
                'message': 'SVG is valid XML' if is_valid else 'SVG validation failed',
                'all_files': {
                    filename: {'valid': valid, 'errors': errs}
                    for filename, (valid, errs) in validation_results.items()
                }
            })
        else:
            return jsonify({'valid': False, 'errors': ['Could not validate SVG file']})
            
    except Exception as e:
        logger.error(f"SVG validation error: {e}")
        return jsonify({'valid': False, 'errors': [f'Validation error: {str(e)}']})

@app.route('/api/project_history')
def api_project_history():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({'error': 'Missing project name'}), 400
    
    project_dir = OUTPUT_DIR / 'projects' / project
    if not project_dir.exists():
        return jsonify({'error': 'Project not found'}), 404
        
    versions_dir = project_dir / 'versions'
    versions = []
    
    # Add current version
    current_svg = next(project_dir.glob('*.svg'), None)
    if current_svg:
        try:
            import subprocess
            result = subprocess.run(['xmllint', '--noout', str(current_svg)], capture_output=True)
            valid = result.returncode == 0
        except:
            valid = False
            
        versions.append({
            'version': 'current',
            'filename': current_svg.name,
            'created_at': datetime.fromtimestamp(current_svg.stat().st_mtime).isoformat(),
            'valid': valid,
            'is_current': True
        })
    
    # Add historical versions
    if versions_dir.exists():
        for svg_file in sorted(versions_dir.glob('*.svg'), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                import subprocess
                result = subprocess.run(['xmllint', '--noout', str(svg_file)], capture_output=True)
                valid = result.returncode == 0
            except:
                valid = False
                
            # Extract version number from filename
            version_num = svg_file.stem.split('_v')[-1] if '_v' in svg_file.stem else 'unknown'
            
            versions.append({
                'version': version_num,
                'filename': f'versions/{svg_file.name}',
                'created_at': datetime.fromtimestamp(svg_file.stat().st_mtime).isoformat(),
                'valid': valid,
                'is_current': False
            })
    
    return jsonify({'versions': versions})

@app.route('/api/restore_version', methods=['POST'])
def api_restore_version():
    try:
        data = request.get_json()
        project = data.get('project', '').strip()
        version = data.get('version', '').strip()
        
        if not project or not version:
            return jsonify({'message': 'Missing project or version'}), 400
        
        project_dir = OUTPUT_DIR / 'projects' / project
        versions_dir = project_dir / 'versions'
        
        if version == 'current':
            return jsonify({'message': 'Cannot restore current version'}), 400
        
        # Find the version file
        version_file = None
        if versions_dir.exists():
            for svg_file in versions_dir.glob('*.svg'):
                if f'_v{version}' in svg_file.stem:
                    version_file = svg_file
                    break
        
        if not version_file or not version_file.exists():
            return jsonify({'message': 'Version file not found'}), 404
        
        # Backup current version before restoring
        current_svg = next(project_dir.glob('*.svg'), None)
        if current_svg:
            # Create versions directory if it doesn't exist
            versions_dir.mkdir(exist_ok=True)
            
            # Generate new version number
            existing_versions = [f for f in versions_dir.glob('*.svg')]
            next_version = len(existing_versions) + 1
            
            backup_name = f"{current_svg.stem}_v{next_version}.svg"
            backup_path = versions_dir / backup_name
            
            # Copy current to versions
            import shutil
            shutil.copy2(current_svg, backup_path)
        
        # Restore the selected version
        import shutil
        shutil.copy2(version_file, project_dir / f"{project}.svg")
        
        return jsonify({'message': f'Version {version} restored successfully'})
        
    except Exception as e:
        logger.error(f"Failed to restore version: {e}")
        return jsonify({'message': f'Failed to restore version: {str(e)}'}), 500

@app.route('/api/delete_project', methods=['POST'])
def api_delete_project():
    """Delete a project and all its files."""
    try:
        data = request.get_json()
        project = data.get('project', '').strip()
        confirm = data.get('confirm', False)
        
        if not project:
            return jsonify({'message': 'Missing project name'}), 400
        if '..' in project or '/' in project or '\\' in project:
            return jsonify({'message': 'Invalid project path'}), 400
        if not confirm:
            return jsonify({'message': 'Confirmation required'}), 400
        
        project_dir = OUTPUT_DIR / 'projects' / project
        
        if not project_dir.exists():
            return jsonify({'message': 'Project not found'}), 404
        
        # Security check: ensure we're only deleting within projects directory
        if not str(project_dir.resolve()).startswith(str((OUTPUT_DIR / 'projects').resolve())):
            return jsonify({'message': 'Invalid project path'}), 400
        
        # Delete the entire project directory
        import shutil
        shutil.rmtree(project_dir)
        
        logger.info(f"Project deleted: {project}")
        return jsonify({'message': f'Project "{project}" deleted successfully'})
        
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        return jsonify({'message': f'Failed to delete project: {str(e)}'}), 500

@app.route('/api/svg_meta')
def api_svg_meta():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({}), 400
    pdir = OUTPUT_DIR / 'projects' / project
    svg = next(pdir.glob('*.svg'), None)
    if not svg:
        return jsonify({}), 404
    meta = parse_svg_meta(svg)
    return jsonify(meta or {})

@app.route('/api/svg_update', methods=['POST'])
def api_svg_update():
    data = request.get_json(silent=True) or {}
    project = data.get('project', '').strip()
    if not project:
        return jsonify({'message': 'Missing project'}), 400
    pdir = OUTPUT_DIR / 'projects' / project
    svg = next(pdir.glob('*.svg'), None)
    if not svg:
        return jsonify({'message': 'SVG not found'}), 404
    # Update media from current files if requested
    if data.get('refresh_media'):
        update_svg_media(svg, str(pdir / 'video.mp4'), str(pdir / 'audio.mp3'), str(pdir / 'thumbnail.jpg'))
    # Update JSON metadata fields partially if provided
    meta = parse_svg_meta(svg) or {}
    patch = data.get('metadata') or {}
    if patch:
        for k, v in patch.items():
            if k == 'media':
                meta.setdefault('media', {}).update(v or {})
            else:
                meta[k] = v
        # write back by injecting new JSON
        import re, json as _json
        txt = svg.read_text(encoding='utf-8')
        m = re.search(r"<script type=\"application/json\">(.*?)</script>", txt, flags=re.S)
        if not m:
            return jsonify({'message': 'SVG meta block missing'}), 500
        new_json = _json.dumps(meta, ensure_ascii=False).replace('<', '&lt;')
        new_txt = txt[:m.start(1)] + new_json + txt[m.end(1):]
        svg.write_text(new_txt, encoding='utf-8')
    return jsonify({'ok': True, 'svg': svg.name})


if __name__ == '__main__':
    # Optionally verify deps at startup
    try:
        verify_dependencies()
    except SystemExit:
        pass
    app.run(host='0.0.0.0', port=5000, debug=False)
