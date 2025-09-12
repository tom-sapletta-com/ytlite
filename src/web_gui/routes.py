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

logger = get_logger("web_gui.routes")

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

    @app.route('/favicon.ico')
    def favicon():
        """Handle favicon requests"""
        return '', 204

    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        """Serve the JavaScript content."""
        try:
            from . import javascript
            return javascript.get_javascript_content(), 200, {'Content-Type': 'application/javascript'}
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

    @app.route('/api/generate', methods=['POST'])
    def api_generate():
        """Generate a new project or update existing one."""
        try:
            logger.info("POST /api/generate start")
            data = request.form.to_dict()
            logger.debug(f"Request form data: {data}")
            project = data.get('project', '').strip()
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

            from .helpers import create_svg_project
            
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
                
                result = create_svg_project(
                    project_name=project,
                    content=data.get('markdown', ''),
                    metadata=metadata,
                    output_path=str(svg_file)
                )
                
                if result:
                    logger.info(f"✅ SVG project creation successful for {project}")
                    logger.info(f"   📄 SVG file: {svg_file}")
                    logger.info(f"   📏 File size: {svg_file.stat().st_size if svg_file.exists() else 'Unknown'} bytes")
                    
                    # Log embedded media information
                    try:
                        svg_content = svg_file.read_text()
                        video_count = svg_content.count('data:video')
                        audio_count = svg_content.count('data:audio')
                        image_count = svg_content.count('data:image')
                        
                        if video_count > 0 or audio_count > 0 or image_count > 0:
                            logger.info(f"   📎 Embedded media - Videos: {video_count}, Audio: {audio_count}, Images: {image_count}")
                        else:
                            logger.info(f"   📎 No embedded media found")
                    except Exception as media_log_error:
                        logger.warning(f"Could not analyze embedded media: {media_log_error}")
                    
                    return jsonify({
                        'message': f'Project "{project}" generated successfully',
                        'project': project,
                        'svg_file': f"svg_projects/{project}.svg",
                        'type': 'svg'
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

            from wordpress_publisher import WordPressPublisher
            pub = WordPressPublisher()
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
                from wordpress_publisher import WordPressPublisher
                publisher = WordPressPublisher()
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
            from storage_nextcloud import NextcloudClient
            client = NextcloudClient()
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
                try:
                    from svg_packager import parse_svg_meta
                    svg_content = svg_file.read_text(encoding='utf-8')
                    metadata = parse_svg_meta(svg_content)
                    projects.append({
                        'name': svg_file.stem,
                        'svg': svg_file.name,
                        'type': 'svg',
                        'metadata': metadata
                    })
                except Exception as e:
                    logger.warning(f"Failed to read SVG metadata for {svg_file}: {e}")
                    projects.append({
                        'name': svg_file.stem,
                        'svg': svg_file.name,
                        'type': 'svg',
                        'metadata': {}
                    })
            
            return jsonify({'projects': projects})
        except Exception as e:
            logger.error(f"Error listing projects: {e}", exc_info=True)
            return jsonify({'message': str(e)}), 500

    @app.route('/api/svg_meta', methods=['GET'])
    def api_svg_meta():
        """API endpoint to get metadata for all SVG files in the output directory, streamed to save memory."""
        from svg_packager import parse_svg_meta
        import json
        from flask import Response

        def generate_metadata():
            svg_projects_dir = output_dir / 'svg_projects'
            if not svg_projects_dir.exists():
                yield '[]'
                return

            yield '['
            first = True
            for svg_file in svg_projects_dir.glob('*.svg'):
                try:
                    meta = parse_svg_meta(svg_file)
                    if meta:
                        if not first:
                            yield ','
                        yield json.dumps(meta)
                        first = False
                except Exception as e:
                    logger.warning(f"Failed to process SVG metadata for {svg_file.name}: {e}")
            yield ']'

        return Response(generate_metadata(), mimetype='application/json')

    @app.route('/api/svg_metadata')
    def api_svg_metadata():
        """Get metadata from SVG project file."""
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'error': 'Missing project parameter'}), 400
        
        try:
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            if not svg_file.exists():
                return jsonify({'error': 'SVG project not found'}), 404
            
            from svg_packager import parse_svg_meta
            svg_content = svg_file.read_text(encoding='utf-8')
            metadata = parse_svg_meta(svg_content)
            
            return jsonify({
                'project': project,
                'metadata': metadata or {},
                'svg_file': f"svg_projects/{project}.svg"
            })
            
        except Exception as e:
            logger.error(f"Failed to get SVG metadata for {project}: {e}")
            return jsonify({'error': 'Failed to read SVG metadata'}), 500

    @app.route('/api/validate_project')
    def api_validate_project():
        """Validate a project's SVG and media files."""
        project = request.args.get('project', '').strip()
        if not project:
            return jsonify({'error': 'Missing project parameter'}), 400
        try:
            from validator import validate_project_files
            from svg_validator import SVGValidator
            
            errors = []
            warnings = []
            
            # Check if project exists
            project_dir = output_dir / 'projects' / project
            svg_file = output_dir / 'svg_projects' / f"{project}.svg"
            
            if svg_file.exists():
                # Validate SVG project
                try:
                    validator = SVGValidator(str(svg_file))
                    is_valid, validation_errors = validator.validate()
                    
                    if not is_valid:
                        errors.extend(validation_errors)
                    
                    from svg_packager import parse_svg_meta
                    metadata = parse_svg_meta(str(svg_file))
                    
                    if not metadata:
                        warnings.append("No metadata found in SVG")
                    
                    # Validate data URIs
                    svg_content = svg_file.read_text()
                    if 'data:video' in svg_content:
                        # Basic validation for video data URIs
                        video_count = svg_content.count('data:video')
                        if video_count > 0:
                            logger.info(f"Found {video_count} video data URI(s) in {project}")
                    
                    if 'data:audio' in svg_content:
                        audio_count = svg_content.count('data:audio')
                        if audio_count > 0:
                            logger.info(f"Found {audio_count} audio data URI(s) in {project}")
                    
                except Exception as e:
                    errors.append(f"SVG validation failed: {str(e)}")
                    
            elif project_dir.exists():
                # Validate directory project
                try:
                    validation_result = validate_project_files(str(project_dir))
                    
                    if not validation_result.get('valid', False):
                        errors.extend(validation_result.get('errors', []))
                    
                    warnings.extend(validation_result.get('warnings', []))
                    
                except Exception as e:
                    errors.append(f"Project validation failed: {str(e)}")
            else:
                errors.append("Project not found")
            
            is_valid = len(errors) == 0
            
            return jsonify({
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'project': project
            })
            
        except Exception as e:
            logger.error(f"Failed to validate project {project}: {e}")
            return jsonify({'error': f'Validation failed: {str(e)}'}), 500

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
