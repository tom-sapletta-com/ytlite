#!/usr/bin/env python3
"""
JavaScript Actions and Publishing Module for YTLite Web GUI
"""

def get_actions_js():
    """Return JavaScript code for actions and publishing functionality."""
    return """
// Project editing functions
async function editProject(name, evt) {
  if (evt) { evt.preventDefault(); evt.stopPropagation(); }
  
  // Show form immediately with loading state
  showFormForEdit();
  document.getElementById('content').value = 'Loading...';
  
  try {
    // Load project metadata
    const meta = await loadProjectMetadata(name);
    if (!meta) {
      // Fallback: try to load markdown content directly
      const content = await fetchProjectMarkdown(name);
      populateProjectForm(name, { markdown_content: content || '' });
    } else {
      populateProjectForm(name, meta);
    }
    
    logEvent(`Opened project for editing: ${name}`, 'info');
  } catch (error) {
    logEvent(`Failed to load project ${name}: ${error.message}`, 'error');
    showMessage(`❌ Failed to load project: ${error.message}`, 'error');
    document.getElementById('content').value = '';
  }
}

// Publishing functions
async function publishToYoutube(projectName, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  try {
    showMessage(`📺 Publishing "${projectName}" to YouTube...`, 'info');
    const response = await fetch('/api/publish/youtube', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName })
    });
    
    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Published "${projectName}" to YouTube!`, 'success');
      logEvent(`YouTube publish: ${projectName}`, 'success', result);
    } else {
      showMessage(`❌ YouTube publish failed: ${result.error}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ YouTube publish error: ${error.message}`, 'error');
  }
}

async function publishToWordPress(projectName, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  try {
    showMessage(`📝 Publishing "${projectName}" to WordPress...`, 'info');
    const response = await fetch('/api/publish/wordpress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName })
    });
    
    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Published "${projectName}" to WordPress!`, 'success');
      logEvent(`WordPress publish: ${projectName}`, 'success', result);
    } else {
      showMessage(`❌ WordPress publish failed: ${result.error}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ WordPress publish error: ${error.message}`, 'error');
  }
}

// Version history functions
async function showVersionHistory(projectName, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  try {
    const response = await fetch(`/api/version_history?project=${encodeURIComponent(projectName)}`);
    const result = await response.json();
    
    if (response.ok && result.versions) {
      const versionsHtml = result.versions.map(v => 
        `<div class="version-item">
          <strong>${v.file}</strong> - ${v.date}
          <button onclick="restoreVersion('${projectName}', '${v.file}')" class="btn-small">Restore</button>
        </div>`
      ).join('');
      
      showMessage(`📚 Version History for "${projectName}":<br>${versionsHtml}`, 'info');
    } else {
      showMessage(`❌ No version history found for "${projectName}"`, 'warning');
    }
  } catch (error) {
    showMessage(`❌ Version history error: ${error.message}`, 'error');
  }
}

async function restoreVersion(projectName, versionFile) {
  if (!confirm(`Restore "${projectName}" to version "${versionFile}"?`)) {
    return;
  }
  
  try {
    const response = await fetch('/api/restore_version', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName, version: versionFile })
    });
    
    const result = await response.json();
    if (response.ok) {
      showMessage(`✅ Restored "${projectName}" to version "${versionFile}"`, 'success');
      loadProjects();
    } else {
      showMessage(`❌ Restore failed: ${result.message}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ Restore error: ${error.message}`, 'error');
  }
}

// SVG operations
async function openSVGWithAutoplay(svgPath, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  try {
    window.open(`/files/${svgPath}`, '_blank');
    logEvent(`Opened SVG: ${svgPath}`, 'info');
  } catch (error) {
    showMessage(`❌ Failed to open SVG: ${error.message}`, 'error');
  }
}

// Message display function
function showMessage(message, type = 'info') {
  // Remove existing messages
  const existing = document.querySelectorAll('.message-toast');
  existing.forEach(el => el.remove());
  
  // Create new message
  const toast = document.createElement('div');
  toast.className = `message-toast message-${type}`;
  toast.innerHTML = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    z-index: 10000;
    max-width: 400px;
    word-wrap: break-word;
    background: ${type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : type === 'success' ? '#28a745' : '#17a2b8'};
  `;
  
  document.body.appendChild(toast);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (toast.parentNode) {
      toast.remove();
    }
  }, 5000);
  
  // Also log the message
  logEvent(message.replace(/<[^>]*>/g, ''), type);
}

window.editProject = editProject;
window.publishToYoutube = publishToYoutube;
window.publishToWordPress = publishToWordPress;
window.showVersionHistory = showVersionHistory;
window.restoreVersion = restoreVersion;
window.openSVGWithAutoplay = openSVGWithAutoplay;
window.showMessage = showMessage;
"""
