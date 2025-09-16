#!/usr/bin/env python3
"""
JavaScript Logger Module for YTLite Web GUI
"""

def get_logger_js():
    """Return JavaScript code for logging functionality."""
    return """
// --- Lightweight logging panel and optional WS publisher ---
function initLogger() {
  try {
    // Create log panel
    if (!document.getElementById('logPanel')) {
      const panel = document.createElement('div');
      panel.id = 'logPanel';
      panel.innerHTML = `
        <div style="position:fixed; bottom:10px; right:10px; width:300px; height:200px; background:#f8f9fa; border:1px solid #dee2e6; border-radius:4px; z-index:9999; display:none; flex-direction:column;">
          <div style="padding:8px; background:#007bff; color:white; font-weight:bold; cursor:pointer; user-select:none;" onclick="document.getElementById('logPanelBody').style.display = document.getElementById('logPanelBody').style.display === 'none' ? 'block' : 'none';">📋 Logs</div>
          <div id="logPanelBody" style="flex:1; overflow-y:auto; padding:4px; font-size:12px; line-height:1.3;"></div>
        </div>`;
      document.body.appendChild(panel);
    }
    // Auto-show log panel if in development
    const dev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (dev) {
      document.getElementById('logPanel').style.display = 'flex';
    }
  } catch (e) {
    console.error('Logger init failed:', e);
  }
}

function logEvent(message, level = 'info', context = {}) {
  const body = document.getElementById('logPanelBody');
  const ts = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  const color = {'error': '#dc3545', 'warn': '#ffc107', 'warning': '#ffc107', 'info': '#17a2b8', 'success': '#28a745'}[level] || '#666';
  line.innerHTML = `<span style="color:${color}">[${ts}] ${level.toUpperCase()}: ${message}</span>`;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
  
  // Limit to last 50 entries
  while (body.children.length > 50) body.removeChild(body.firstChild);
  
  // Also log to console for debugging
  console.log(`[${level}] ${message}`, context);
  
  // Optional: send to WebSocket if available and ready
  if (window.wsReady && window.ws && typeof context === 'object') {
    try { window.ws.send(JSON.stringify({level, message, context, ts})); } catch (_) {}
  }
}

function tryOpenWs(url, topic) {
  try {
    ws = new WebSocket(url);
    ws.onopen = () => { wsReady = true; logEvent(`WS connected to ${url}`, 'info', {topic}); };
    ws.onerror = (e) => logEvent(`WS error: ${e}`, 'error');
    ws.onclose = () => { wsReady = false; logEvent('WS disconnected', 'warn'); };
  } catch (e) {
    logEvent(`WS connection failed: ${e.message}`, 'error');
  }
}

function loadMqttLib() {
  return new Promise((resolve, reject) => {
    if (window.mqtt) return resolve();
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/mqtt@4.3.7/dist/mqtt.min.js';
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

function tryOpenMqtt(url, topic) {
  try {
    if (!window.mqtt) throw new Error('mqtt lib not loaded');
    mqttClient = window.mqtt.connect(url);
    mqttClient.on('connect', () => {
      logEvent(`MQTT connected to ${url}`, 'info', {topic});
      mqttClient.subscribe(topic);
    });
  } catch (e) {
    logEvent(`MQTT error: ${e.message}`, 'error');
  }
}

window.initLogger = initLogger;
window.logEvent = logEvent;
window.tryOpenWs = tryOpenWs;
window.loadMqttLib = loadMqttLib;
window.tryOpenMqtt = tryOpenMqtt;
"""
