'use strict';

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
    loadProjects();
  }
}

function selectProject(name) {
  editProject(name);
}

async function loadProjectMetadata(projectName) {
  try {
    const res = await fetch(`/api/svg_meta?project=${projectName}`);
    if (!res.ok) return;

    const meta = await res.json();
    if (!meta) return;

    const metaContainer = document.getElementById(`project-meta-${projectName}`);
    if (metaContainer) {
      const metaInfo = meta.title && meta.title !== projectName ? `<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📝 ${meta.title}</div>` : '';
      const dateInfo = meta.created ? `<div style="font-size: 11px; color: var(--text-muted);">📅 ${new Date(meta.created).toLocaleDateString()}</div>` : '';
      metaContainer.innerHTML = '<span class="status-badge status-success">✓ SVG Project</span>' + metaInfo + dateInfo;
    }

    const statusCell = document.getElementById(`project-status-${projectName}`);
    const dateCell = document.getElementById(`project-date-${projectName}`);
    if (statusCell) statusCell.innerHTML = '✓ SVG Project';
    if (dateCell) dateCell.innerHTML = meta.created ? new Date(meta.created).toLocaleDateString() : 'N/A';
  } catch (e) {
    console.error(`Failed to load metadata for ${projectName}:`, e);
  }
}

async function urlExists(url) {
  try {
    const res = await fetch(url, { method: 'HEAD', cache: 'no-store' });
    return res.ok;
  } catch (e) { return false; }
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
    if (typeof logEvent === 'function') { try { logEvent(`Media preview: no files found for ${projectName}`, 'warn'); } catch (_) {} }
  } else {
    body.innerHTML = blocks.join('') + `
      <div style="margin-top:8px;">
        <button onclick="checkMedia('${projectName}')" class="btn">🔎 Check Media</button>
      </div>`;
    try {
      const v = document.getElementById(`video-${projectName}`);
      if (v) v.addEventListener('play', (ev) => prePlaybackCheck(projectName, v, 'video'));
      const a = document.getElementById(`audio-${projectName}`);
      if (a) a.addEventListener('play', (ev) => prePlaybackCheck(projectName, a, 'audio'));
    } catch (e) { /* ignore */ }
    if (typeof logEvent === 'function') { try { logEvent(`Media preview updated for ${projectName}`, 'info', {count: blocks.length}); } catch (_) {} }
  }
}

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
        if (typeof logEvent === 'function') { try { logEvent(`Pre-playback audio check failed for ${projectName}`, 'warn', a); } catch (_) {} }
        try { mediaEl.pause(); mediaEl.currentTime = 0; } catch (_) {}
      }
    } else {
      const v = data.video || {};
      if (!v.exists || !v.has_audio || v.silent) {
        showMessage('⚠️ Video audio missing or silent. Playback stopped.', 'warning');
        if (typeof logEvent === 'function') { try { logEvent(`Pre-playback video check failed for ${projectName}`, 'warn', v); } catch (_) {} }
        try { mediaEl.pause(); mediaEl.currentTime = 0; } catch (_) {}
      }
    }
  } catch (e) {
    showMessage(`❌ Media check error: ${e.message}`, 'error');
  }
}

async function checkMedia(projectName) {
  if (!projectName) return;
  try {
    const res = await fetch('/api/check_media?project=' + encodeURIComponent(projectName), { cache: 'no-store' });
    const data = await res.json();
    if (!res.ok) {
      showMessage('Media check failed', 'error');
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
