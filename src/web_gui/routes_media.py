#!/usr/bin/env python3
"""
Media-related Flask routes extracted from routes.py to reduce file size and improve modularity.
Contains:
- /files/<path>
- /api/generate_media
- /api/check_media
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

from flask import request, jsonify, send_from_directory

from media_validator import check_audio_silence, check_video_audio_silence
from mqtt_client import publish_mqtt_event

from . import helpers


def _mime_for(path: str) -> str:
    mime_types = {
        '.svg': 'image/svg+xml',
        '.html': 'text/html',
        '.mp4': 'video/mp4',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.txt': 'text/plain',
        '.md': 'text/markdown'
    }
    file_ext = Path(path).suffix.lower()
    content_type = mime_types.get(file_ext, 'application/octet-stream')
    if file_ext == '.svg':
        content_type += '; charset=utf-8'
    return content_type


def register_media_routes(app, output_dir: Path, logger) -> None:
    @app.route('/files/<path:filepath>')
    def serve_files(filepath):
        """Serve files from output directory with proper MIME types and security."""
        try:
            if '..' in filepath or filepath.startswith('/'):
                logger.warning(f"Potential directory traversal attempt: {filepath}")
                return 'Forbidden', 403
            full_path = output_dir / filepath
            if not full_path.exists():
                logger.warning(f"File not found: {filepath}")
                return 'File not found', 404
            if full_path.is_dir():
                logger.warning(f"Requested path is a directory, not a file: {filepath}")
                return 'Not a file', 404
            return send_from_directory(
                str(output_dir),
                filepath,
                mimetype=_mime_for(filepath),
                as_attachment=False
            )
        except Exception as e:
            logger.error(f"Error serving file {filepath}: {e}")
            return 'Server error', 500

    @app.route('/api/generate_media', methods=['POST'])
    def api_generate_media():
        """Generate missing media files (audio, video, thumb) for a project."""
        data = request.get_json()
        project_name = data.get('project') if data else None
        if not project_name:
            return jsonify({'error': 'Missing project name'}), 400
        try:
            success, generated_files, error = helpers.generate_missing_media(project_name, output_dir)
            if success:
                return jsonify({'message': 'Media generated successfully', 'files_generated': generated_files}), 200
            else:
                logger.error(f"Failed to generate media for {project_name}: {error}")
                return jsonify({'error': f'Failed to generate media: {error}'}), 500
        except Exception as e:
            logger.error(f"Error in /api/generate_media for {project_name}: {e}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.route('/api/check_media')
    def api_check_media():
        """Validate project's audio/video before playback and publish MQTT warnings if silent/missing."""
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'error': 'Missing project parameter'}), 400
        try:
            audio_path = output_dir / 'audio' / f"{project}.mp3"
            video_path = output_dir / 'videos' / f"{project}.mp4"
            ares = check_audio_silence(audio_path)
            vres = check_video_audio_silence(video_path)
            try:
                publish_mqtt_event(
                    'preplay_audio_silence' if ares.get('silent') else 'preplay_audio_ok',
                    'error' if ares.get('silent') else 'info',
                    project,
                    {'check': ares},
                    tags=['preplay', 'media']
                )
                publish_mqtt_event(
                    'preplay_video_silence' if (vres.get('silent') or not vres.get('has_audio')) else 'preplay_video_ok',
                    'error' if (vres.get('silent') or not vres.get('has_audio')) else 'info',
                    project,
                    {'check': vres},
                    tags=['preplay', 'media']
                )
            except Exception:
                pass
            ok = bool(ares.get('exists') and not ares.get('silent') and vres.get('exists') and vres.get('has_audio') and not vres.get('silent'))
            return jsonify({'project': project, 'audio': ares, 'video': vres, 'ok': ok}), 200
        except Exception as e:
            logger.error(f"/api/check_media failed for {project}: {e}")
            return jsonify({'error': 'Failed to check media'}), 500
