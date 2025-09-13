#!/usr/bin/env python3
"""
Static and config routes extracted from routes.py
- /output-index
- /health
- /api/config
- /favicon.ico
- /static/js/web_gui.js and /main.js
"""
from __future__ import annotations

import os
from pathlib import Path
from flask import jsonify, render_template_string


def register_static_routes(app, output_dir: Path, logger) -> None:
    @app.route('/output-index')
    def output_index():
        p = output_dir / 'README.md'
        if p.exists():
            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/markdown; charset=utf-8'}
        return 'No output yet', 404

    @app.route('/health')
    def health():
        return '', 204

    @app.route('/api/config')
    def api_config():
        try:
            cfg = {
                'mqtt_ws_url': os.environ.get('MQTT_WS_URL') or os.environ.get('MQTT_WS') or '',
                'mqtt_ws_topic': os.environ.get('MQTT_WS_TOPIC', 'ytlite/logs')
            }
            return jsonify(cfg)
        except Exception:
            return jsonify({'mqtt_ws_url': '', 'mqtt_ws_topic': 'ytlite/logs'})

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        try:
            from . import javascript as _js
            try:
                import importlib
                _js = importlib.reload(_js)
            except Exception:
                pass
            return _js.get_javascript_content(), 200, {
                'Content-Type': 'application/javascript',
                'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma': 'no-cache'
            }
        except ImportError:
            logger.error("Failed to import get_javascript_content from web_gui.javascript")
            return "// Error: JavaScript content not available", 200, {'Content-Type': 'application/javascript'}

    @app.route('/main.js')
    def serve_main_js():
        return serve_javascript()
