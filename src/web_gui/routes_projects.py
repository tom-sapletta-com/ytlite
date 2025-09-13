#!/usr/bin/env python3
"""
Project listing and metadata routes extracted from routes.py
- /api/projects
- /api/svg_meta
- /api/svg_metadata
- /api/delete_project
"""
from __future__ import annotations

from pathlib import Path
from flask import request, jsonify


def register_project_routes(app, output_dir: Path, logger) -> None:
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
                    'metadata': None
                })
            return jsonify({'projects': projects})
        except Exception as e:
            logger.error(f"Error listing projects: {e}", exc_info=True)
            return jsonify({'message': str(e)}), 500

    @app.route('/api/svg_meta', methods=['GET'])
    def api_svg_meta():
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
                try:
                    import frontmatter
                    fm = frontmatter.loads(content)
                    meta_dict = fm.get('meta') or {}
                    metadata['theme'] = fm.get('theme') or meta_dict.get('theme')
                    metadata['template'] = fm.get('template') or meta_dict.get('template')
                    metadata['voice'] = fm.get('voice') or meta_dict.get('voice')
                    metadata['font_size'] = fm.get('font_size') or fm.get('fontSize') or meta_dict.get('font_size')
                    metadata['lang'] = fm.get('lang') or fm.get('language') or meta_dict.get('lang')
                except Exception as _e:
                    logger.warning(f"Frontmatter parse failed for {project}: {_e}")
                return jsonify({'project': project, 'metadata': metadata})
            return jsonify({'error': 'Project not found'}), 404
        except Exception as e:
            logger.error(f"Failed to get metadata for {project}: {e}")
            return jsonify({'error': 'Failed to read project metadata'}), 500

    @app.route('/api/delete_project', methods=['POST'])
    def api_delete_project():
        try:
            data = request.get_json()
            project = data.get('project', '').strip()
            if not project:
                return jsonify({'error': 'Missing project name'}), 400
            deleted = False
            # Try to delete directory-based project
            project_dir = output_dir / 'projects' / project
            if project_dir.exists():
                import shutil
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
