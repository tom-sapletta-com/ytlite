'use strict';

// Global state variables
let currentProjectView = 'grid';
let ws = null; // optional raw WebSocket logger
let wsReady = false;
let mqttClient = null; // optional MQTT logger
let mqttReady = false;
let mqttTopic = 'ytlite/logs';
let formHandlersAttached = false;
