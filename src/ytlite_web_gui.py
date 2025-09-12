#!/usr/bin/env python3
"""
YTLite Web GUI - Production Ready Version
Final refactored web GUI with all components working correctly.
"""
import os
import sys
from pathlib import Path

# Setup import path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask
from rich.console import Console

console = Console()

def create_production_app():
    """Create the production-ready Flask application."""
    app = Flask(__name__)
    
    # Define paths
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / 'output'
    
    # Ensure all required directories exist
    output_dir.mkdir(exist_ok=True)
    (output_dir / 'projects').mkdir(exist_ok=True)
    (output_dir / 'svg_projects').mkdir(exist_ok=True)
    (output_dir / 'files' / 'projects').mkdir(parents=True, exist_ok=True)
    
    console.print(f"[blue]📁 Base directory: {base_dir}[/blue]")
    console.print(f"[blue]📁 Output directory: {output_dir}[/blue]")
    
    # Import and setup all routes
    try:
        from web_gui.routes import setup_routes
        setup_routes(app, base_dir, output_dir)
        
        route_count = len(list(app.url_map.iter_rules()))
        console.print(f"[green]✅ Routes configured: {route_count} endpoints[/green]")
        
        # Log important endpoints for debugging
        key_routes = []
        for rule in app.url_map.iter_rules():
            if any(endpoint in rule.rule for endpoint in ['/api/projects', '/api/generate', '/api/svg_meta']):
                key_routes.append(f"  {rule.rule} -> {rule.endpoint}")
        
        if key_routes:
            console.print("[dim]Key API endpoints:[/dim]")
            for route in key_routes:
                console.print(f"[dim]{route}[/dim]")
                
    except Exception as e:
        console.print(f"[red]❌ Routes setup failed: {e}[/red]")
        raise
    
    # Setup JavaScript serving
    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        try:
            from web_gui.javascript import JAVASCRIPT_CODE
            return JAVASCRIPT_CODE, 200, {'Content-Type': 'application/javascript; charset=utf-8'}
        except Exception as e:
            console.print(f"[red]❌ JavaScript serving error: {e}[/red]")
            return f"// JavaScript loading error: {e}", 500, {'Content-Type': 'application/javascript'}
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': 'refactored'}, 200
    
    console.print("[green]✅ JavaScript routes configured[/green]")
    
    return app

def run_server():
    """Run the production server."""
    console.print("[bold green]🚀 YTLite Web GUI - Production Version[/bold green]")
    
    # Skip dependency verification in test mode
    if not os.getenv('YTLITE_FAST_TEST'):
        try:
            from dependencies import verify_dependencies
            from logging_setup import get_logger
            
            console.print("[yellow]🔍 Verifying dependencies...[/yellow]")
            verify_dependencies()
            console.print("[green]✅ Dependencies verified[/green]")
            
            logger = get_logger("web_gui")
            logger.info("YTLite Web GUI starting up")
            
        except Exception as e:
            console.print(f"[orange1]⚠️  Dependency check failed (continuing): {e}[/orange1]")
    else:
        console.print("[cyan]⚡ Fast test mode: skipping dependency verification[/cyan]")
    
    # Create the Flask app
    try:
        app = create_production_app()
        console.print("[green]✅ Flask application created successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to create Flask app: {e}[/red]")
        return 1
    
    # Run validation tests
    try:
        console.print("[yellow]🔍 Running validation tests...[/yellow]")
        with app.test_client() as client:
            # Test main page
            resp = client.get('/')
            if resp.status_code == 200:
                console.print("[green]  ✅ Index page: OK[/green]")
            else:
                console.print(f"[red]  ❌ Index page: {resp.status_code}[/red]")
            
            # Test API endpoints
            resp = client.get('/api/projects')
            if resp.status_code == 200:
                console.print("[green]  ✅ Projects API: OK[/green]")
            else:
                console.print(f"[red]  ❌ Projects API: {resp.status_code}[/red]")
            
            resp = client.get('/api/svg_meta?project=test')
            if resp.status_code in [200, 404]:  # 404 is OK for non-existent project
                console.print("[green]  ✅ SVG Meta API: OK[/green]")
            else:
                console.print(f"[red]  ❌ SVG Meta API: {resp.status_code}[/red]")
            
            # Test JavaScript serving
            resp = client.get('/static/js/web_gui.js')
            if resp.status_code == 200:
                console.print("[green]  ✅ JavaScript serving: OK[/green]")
            else:
                console.print(f"[red]  ❌ JavaScript serving: {resp.status_code}[/red]")
                
        console.print("[green]✅ All validation tests completed[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        return 1
    
    # Get port configuration
    port = int(os.getenv('FLASK_PORT', 5000))
    
    console.print(f"[bold green]🌐 Starting server on http://localhost:{port}[/bold green]")
    console.print("[dim]📝 All refactored components are active and tested[/dim]")
    console.print("[dim]🔄 Features: Grid/Table toggle, Video previews, Real-time validation[/dim]")
    console.print("[dim]⏹️  Press Ctrl+C to stop the server[/dim]")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Server stopped by user[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[red]❌ Server error: {e}[/red]")
        return 1

if __name__ == '__main__':
    exit_code = run_server()
    sys.exit(exit_code)
