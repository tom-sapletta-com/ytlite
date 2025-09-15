from flask import Flask
from pathlib import Path
import os
import sys

def create_app(config_overrides=None):
    """Create and configure the Flask app using the factory pattern."""
    
    # Project root is three levels up from this file (src/web_gui/__init__.py)
    project_root = Path(__file__).parent.parent.parent

    app = Flask(
        __name__,
        template_folder=str(project_root / 'templates'),
        static_folder=str(project_root / 'web_static')
    )

    # Basic configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        TESTING=False,
    )

    if config_overrides:
        app.config.update(config_overrides)

    from .routes import setup_routes

    base_dir = project_root
    output_dir = base_dir / 'output'
    output_dir.mkdir(exist_ok=True)

    # In testing, we might want to use a different output dir
    if app.config['TESTING']:
        test_output_dir = base_dir / 'tests' / 'output'
        test_output_dir.mkdir(exist_ok=True)
        output_dir = test_output_dir

    # Setup routes
    with app.app_context():
        setup_routes(app, base_dir, output_dir)

    return app
