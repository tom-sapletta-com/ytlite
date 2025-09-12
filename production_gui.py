#!/usr/bin/env python3
"""
Production YTLite Web GUI - Robust Startup
With comprehensive error handling and logging
"""
import sys
import os
import traceback
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/ytlite_gui.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup paths and environment variables."""
    try:
        current_dir = Path(__file__).parent
        src_dir = current_dir / 'src'
        
        logger.info(f"Current dir: {current_dir}")
        logger.info(f"Source dir: {src_dir}")
        
        if not src_dir.exists():
            logger.error(f"Source directory does not exist: {src_dir}")
            return None, None
            
        sys.path.insert(0, str(src_dir))
        os.environ['YTLITE_FAST_TEST'] = '1'
        
        return current_dir, src_dir
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        traceback.print_exc()
        return None, None

def test_imports():
    """Test all required imports."""
    try:
        logger.info("Testing Flask import...")
        from flask import Flask
        logger.info("✓ Flask imported successfully")
        
        logger.info("Testing web_gui.routes import...")
        from web_gui.routes import setup_routes
        logger.info("✓ setup_routes imported successfully")
        
        logger.info("Testing web_gui.templates import...")
        from web_gui.templates import get_html_template
        logger.info("✓ get_html_template imported successfully")
        
        logger.info("Testing web_gui.javascript import...")
        from web_gui.javascript import get_javascript_content
        logger.info("✓ get_javascript_content imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        traceback.print_exc()
        return False

def create_flask_app(base_dir):
    """Create and configure Flask application."""
    try:
        logger.info("Creating Flask application...")
        from flask import Flask
        from web_gui.routes import setup_routes
        
        app = Flask(__name__)
        
        # Setup output directories
        output_dir = base_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        (output_dir / 'projects').mkdir(exist_ok=True)
        (output_dir / 'svg_projects').mkdir(exist_ok=True)
        
        logger.info(f"Output directory: {output_dir}")
        
        # Setup routes
        logger.info("Setting up routes...")
        setup_routes(app, base_dir, output_dir)
        
        route_count = len(list(app.url_map.iter_rules()))
        logger.info(f"✓ {route_count} routes configured")
        
        # Test routes
        logger.info("Testing routes with test client...")
        with app.test_client() as client:
            test_routes = [
                ('/', 'Index'),
                ('/api/projects', 'Projects API'),
                ('/health', 'Health check')
            ]
            
            for route, name in test_routes:
                try:
                    resp = client.get(route)
                    logger.info(f"  {name} ({route}): {resp.status_code}")
                except Exception as e:
                    logger.warning(f"  {name} ({route}): Error - {e}")
        
        return app
    except Exception as e:
        logger.error(f"Flask app creation failed: {e}")
        traceback.print_exc()
        return None

def main():
    """Main application entry point."""
    logger.info("🚀 Starting YTLite Web GUI - Production Version")
    logger.info("Features: Modular architecture, Enhanced validation, Real-time forms")
    
    try:
        # Setup environment
        base_dir, src_dir = setup_environment()
        if not base_dir:
            return 1
        
        # Test imports
        if not test_imports():
            return 1
        
        # Create Flask app
        app = create_flask_app(base_dir)
        if not app:
            return 1
        
        # Start server
        port = int(os.getenv('FLASK_PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"🌐 Starting server on http://{host}:{port}")
        logger.info("📋 All refactored components loaded successfully")
        logger.info("⏹️ Press Ctrl+C to stop the server")
        
        # Use Flask's built-in server with error handling
        try:
            app.run(
                host=host,
                port=port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"Port {port} is already in use. Try a different port.")
                return 1
            else:
                raise
        
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
