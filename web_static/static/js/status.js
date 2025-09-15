'use strict';

function showMessage(text, type = 'info') {
  const existingMsg = document.getElementById('statusMessage');
  if (existingMsg) {
    existingMsg.remove();
  }

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
  if (typeof logEvent === 'function') { try { logEvent(text, type); } catch (_) {} }

  setTimeout(() => {
    if (msgDiv.parentNode) {
      msgDiv.remove();
    }
  }, 3000);
}
