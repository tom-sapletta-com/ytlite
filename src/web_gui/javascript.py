#!/usr/bin/env python3
"""
JavaScript code for YTLite Web GUI
Refactored into modular components for better maintainability
"""

from .js_logger import get_logger_js
from .js_theme import get_theme_js
from .js_validation import get_validation_js
from .js_projects import get_projects_js
from .js_forms import get_forms_js
from .js_media import get_media_js
from .js_operations import get_operations_js
from .js_actions import get_actions_js

def get_javascript_content():
    """Return the JavaScript content for the web GUI."""
    # First try to load from static files if they exist
    try:
        from pathlib import Path
        base = Path(__file__).resolve().parents[2]  # project root
        parts = []
        modular_order = [
            'globals.js',
            'logger.js',
            'status.js',
            'theme.js',
            'validation.js',
            'form.js',
            'projects-grid.js',
            'projects-table.js',
            'media.js',
            'publish.js',
            'history.js',
            'projects.js',
            'operations.js',
            'actions.js',
            'bootstrap.js',
        ]
        for name in modular_order:
            p = base / 'web_static' / 'static' / 'js' / name
            if p.exists():
                parts.append(p.read_text(encoding='utf-8'))
        if parts:
            return '\n'.join(parts)
        # fallback to older single-file if present
        single = base / 'web_static' / 'static' / 'js' / 'web_gui.js'
        if single.exists():
            return single.read_text(encoding='utf-8')
    except Exception:
        pass
    
    # Fallback to modular Python-generated JavaScript
    return get_modular_javascript()

def get_modular_javascript():
    """Generate JavaScript from modular Python components."""
    components = [
        get_logger_js(),
        get_theme_js(), 
        get_validation_js(),
        get_projects_js(),
        get_forms_js(),
        get_media_js(),
        get_operations_js(),
        get_actions_js()
    ]
    
    # Add main initialization
    init_js = """
'use strict';

// Global variables
let ws = null;
let wsReady = false;
let mqttClient = null;
let mqttTopic = 'ytlite/logs';
let formHandlersAttached = false;

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initLogger();
  loadTheme();
  loadProjects();
});

// Action tracking for analytics
function trackAction(action, context = {}) {
  try {
    fetch('/api/ui_event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, context })
    }).catch(() => {}); // Ignore errors
  } catch (e) {}
}

function _wrapAction(actionName, originalFunc) {
  return function(...args) {
    trackAction(actionName, { args });
    return originalFunc.apply(this, args);
  };
}
"""
    
    return init_js + '\n\n'.join(components)


JAVASCRIPT_CODE = get_javascript_content()
