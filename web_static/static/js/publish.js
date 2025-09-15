'use strict';

async function publishToYoutube(projectName, event) {
  if (event) event.stopPropagation();
  if (typeof showMessage === 'function') showMessage('📺 Publishing to YouTube...', 'info');
  try {
    const response = await fetch('/api/publish/youtube', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    const data = await response.json();
    if (response.ok) {
      if (typeof showMessage === 'function') showMessage(`✅ Published "${projectName}" to YouTube successfully`, 'success');
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ YouTube publish failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ YouTube publish error: ${e.message}`, 'error');
  }
}

async function publishToWordPress(projectName, event) {
  if (event) event.stopPropagation();
  if (typeof showMessage === 'function') showMessage('📝 Publishing to WordPress...', 'info');
  try {
    const response = await fetch('/api/publish/wordpress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({project: projectName})
    });
    const data = await response.json();
    if (response.ok) {
      if (typeof showMessage === 'function') showMessage(`✅ Published "${projectName}" to WordPress successfully`, 'success');
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ WordPress publish failed: ${data.message || data.error}`, 'error');
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ WordPress publish error: ${e.message}`, 'error');
  }
}
