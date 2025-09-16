#!/usr/bin/env python3
"""
JavaScript Media Module for YTLite Web GUI
"""

def get_media_js():
    """Return JavaScript code for media functionality."""
    return """
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
      blocks.push(`<div class="media-item"><h4>🎬 ${it.label}</h4><video id="video-${projectName}" class="thumb" src="${it.url}" controls></video></div>`);
    } else if (it.key === 'audio') {
      blocks.push(`<div class="media-item"><h4>🔊 ${it.label}</h4><audio id="audio-${projectName}" src="${it.url}" controls></audio></div>`);
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
      <button onclick="checkMedia('${projectName}')" class="btn" style="margin-top:10px; margin-left:8px;">
        🔎 Check Media
      </button>
    `;
    logEvent(`Media preview: no files found for ${projectName}`, 'warn');
  } else {
    body.innerHTML = blocks.join('') + `
      <div style="margin-top:8px;">
        <button onclick="checkMedia('${projectName}')" class="btn">🔎 Check Media</button>
      </div>`;
    // Attach pre-playback validation listeners
    try {
      const v = document.getElementById(`video-${projectName}`);
      if (v) v.addEventListener('play', (ev) => prePlaybackCheck(projectName, v, 'video'));
      const a = document.getElementById(`audio-${projectName}`);
      if (a) a.addEventListener('play', (ev) => prePlaybackCheck(projectName, a, 'audio'));
    } catch (e) { /* ignore */ }
    logEvent(`Media preview updated for ${projectName}`, 'info', {count: blocks.length});
  }
}

// Manual media check via button
async function checkMedia(projectName) {
  if (!projectName) return;
  try {
    const res = await fetch('/api/check_media?project=' + encodeURIComponent(projectName), { cache: 'no-store' });
    const data = await res.json();
    if (!res.ok) {
      showMessage(`Media check failed: ${data.error || data.message || res.status}`, 'error');
      return;
    }
    const status = (data && data.ok) ? 'OK' : 'Issues detected';
    const type = (data && data.ok) ? 'success' : 'warning';
    const msg = 'Media check for ' + projectName + ': ' + status;
    if (typeof logEvent === 'function') { try { logEvent('Media check', type, data); } catch (_) {} }
    showMessage(msg, type);
  } catch (e) {
    showMessage('Media check error: ' + e.message, 'error');
  }
}

// Pre-playback media validator: stops playback if silence/missing audio is detected
async function prePlaybackCheck(projectName, mediaEl, kind) {
  try {
    const res = await fetch(`/api/check_media?project=${encodeURIComponent(projectName)}`, { cache: 'no-store' });
    const data = await res.json();
    if (!res.ok) {
      showMessage(`❌ Media check failed: ${data.error || data.message || res.status}`, 'error');
      return;
    }
    if (kind === 'audio') {
      const a = data.audio || {};
      if (!a.exists || a.silent) {
        showMessage('⚠️ Audio appears silent or missing. Playback stopped.', 'warning');
        logEvent(`Pre-playback audio check failed for ${projectName}`, 'warn', a);
        try { mediaEl.pause(); mediaEl.currentTime = 0; } catch (_) {}
      }
    } else {
      const v = data.video || {};
      if (!v.exists || !v.has_audio || v.silent) {
        showMessage('⚠️ Video audio missing or silent. Playback stopped.', 'warning');
        logEvent(`Pre-playback video check failed for ${projectName}`, 'warn', v);
        try { mediaEl.pause(); mediaEl.currentTime = 0; } catch (_) {}
      }
    }
  } catch (e) {
    showMessage(`❌ Media check error: ${e.message}`, 'error');
  }
}

async function generateMedia(projectName) {
  if (!projectName) return;
  try {
    showMessage(`🎬 Generating media for ${projectName}...`, 'info');
    const res = await fetch('/api/generate_media', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: projectName })
    });
    const data = await res.json();
    if (res.ok) {
      showMessage(`✅ Media generated for ${projectName}`, 'success');
      updateMediaPreview(projectName);
    } else {
      showMessage(`❌ Failed to generate media: ${data.message}`, 'error');
    }
  } catch (e) {
    showMessage(`❌ Media generation error: ${e.message}`, 'error');
  }
}

window.urlExists = urlExists;
window.updateMediaPreview = updateMediaPreview;
window.checkMedia = checkMedia;
window.prePlaybackCheck = prePlaybackCheck;
window.generateMedia = generateMedia;
"""
