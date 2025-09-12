#!/usr/bin/env python3
"""
YTLite Web GUI - Working Version
Combines the modular refactored components with a reliable startup process.
"""
import os
import sys
from pathlib import Path

# Ensure proper import path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from rich.console import Console

console = Console()

def create_working_app():
    """Create a working Flask app with all refactored components."""
    app = Flask(__name__)
    
    # Define paths  
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / 'output'
    
    # Ensure directories exist
    output_dir.mkdir(exist_ok=True)
    (output_dir / 'projects').mkdir(exist_ok=True)
    (output_dir / 'svg_projects').mkdir(exist_ok=True)
    
    console.print(f"[blue]📁 Base dir: {base_dir}[/blue]")
    console.print(f"[blue]📁 Output dir: {output_dir}[/blue]")
    
    # Import and setup routes
    try:
        from web_gui.routes import setup_routes
        setup_routes(app, base_dir, output_dir)
        console.print(f"[green]✓ Routes setup: {len(list(app.url_map.iter_rules()))} endpoints[/green]")
    except Exception as e:
        console.print(f"[red]✗ Routes setup failed: {e}[/red]")
        raise
    
    # Add JavaScript serving
    @app.route('/static/js/web_gui.js')
    def serve_javascript():
        from web_gui.javascript import JAVASCRIPT_CODE
        return JAVASCRIPT_CODE, 200, {'Content-Type': 'application/javascript'}
    
    console.print("[green]✓ JavaScript route added[/green]")
    
    return app

def main():
    """Main function to run the web GUI."""
    console.print("[bold green]🚀 Starting YTLite Web GUI (Working Version)[/bold green]")
    
    # Skip dependency check in fast test mode
    if not os.getenv('YTLITE_FAST_TEST'):
        try:
            from dependencies import verify_dependencies
            console.print("[yellow]⏳ Verifying dependencies...[/yellow]")
            verify_dependencies()
            console.print("[green]✓ Dependencies verified[/green]")
        except Exception as e:
            console.print(f"[orange1]⚠️  Dependency check skipped: {e}[/orange1]")
    
    # Create the app
    try:
        app = create_working_app()
        console.print("[green]✓ Flask app created successfully[/green]")
    except Exception as e:
        console.print(f"[red]✗ App creation failed: {e}[/red]")
        return 1
    
    # Test the app quickly
    try:
        with app.test_client() as client:
            resp = client.get('/')
            console.print(f"[green]✓ Index route test: {resp.status_code}[/green]")
            
            resp = client.get('/api/projects')  
            console.print(f"[green]✓ Projects API test: {resp.status_code}[/green]")
    except Exception as e:
        console.print(f"[red]✗ App test failed: {e}[/red]")
        return 1
    
    # Get port
    port = int(os.getenv('FLASK_PORT', 5000))
    
    console.print(f"[bold green]🌐 Server starting on http://localhost:{port}[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]✗ Server error: {e}[/red]")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
