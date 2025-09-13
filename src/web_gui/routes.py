#!/usr/bin/env python3
"""
Flask Routes for YTLite Web GUI
Extracted from web_gui.py for better modularity
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logging_setup import get_logger

# Import helpers directly to avoid import issues
import sys
import os
# Add the web_gui directory to path if needed
web_gui_dir = os.path.dirname(__file__)
if web_gui_dir not in sys.path:
    sys.path.insert(0, web_gui_dir)

import helpers

logger = get_logger("web_gui.routes")

# Injection points for tests (monkeypatching)
# Tests expect to be able to monkeypatch these symbols on this module
WordPressPublisher = None  # monkeypatch can set to a fake publisher class
NextcloudClient = None     # monkeypatch can set to a fake nextcloud client class

def setup_routes(app: Flask, base_dir: Path, output_dir: Path):
    """Setup all Flask routes for the web GUI."""
    
    @app.route('/')
    def index():
        logger.info("GET /")
        from .templates import INDEX_HTML
        return render_template_string(INDEX_HTML)

    # Register static/config routes
    try:
        from .routes_static import register_static_routes as _register_static_routes
        _register_static_routes(app, output_dir, logger)
    except Exception as _reg_err:
        logger.warning(f"Failed to register static routes: {_reg_err}")

    # Register media-related routes (files serving, media generation/check)
    try:
        from .routes_media import register_media_routes as _register_media_routes
        _register_media_routes(app, output_dir, logger)
    except Exception as _reg_err:
        logger.warning(f"Failed to register media routes: {_reg_err}")

    # Register project list/metadata routes
    try:
        from .routes_projects import register_project_routes as _register_project_routes
        _register_project_routes(app, output_dir, logger)
    except Exception as _reg_err:
        logger.warning(f"Failed to register project routes: {_reg_err}")

    @app.route('/api/generate', methods=['POST'])
    def api_generate():
        """Generate a new project or update existing one."""
        try:
            logger.info("POST /api/generate start")
            data = request.form.to_dict()
            logger.debug(f"Request form data: {data}")
            project = data.get('project', '').strip()
            force_regenerate = data.get('force_regenerate', 'false').lower() == 'true'
            if not project:
                logger.error("Missing project name in request")
                return jsonify({'message': 'Missing project name'}), 400

            # Get per-project env file if uploaded
            env_file = request.files.get('env')
            if env_file and env_file.filename:
                env_path = output_dir / 'projects' / project / '.env'
                env_path.parent.mkdir(parents=True, exist_ok=True)
                env_file.save(str(env_path))
                logger.info(f"Saved per-project .env to {env_path}")

            # Load per-project .env if it exists
            proj_env = output_dir / 'projects' / project / '.env'
            if proj_env.exists():
                load_dotenv(str(proj_env))
                logger.info(f"Loaded per-project .env from {proj_env}")

            # Prepare metadata for SVG project creation
            metadata = {
                'project': project,
                'markdown_content': data.get('markdown', ''),
                'voice': data.get('voice', 'en-US-AriaNeural'),
                'theme': data.get('theme', 'default'),
                'template': data.get('template', 'simple'),
                'font_size': data.get('font_size', 'medium'),
                'language': data.get('lang', 'en'),
                'created': datetime.now().isoformat()
            }

            # Create SVG project using new architecture
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            svg_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                logger.info(f"Starting SVG project creation for {project}")
                logger.debug(f"Metadata: {metadata}")
                
                # Determine if it's a create or update operation based on whether the project dir exists
                project_dir = output_dir / 'projects' / project
                is_update = project_dir.exists()

                # Create/update SVG project
                svg_path = helpers.create_svg_project(
                    project_name=project,
                    content=data.get('markdown', ''),
                    metadata=data,
                    output_path=svg_file,
                    force_regenerate=force_regenerate
                )
                
                if svg_path:
                    logger.info(f"✅ SVG project creation successful for {project}")
                    
                    # Post-generation validation
                    validation_status = {'valid': False, 'message': 'Validation failed'}
                    try:
                        from svg_packager import parse_svg_meta
                        svg_meta = parse_svg_meta(svg_file)
                        if svg_meta:
                            validation_status['valid'] = True
                            validation_status['message'] = 'SVG is well-formed.'
                            
                            # Check for embedded media
                            svg_content = svg_file.read_text(encoding='utf-8')
                            has_audio = 'data:audio' in svg_content
                            if has_audio:
                                validation_status['message'] += ' Contains embedded audio.'
                            else:
                                validation_status['message'] += ' No embedded audio found.'
                        else:
                            validation_status['message'] = 'SVG appears to be corrupt or empty.'
                    except Exception as val_err:
                        logger.error(f"Validation error for {project}: {val_err}")
                        validation_status['message'] = f"Validation failed: {val_err}"

                    return jsonify({
                        'message': f'Project "{project}" generated successfully.',
                        'project': project,
                        'svg_file': f"svg_projects/{project}.svg",
                        'type': 'svg',
                        'validation': validation_status
                    })
                else:
                    logger.error(f"❌ SVG project creation failed for {project} - create_svg_project returned False")
                    return jsonify({'message': 'Failed to generate project'}), 500
                    
            except Exception as svg_error:
                logger.error(f"❌ SVG project creation error for {project}: {str(svg_error)}")
                logger.debug(f"   Full error details: {svg_error}", exc_info=True)
                return jsonify({'message': f'SVG generation error: {str(svg_error)}'}), 500

        except Exception as e:
            logger.error("POST /api/generate failed", extra={"error": str(e)})
            logger.debug(f"Full error details: {e}", exc_info=True)
            return jsonify({'message': str(e)}), 500

    @app.route('/api/publish_wordpress', methods=['POST'])
    def api_publish_wordpress():
        """Legacy WordPress publishing endpoint."""
        try:
            data = request.get_json(silent=True) or {}
            project = data.get('project', '').strip()
            if not project:
                return jsonify({'message': 'Missing project name'}), 400

            proj_dir = output_dir / 'projects' / project
            if not proj_dir.exists():
                return jsonify({'message': f'Project "{project}" not found'}), 404

            # Load per-project env if provided
            if project:
                proj_env = output_dir / 'projects' / project / '.env'
                if proj_env.exists():
                    load_dotenv(str(proj_env))

            # Prefer monkeypatched publisher if provided
            publisher_cls = WordPressPublisher
            if publisher_cls is None:
                try:
                    from wordpress_publisher import WordPressPublisher as _WPP
                    publisher_cls = _WPP
                except Exception as _imp_err:
                    logger.error(f"Failed to import WordPressPublisher: {_imp_err}")
                    return jsonify({'message': 'Publish failed'}), 500

            pub = publisher_cls()
            result = pub.publish_project(str(proj_dir), publish_status=data.get('status', 'draft'))
            if not result:
                logger.error("Publish failed", extra={"project": project})
                return jsonify({'message': 'Publish failed'}), 500
            logger.info("Publish ok", extra={"project": project, "id": result.get('id') if isinstance(result, dict) else None})
            return jsonify(result)
        except Exception as e:
            logger.error("POST /api/publish_wordpress failed", extra={"error": str(e)})
            return jsonify({'message': str(e)}), 500

    @app.route('/api/publish/youtube', methods=['POST'])
    def api_publish_youtube():
        """Publish project to YouTube."""
        try:
            data = request.get_json()
            project = data.get('project', '').strip()
            
            if not project:
                return jsonify({'error': 'Missing project name'}), 400
            
            # Check if project exists
            project_dir = output_dir / 'projects' / project
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            
            if not project_dir.exists() and not svg_file.exists():
                return jsonify({'error': 'Project not found'}), 404
            
            # For now, return a placeholder response
            # In a real implementation, this would integrate with YouTube API
            return jsonify({
                'message': f'YouTube publishing for "{project}" would be initiated here',
                'status': 'placeholder',
                'project': project
            })
            
        except Exception as e:
            logger.error(f"Failed to publish to YouTube: {e}")
            return jsonify({'error': 'Failed to publish to YouTube'}), 500

    @app.route('/api/publish/wordpress', methods=['POST'])
    def api_publish_wordpress_new():
        """Publish project to WordPress (new endpoint)."""
        try:
            data = request.get_json()
            project = data.get('project', '').strip()
            
            if not project:
                return jsonify({'error': 'Missing project name'}), 400
            
            # Check if project exists
            project_dir = output_dir / 'projects' / project
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            
            if not project_dir.exists() and not svg_file.exists():
                return jsonify({'error': 'Project not found'}), 404
            
            # Try to use existing WordPress publisher
            try:
                # Prefer monkeypatched publisher if provided
                publisher_cls = WordPressPublisher
                if publisher_cls is None:
                    from wordpress_publisher import WordPressPublisher as _WPP
                    publisher_cls = _WPP
                publisher = publisher_cls()
                result = publisher.publish_project(project)
                return jsonify({
                    'message': f'Published "{project}" to WordPress successfully',
                    'status': 'success',
                    'project': project,
                    'details': result
                })
            except ImportError:
                # Fallback if WordPress publisher not available
                return jsonify({
                    'message': f'WordPress publishing for "{project}" would be initiated here',
                    'status': 'placeholder',
                    'project': project
                })
            
        except Exception as e:
            logger.error(f"Failed to publish to WordPress: {e}")
            return jsonify({'error': 'Failed to publish to WordPress'}), 500

    @app.route('/api/fetch_nextcloud', methods=['POST'])
    def api_fetch_nextcloud():
        """Fetch content from Nextcloud."""
        try:
            data = request.get_json(silent=True) or {}
            remote_path = data.get('remote_path')
            project = data.get('project')
            if not remote_path:
                return jsonify({'message': 'Missing remote_path'}), 400
            # Load per-project env if provided
            if project:
                proj_env = output_dir / 'projects' / project / '.env'
                if proj_env.exists():
                    load_dotenv(str(proj_env))
            # Prefer monkeypatched Nextcloud client if provided
            client_cls = NextcloudClient
            if client_cls is None:
                from storage_nextcloud import NextcloudClient as _NC
                client_cls = _NC
            client = client_cls()
            local_path = client.fetch_file(remote_path)
            if not local_path:
                return jsonify({'message': 'Failed to fetch file'}), 500
            return jsonify({'message': f'File fetched to {local_path}', 'local_path': local_path})
        except Exception as e:
            logger.error("POST /api/fetch_nextcloud failed", extra={"error": str(e)})
            return jsonify({'message': str(e)}), 500

    @app.route('/api/progress')
    def api_progress():
        """Get progress for a project."""
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'message': 'Missing project parameter'}), 400
        from progress import load_progress
        prog = load_progress(project, output_dir)
        return jsonify(prog or {})


    return app
