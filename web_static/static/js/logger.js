'use strict';

function loadMqttLib() {
  return new Promise((resolve, reject) => {
    if (window.mqtt) return resolve();
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/mqtt/dist/mqtt.min.js';
    s.onload = () => resolve();
    s.onerror = () => reject(new Error('Failed to load mqtt.js'));
    document.head.appendChild(s);
  });
}

function tryOpenMqtt(url, topic) {
  try {
    if (!window.mqtt) throw new Error('mqtt lib not loaded');
    mqttClient = window.mqtt.connect(url);
    mqttClient.on('connect', () => { mqttReady = true; logEvent(`MQTT connected to ${url}`, 'info', {topic}); });
    mqttClient.on('error', () => { mqttReady = false; logEvent('MQTT error (non-fatal)', 'warn'); });
    mqttClient.on('close', () => { mqttReady = false; logEvent('MQTT closed', 'warn'); });
  } catch (e) {
    logEvent('MQTT init failed', 'warn');
  }
}

function tryOpenWs(url, topic) {
  try {
    ws = new WebSocket(url);
    ws.onopen = () => { wsReady = true; logEvent(`WS connected to ${url}`, 'info', {topic}); };
    ws.onerror = () => { logEvent('WS error (non-fatal, proceeding without WS)', 'warn'); };
    ws.onclose = () => { wsReady = false; logEvent('WS closed', 'warn'); };
  } catch (e) {
    logEvent('WS init failed', 'warn');
  }
}

function initLogger() {
  try {
    if (!document.getElementById('logPanel')) {
      const panel = document.createElement('div');
      panel.id = 'logPanel';
      panel.style.cssText = `
        position: fixed; bottom: 10px; left: 10px; z-index: 999;
        width: 420px; max-height: 180px; overflow:auto; font-size: 12px;
        background: rgba(0,0,0,0.6); color: #fff; padding: 8px 10px; border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      `;
      panel.innerHTML = '<div style="font-weight:600; margin-bottom:4px;">Logs</div><div id="logPanelBody"></div>';
      document.body.appendChild(panel);
    }

    fetch('/api/config').then(r => r.json()).then(cfg => {
      if (cfg && cfg.mqtt_ws_url) {
        mqttTopic = cfg.mqtt_ws_topic || 'ytlite/logs';
        loadMqttLib().then(() => {
          tryOpenMqtt(cfg.mqtt_ws_url, mqttTopic);
        }).catch(() => {
          tryOpenWs(cfg.mqtt_ws_url, mqttTopic);
        });
      }
    }).catch(() => {/* ignore */});
  } catch (e) {
    console.warn('Logger init failed', e);
  }
}

function logEvent(message, level = 'info', context = {}) {
  const body = document.getElementById('logPanelBody');
  const ts = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  line.textContent = `[${ts}] ${level.toUpperCase()}: ${message}`;
  body && body.appendChild(line);
  if (body) body.scrollTop = body.scrollHeight;
  if (mqttReady && mqttClient) {
    try {
      const payload = JSON.stringify({t: Date.now(), level, message, context});
      mqttClient.publish(mqttTopic, payload);
    } catch (e) { /* ignore */ }
  }
  if (wsReady && ws) {
    try {
      const payload = JSON.stringify({t: Date.now(), level, message, context});
      ws.send(payload);
    } catch (e) { /* ignore */ }
  }
}
