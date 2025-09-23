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
    const res = await fetch(`/api/svg_metadata?project=${projectName}`);
    if (!res.ok) return;

    const data = await res.json();
    const meta = data.metadata || {};
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
      blocks.push(`
        <div class="media-item">
          <h4>🎬 ${it.label}</h4>
          <video id="video-${projectName}" class="thumb" controls>
            <source src="${it.url}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
          <div id="video-debug-${projectName}" style="font-size: 12px; color: #666; margin-top: 5px;"></div>
          <button onclick="testVideoPlayback('${projectName}', '${it.url}')" class="btn btn-sm btn-secondary" style="margin-top: 5px;">Test Playback</button>
        </div>
      `);
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

function testVideoPlayback(projectName, videoUrl) {
  const debugEl = document.getElementById(`video-debug-${projectName}`);
  if (!debugEl) return;
  
  debugEl.innerHTML = 'Testing video playback...';
  
  // Create a new video element for testing
  const testVideo = document.createElement('video');
  testVideo.controls = true;
  testVideo.style.width = '100%';
  
  // Set up event listeners to track what's happening
  testVideo.addEventListener('error', (e) => {
    let message = 'Video error: ';
    switch(testVideo.error.code) {
      case MediaError.MEDIA_ERR_ABORTED:
        message += 'Playback was aborted';
        break;
      case MediaError.MEDIA_ERR_NETWORK:
        message += 'A network error occurred';
        break;
      case MediaError.MEDIA_ERR_DECODE:
        message += 'The video could not be decoded';
        break;
      case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
        message += 'The video format is not supported';
        break;
      default:
        message += 'Unknown error occurred';
    }
    debugEl.innerHTML += `<div style="color:red">❌ ${message}</div>`;
    debugEl.innerHTML += `<div>Error details: ${JSON.stringify(testVideo.error, null, 2)}</div>`;
  });
  
  testVideo.addEventListener('loadedmetadata', () => {
    debugEl.innerHTML += `<div>✅ Video metadata loaded (${testVideo.videoWidth}x${testVideo.videoHeight}, ${testVideo.duration.toFixed(1)}s)</div>`;
    testVideo.play().catch(e => {
      debugEl.innerHTML += `<div style="color:orange">⚠️ Autoplay prevented: ${e.message}</div>`;
      debugEl.innerHTML += '<div>Click the play button above to start playback</div>';
    });
  });
  
  testVideo.addEventListener('playing', () => {
    debugEl.innerHTML += '<div style="color:green">▶️ Video is playing!</div>';
  });
  
  // Replace the debug content with the test video
  debugEl.innerHTML = '';
  debugEl.appendChild(testVideo);
  
  // Set the video source
  testVideo.src = videoUrl;
  
  // Add a button to close the test
  const closeBtn = document.createElement('button');
  closeBtn.className = 'btn btn-sm btn-secondary';
  closeBtn.style.marginTop = '10px';
  closeBtn.textContent = 'Close Test';
  closeBtn.onclick = () => {
    debugEl.innerHTML = 'Test completed. <a href="#" onclick="event.preventDefault(); testVideoPlayback(\'' + projectName + '\', \'' + videoUrl + '\')">Test again</a>';
    testVideo.pause();
    testVideo.src = '';
  };
  debugEl.appendChild(closeBtn);
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
