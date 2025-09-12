#!/usr/bin/env python3
"""
HTML Templates for YTLite Web GUI
Extracted from web_gui.py for better modularity
"""

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
    
    .projects-view-toggle {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      align-items: center;
    }
    
    .view-btn {
      padding: 8px 16px;
      border: 1px solid var(--border-color);
      background: var(--bg-secondary);
      color: var(--text-primary);
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
    }
    
    .view-btn.active, .view-btn:hover {
      background: var(--btn-primary);
      color: white;
      border-color: var(--btn-primary);
    }
    
    .projects-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
      gap: 20px; 
      margin-top: 24px; 
    }
    
    .projects-table {
      display: none;
      margin-top: 24px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
    }
    
    .projects-table.active {
      display: block;
    }
    
    .projects-table table {
      width: 100%;
      border-collapse: collapse;
    }
    
    .projects-table th,
    .projects-table td {
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
    }
    
    .projects-table th {
      background: var(--bg-secondary);
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .projects-table tr:hover {
      background: var(--bg-accent);
    }

    .video-preview {
      max-width: 200px;
      max-height: 120px;
      border-radius: 6px;
      margin-top: 8px;
    }

    .svg-viewer {
      width: 100%;
      height: 500px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
    }

    .validation-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
    }

    .validation-valid {
      background: #d4edda;
      color: #155724;
    }

    .validation-invalid {
      background: #f8d7da;
      color: #721c24;
    }

    .validation-warning {
      background: #fff3cd;
      color: #856404;
    }

    .validation-errors {
      background: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 16px;
    }

    .field-error {
      color: #dc3545;
      font-size: 12px;
      margin-top: 4px;
      margin-bottom: 8px;
      display: none;
    }

    .field-error.show {
      display: block;
    }

    .form-field.error input,
    .form-field.error textarea {
      border-color: #dc3545;
      background-color: rgba(220, 53, 69, 0.1);
    }

    .validation-warning {
      background: #fff3cd;
      color: #856404;
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
      text-decoration: none; 
      border-radius: 6px; 
      font-size: 14px; 
      font-weight: 500;
      border: 1px solid var(--border-color);
      background: var(--bg-secondary);
      color: var(--text-primary);
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    
    .btn:hover { 
      background: var(--bg-accent); 
    }
    
    .btn-primary { 
      background: var(--btn-primary); 
      color: white; 
      border-color: var(--btn-primary);
    }
    
    .btn-primary:hover { 
      background: var(--btn-primary-hover); 
      border-color: var(--btn-primary-hover);
    }
    
    .btn-secondary { 
      background: var(--btn-secondary); 
      color: white; 
      border-color: var(--btn-secondary);
    }
    
    .btn-danger { 
      background: var(--btn-danger); 
      color: white; 
      border-color: var(--btn-danger);
    }
    
    .btn-danger:hover { 
      background: #c82333; 
      border-color: #bd2130;
    }
    
    .status-badge {
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .status-success {
      background: #d4edda;
      color: #155724;
    }
    
    .status-warning {
      background: #fff3cd;
      color: #856404;
    }
    
    .status-error {
      background: #f8d7da;
      color: #721c24;
    }
    
    .loading { opacity: 0.7; }
    
    #createForm { display: none; }
    #editForm { display: none; }
    
    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 24px;
      justify-content: flex-end;
    }
    
    @media (max-width: 768px) {
      body { padding: 12px; }
      .header { flex-direction: column; gap: 16px; text-align: center; }
      .row { flex-direction: column; }
      .projects-grid { grid-template-columns: 1fr; }
      .project-actions { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎬 YTLite</h1>
    <button class="theme-toggle" onclick="toggleTheme()">
      <span id="theme-icon">🌙</span>
      <span id="theme-text">Dark Mode</span>
    </button>
  </div>

  <div class="box">
    <h2>📝 Create New Project</h2>
    <button onclick="showCreateForm()" class="btn btn-primary">+ New Project</button>
    
    <div id="createForm">
      <div id="validationErrors" class="validation-errors" style="display: none;"></div>
      
      <label for="project">Project Name:</label>
      <input type="text" id="project" name="project" placeholder="my-awesome-project" onblur="validateField('project')">
      <div id="project-error" class="field-error"></div>
      
      <label for="content">Content (Markdown):</label>
      <textarea id="content" name="content" placeholder="title: My Title
date: 2025-01-15
theme: wetware
tags: ['example', 'demo']

# My Title

This is my content with **markdown** support.

- Point 1
- Point 2

## Features
- Markdown formatting
- YAML frontmatter
- Multiple themes" onblur="validateField('content')"></textarea>
      <div id="content-error" class="field-error"></div>
      
      <div class="row">
        <div class="col">
          <label for="theme">Theme:</label>
          <select id="theme" name="theme">
            <option value="default">Default</option>
            <option value="dark">Dark</option>
            <option value="blue">Blue</option>
            <option value="green">Green</option>
          </select>
        </div>
        <div class="col">
          <label for="template">Template:</label>
          <select id="template" name="template">
            <option value="simple">Simple</option>
            <option value="modern">Modern</option>
            <option value="minimal">Minimal</option>
            <option value="corporate">Corporate</option>
          </select>
        </div>
      </div>
      
      <div class="row">
        <div class="col">
          <label for="voice">Voice:</label>
          <select id="voice" name="voice">
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (UK)</option>
            <option value="es-ES">Spanish</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
            <option value="it-IT">Italian</option>
            <option value="pl-PL">Polish</option>
          </select>
        </div>
        <div class="col">
          <label for="font_size">Font Size:</label>
          <select id="font_size" name="font_size">
            <option value="small">Small</option>
            <option value="medium" selected>Medium</option>
            <option value="large">Large</option>
            <option value="xl">Extra Large</option>
          </select>
        </div>
      </div>
      
      <div class="form-actions">
        <button onclick="hideCreateForm()" class="btn">Cancel</button>
        <button onclick="generateProject()" class="btn btn-primary">🚀 Generate Project</button>
      </div>
    </div>
  </div>

  <div class="box">
    <h2>📂 Projects</h2>
    <div class="projects-view-toggle">
      <span>View:</span>
      <button class="view-btn active" onclick="switchProjectView('grid')" id="grid-btn">📱 Grid</button>
      <button class="view-btn" onclick="switchProjectView('table')" id="table-btn">📋 Table</button>
    </div>
    <div id="projectsContainer">Loading projects...</div>
    <div id="projectsTable" class="projects-table">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="projectsTableBody">
        </tbody>
      </table>
    </div>
  </div>

  <div id="editForm" class="box">
    <h2>✏️ Edit Project</h2>
    <div id="editValidationErrors" class="validation-errors" style="display: none;"></div>
    
    <label for="editProject">Project Name:</label>
    <input type="text" id="editProject" name="editProject" readonly>
    
    <label for="editContent">Content (Markdown):</label>
    <textarea id="editContent" name="editContent" onblur="validateEditField('editContent')"></textarea>
    <div id="editContent-error" class="field-error"></div>
    
    <div class="row">
      <div class="col">
        <label for="editTheme">Theme:</label>
        <select id="editTheme" name="editTheme">
          <option value="default">Default</option>
          <option value="dark">Dark</option>
          <option value="blue">Blue</option>
          <option value="green">Green</option>
        </select>
      </div>
      <div class="col">
        <label for="editTemplate">Template:</label>
        <select id="editTemplate" name="editTemplate">
          <option value="simple">Simple</option>
          <option value="modern">Modern</option>
          <option value="minimal">Minimal</option>
          <option value="corporate">Corporate</option>
        </select>
      </div>
    </div>
    
    <div class="row">
      <div class="col">
        <label for="editVoice">Voice:</label>
        <select id="editVoice" name="editVoice">
          <option value="en-US">English (US)</option>
          <option value="en-GB">English (UK)</option>
          <option value="es-ES">Spanish</option>
          <option value="fr-FR">French</option>
          <option value="de-DE">German</option>
          <option value="it-IT">Italian</option>
          <option value="pl-PL">Polish</option>
        </select>
      </div>
      <div class="col">
        <label for="editFontSize">Font Size:</label>
        <select id="editFontSize" name="editFontSize">
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
          <option value="xl">Extra Large</option>
        </select>
      </div>
    </div>
    
    <div class="form-actions">
      <button onclick="hideEditForm()" class="btn">Cancel</button>
      <button onclick="updateProject()" class="btn btn-primary">💾 Update Project</button>
    </div>
  </div>

  <script src="/static/js/web_gui.js"></script>
</body>
</html>
"""
