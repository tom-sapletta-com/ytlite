'use strict';

async function generateMedia(projectName) {
  if (!projectName) return;
  if (typeof showMessage === 'function') showMessage(`🎬 Generating media for ${projectName}...`, 'info');
  if (typeof logEvent === 'function') { try { logEvent(`Media generation start for ${projectName}`, 'info'); } catch (_) {} }
  try {
    const res = await fetch('/api/generate_media', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ project: projectName })
    });
    const data = await res.json();
    if (res.ok) {
      if (typeof showMessage === 'function') showMessage(`✅ Media for "${projectName}" generated successfully.`, 'success');
      if (typeof logEvent === 'function') { try { logEvent(`Media generation done for ${projectName}`, 'success', { files: data.files_generated }); } catch (_) {} }
      if (typeof updateMediaPreview === 'function') updateMediaPreview(projectName);
    } else {
      if (typeof showMessage === 'function') showMessage(`❌ Media generation failed: ${data.message || data.error}`, 'error');
      if (typeof logEvent === 'function') { try { logEvent(`Media generation failed for ${projectName}: ${data.message || data.error}`, 'error'); } catch (_) {} }
    }
  } catch (e) {
    if (typeof showMessage === 'function') showMessage(`❌ Media generation error: ${e.message}`, 'error');
    if (typeof logEvent === 'function') { try { logEvent(`Media generation error for ${projectName}: ${e.message}`, 'error'); } catch (_) {} }
  }
}

function openSVGWithAutoplay(svgPath, event) {
  if (event) event.preventDefault();
  const newWindow = window.open(svgPath, '_blank');
  newWindow.addEventListener('load', function() {
    const script = newWindow.document.createElement('script');
    script.textContent = `
      document.addEventListener('DOMContentLoaded', function() {
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
          video.autoplay = true;
          video.play().catch(e => console.log('Auto-play prevented:', e));
        });
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
