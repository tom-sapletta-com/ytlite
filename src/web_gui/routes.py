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

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from dotenv import load_dotenv

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logging_setup import get_logger
from media_validator import check_audio_silence, check_video_audio_silence
from mqtt_client import publish_mqtt_event

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

    @app.route('/output-index')
    def output_index():
        # Serve the output README via Flask if nginx isn't running
        p = output_dir / 'README.md'
        if p.exists():
            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/markdown; charset=utf-8'}
        return 'No output yet', 404

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return '', 204

    @app.route('/api/config')
    def api_config():
        """Return frontend config such as MQTT WebSocket settings (optional)."""
        try:
            cfg = {
                'mqtt_ws_url': os.environ.get('MQTT_WS_URL') or os.environ.get('MQTT_WS') or '',
                'mqtt_ws_topic': os.environ.get('MQTT_WS_TOPIC', 'ytlite/logs')
            }
            return jsonify(cfg)
        except Exception:
            # Be permissive; return empty config on error
            return jsonify({'mqtt_ws_url': '', 'mqtt_ws_topic': 'ytlite/logs'})

    @app.route('/favicon.ico')
    def favicon():
        """Handle favicon requests"""
        return '', 204

    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        """Serve the JavaScript content."""
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
        """Alternative route for JavaScript content."""
        return serve_javascript()

    @app.route('/files/<path:filepath>')
    def serve_files(filepath):
        """Serve files from output directory with proper MIME types and security."""
        try:
            # Security: prevent directory traversal
            if '..' in filepath or filepath.startswith('/'):
                logger.warning(f"Potential directory traversal attempt: {filepath}")
                return 'Forbidden', 403

            # Check if path exists in output directory
            full_path = output_dir / filepath
            if not full_path.exists():
                logger.warning(f"File not found: {filepath}")
                return 'File not found', 404

            # Determine MIME type based on file extension
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
            
            file_ext = Path(filepath).suffix.lower()
            content_type = mime_types.get(file_ext, 'application/octet-stream')
            
            # For SVG files, add charset
            if file_ext == '.svg':
                content_type += '; charset=utf-8'
            
            return send_from_directory(
                str(output_dir), 
                filepath, 
                mimetype=content_type,
                as_attachment=False
            )
            
        except Exception as e:
            logger.error(f"Error serving file {filepath}: {e}")
            return 'Server error', 500

    @app.route('/api/generate_media', methods=['POST'])
    def api_generate_media():
        """Generate missing media files (audio, video, thumb) for a project."""
        data = request.get_json()
        project_name = data.get('project')

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
            # Publish MQTT events
            try:
                publish_mqtt_event(
                    'preplay_audio_silence' if ares.get('silent') else 'preplay_audio_ok',
                    'error' if ares.get('silent') else 'info',
                    project,
                    {'check': ares}
                )
                publish_mqtt_event(
                    'preplay_video_silence' if (vres.get('silent') or not vres.get('has_audio')) else 'preplay_video_ok',
                    'error' if (vres.get('silent') or not vres.get('has_audio')) else 'info',
                    project,
                    {'check': vres}
                )
            except Exception:
                pass
            ok = bool(ares.get('exists') and not ares.get('silent') and vres.get('exists') and vres.get('has_audio') and not vres.get('silent'))
            return jsonify({'project': project, 'audio': ares, 'video': vres, 'ok': ok}), 200
        except Exception as e:
            logger.error(f"/api/check_media failed for {project}: {e}")
            return jsonify({'error': 'Failed to check media'}), 500

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

    @app.route('/api/projects')
    def api_projects():
        try:
            projects = []
            # List directory-based projects
            projects_dir = output_dir / 'projects'
            projects_dir.mkdir(parents=True, exist_ok=True)
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    svg_file = next(project_dir.glob('*.svg'), None)
                    projects.append({
                        'name': project_dir.name,
                        'svg': svg_file.name if svg_file else None,
                        'type': 'directory'
                    })
            
            # List SVG-based projects
            svg_projects_dir = output_dir / 'svg_projects'
            svg_projects_dir.mkdir(parents=True, exist_ok=True)
            for svg_file in svg_projects_dir.glob('*.svg'):
                projects.append({
                    'name': svg_file.stem,
                    'svg': svg_file.name,
                    'type': 'svg',
                    'metadata': None  # Metadata will be fetched on demand by the client
                })
            
            return jsonify({'projects': projects})
        except Exception as e:
            logger.error(f"Error listing projects: {e}", exc_info=True)
            return jsonify({'message': str(e)}), 500

    @app.route('/api/svg_meta', methods=['GET'])
    def api_svg_meta():
        """Get metadata for a single SVG project (simple validator).
        Returns 400 if project missing, 404 if not found, else metadata JSON.
        """
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'error': 'Missing project parameter'}), 400

        svg_file = output_dir / 'svg_projects' / f"{project}.svg"
        if not svg_file.exists():
            return jsonify({'error': 'Project not found'}), 404

        try:
            from svg_packager import parse_svg_meta
            meta = parse_svg_meta(svg_file)
            return jsonify(meta or {}), 200
        except Exception as e:
            logger.error(f"Failed to read SVG metadata for {project}: {e}")
            return jsonify({'error': 'Failed to read SVG metadata'}), 500

    @app.route('/api/svg_metadata')
    def api_svg_metadata():
        """Get metadata for a project, supporting both SVG and directory types."""
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'error': 'Missing project parameter'}), 400

        try:
            # Check for SVG project first
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            if svg_file.exists():
                from svg_packager import parse_svg_meta
                metadata = parse_svg_meta(svg_file) or {}

                # Try to include original markdown content if it exists
                proj_dir = output_dir / 'projects' / project
                md_primary = proj_dir / f"{project}.md"
                desc_fallback = proj_dir / 'description.md'
                try:
                    if md_primary.exists():
                        metadata['markdown_content'] = md_primary.read_text(encoding='utf-8')
                    elif desc_fallback.exists():
                        metadata['markdown_content'] = desc_fallback.read_text(encoding='utf-8')
                except Exception as _e:
                    logger.warning(f"Could not read markdown for {project}: {_e}")
                
                return jsonify({
                    'project': project,
                    'metadata': metadata,
                    'svg_file': f"svg_projects/{project}.svg"
                })

            # Check for directory-based project
            project_dir = output_dir / 'projects' / project
            md_primary = project_dir / f"{project}.md"
            desc_file = project_dir / 'description.md'
            target_md = md_primary if md_primary.exists() else desc_file
            if target_md.exists():
                content = target_md.read_text(encoding='utf-8')
                metadata = {'markdown_content': content}
                # Try to parse frontmatter for theme/template/voice/font_size/lang
                try:
                    import frontmatter
                    fm = frontmatter.loads(content)
                    meta_dict = fm.get('meta') or {}
                    # Direct fields or under 'meta'
                    metadata['theme'] = fm.get('theme') or meta_dict.get('theme')
                    metadata['template'] = fm.get('template') or meta_dict.get('template')
                    metadata['voice'] = fm.get('voice') or meta_dict.get('voice')
                    metadata['font_size'] = fm.get('font_size') or fm.get('fontSize') or meta_dict.get('font_size')
                    metadata['lang'] = fm.get('lang') or fm.get('language') or meta_dict.get('lang')
                except Exception as _e:
                    logger.warning(f"Frontmatter parse failed for {project}: {_e}")

                return jsonify({
                    'project': project,
                    'metadata': metadata
                })

            return jsonify({'error': 'Project not found'}), 404

        except Exception as e:
            logger.error(f"Failed to get metadata for {project}: {e}")
            return jsonify({'error': 'Failed to read project metadata'}), 500

    @app.route('/api/delete_project', methods=['POST'])
    def api_delete_project():
        """Delete a project and all its files."""
        try:
            data = request.get_json()
            project = data.get('project', '').strip()
            
            if not project:
                return jsonify({'error': 'Missing project name'}), 400
            
            deleted = False
            
            # Try to delete directory-based project
            project_dir = output_dir / 'projects' / project
            if project_dir.exists():
                shutil.rmtree(str(project_dir))
                deleted = True
                logger.info(f"Deleted directory project: {project}")
            
            # Try to delete SVG-based project
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            if svg_file.exists():
                svg_file.unlink()
                deleted = True
                logger.info(f"Deleted SVG project: {project}")
            
            if deleted:
                return jsonify({'message': f'Project "{project}" deleted successfully'})
            else:
                return jsonify({'error': f'Project "{project}" not found'}), 404
                
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return jsonify({'error': f'Failed to delete project: {str(e)}'}), 500

    return app
