'use strict';

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
      if (typeof showMessage === 'function') showMessage('Failed to load version history', 'error');
    }
  } catch (e) {
    console.error('Failed to load version history:', e);
    if (typeof showMessage === 'function') showMessage('Failed to load version history', 'error');
  }
}

async function restoreVersion(projectName, versionFile) {
  try {
    const response = await fetch('/api/restore_version', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ project: projectName, version_file: versionFile })
    });
    const data = await response.json();
    if (response.ok) {
      if (typeof showMessage === 'function') showMessage(`✅ Restored version for "${projectName}"`, 'success');
      const modal = document.getElementById('versionModal');
      if (modal) modal.style.display = 'none';
      if (typeof loadProjects === 'function') await loadProjects();
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ Restore failed: ${data.message}`, 'error');
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Restore error: ${e.message}`, 'error');
  }
}
