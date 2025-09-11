#!/usr/bin/env python3
"""
YTLite Web GUI
- Generate a single project in real time with preview
- Load per-project .env (uploaded or existing in output/projects/<name>/.env)
- Publish project to WordPress
- Fetch content from Nextcloud

Run: python3 -u src/web_gui.py
Open: http://localhost:5000
Optionally also run: make preview (serves /output over nginx)
"""
from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from dotenv import load_dotenv
from rich.console import Console

from dependencies import verify_dependencies
from ytlite_main import YTLite
from wordpress_publisher import WordPressPublisher
from storage_nextcloud import NextcloudClient
from logging_setup import get_logger
from progress import load_progress
from svg_packager import parse_svg_meta, update_svg_media

console = Console()
app = Flask(__name__)
logger = get_logger("web_gui")
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'output'

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>YTLite Web GUI</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 20px; }
    .box { border: 1px solid #ddd; padding: 16px; margin-bottom: 16px; border-radius: 8px; }
    label { display:block; margin-top:8px; font-weight:bold; }
    textarea { width: 100%; height: 180px; }
    input[type=text] { width: 100%; }
    .row { display: flex; gap: 16px; }
    .col { flex: 1; }
    .preview { margin-top: 16px; }
    video { width: 100%; max-width: 720px; }
    progress { width: 100%; height: 20px; }
  </style>
</head>
<body>
  <h1>YTLite Web GUI</h1>

  <div class="box">
    <h2>1) Project</h2>
    <label>Project name</label>
    <input id="project" type="text" placeholder="np. my_project" />

    <label>Markdown content</label>
    <textarea id="markdown" placeholder="---\ntitle: Mój Film\ndate: 2025-01-01\n---\n\nTreść filmu...\n"></textarea>

    <div class="row">
      <div class="col">
        <label>Voice</label>
        <select id="voice">
          <option value="pl-PL-MarekNeural">pl-PL-MarekNeural</option>
          <option value="pl-PL-ZofiaNeural">pl-PL-ZofiaNeural</option>
          <option value="de-DE-KillianNeural">de-DE-KillianNeural</option>
          <option value="de-DE-KatjaNeural">de-DE-KatjaNeural</option>
          <option value="en-US-GuyNeural">en-US-GuyNeural</option>
          <option value="en-US-AriaNeural">en-US-AriaNeural</option>
        </select>
      </div>
      <div class="col">
        <label>Theme</label>
        <select id="theme">
          <option value="tech">tech</option>
          <option value="philosophy">philosophy</option>
          <option value="wetware">wetware</option>
        </select>
      </div>
      <div class="col">
        <label>Template</label>
        <select id="template">
          <option value="classic">classic</option>
          <option value="gradient">gradient</option>
          <option value="boxed">boxed</option>
          <option value="left">left</option>
        </select>
      </div>
      <div class="col">
        <label>Font size</label>
        <input id="font_size" type="text" placeholder="48" />
      </div>
      <div class="col">
        <label>Lang</label>
        <input id="lang" type="text" placeholder="pl" />
      </div>
    </div>

    <label>Upload .env (optional, per-project)</label>
    <input id="envfile" type="file" accept=".env" />

    <div class="row">
      <div class="col">
        <button onclick="generate()">Generate</button>
        <button onclick="publishWP()">Publish to WordPress</button>
      </div>
      <div class="col" style="text-align:right">
        <a href="/output-index" target="_blank">Open Output Index</a>
      </div>
    </div>
  </div>

  <div class="box">
    <h2>2) Nextcloud (optional)</h2>
    <label>Remote path (e.g. /YT/content/sample.md)</label>
    <input id="ncpath" type="text" placeholder="/path/to/file.md" />
    <button onclick="fetchNC()">Fetch to content/episodes/</button>
  </div>

  <div class="box" id="progressBox" style="display:none">
    <h2>Progress</h2>
    <div id="progmsg">Waiting...</div>
    <progress id="progbar" value="0" max="100"></progress>
  </div>

  <div class="box">
    <h2>3) WordPress (optional, multiple targets)</h2>
    <label>WordPress URL</label>
    <input id="wp_url" type="text" placeholder="https://example.com" />
    <label>Username</label>
    <input id="wp_user" type="text" />
    <label>App Password</label>
    <input id="wp_pass" type="text" />
  </div>

  <div class="box preview" id="preview" style="display:none">
    <h2>Preview</h2>
    <div id="links"></div>
    <video id="vid" controls></video>
    <div><img id="thumb" alt="thumbnail" style="max-width:360px;margin-top:8px;"/></div>
  </div>

<script>
async function generate() {
  const project = document.getElementById('project').value.trim();
  const markdown = document.getElementById('markdown').value;
  const voice = document.getElementById('voice').value;
  const theme = document.getElementById('theme').value;
  const template = document.getElementById('template').value;
  const font_size = document.getElementById('font_size').value.trim();
  const lang = document.getElementById('lang').value.trim();
  const envfile = document.getElementById('envfile').files[0];
  if (!project) { alert('Podaj nazwę projektu'); return; }
  const fd = new FormData();
  fd.append('project', project);
  fd.append('markdown', markdown);
  fd.append('voice', voice);
  fd.append('theme', theme);
  fd.append('template', template);
  if (font_size) fd.append('font_size', font_size);
  if (lang) fd.append('lang', lang);
  if (envfile) fd.append('env', envfile);
  document.getElementById('progressBox').style.display = '';
  const timer = setInterval(async () => {
    try {
      const pr = await fetch(`/api/progress?project=${encodeURIComponent(project)}`);
      if (pr.ok) {
        const p = await pr.json();
        document.getElementById('progmsg').textContent = p.message || p.step || '';
        document.getElementById('progbar').value = p.percent || 0;
      }
    } catch (e) {}
  }, 500);

  const res = await fetch('/api/generate', { method:'POST', body: fd });
  const data = await res.json();
  clearInterval(timer);
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  document.getElementById('preview').style.display = '';
  document.getElementById('links').innerHTML = `
    <div><a href="${data.urls.index}" target="_blank">Project index</a> | 
    <a href="${data.urls.video}" target="_blank">Video</a> | 
    <a href="${data.urls.audio}" target="_blank">Audio</a></div>`;
  document.getElementById('vid').src = data.urls.video;
  document.getElementById('thumb').src = data.urls.thumb;
}

async function publishWP() {
  const project = document.getElementById('project').value.trim();
  if (!project) { alert('Podaj nazwę projektu'); return; }
  const wp_url = document.getElementById('wp_url').value.trim();
  const wp_user = document.getElementById('wp_user').value.trim();
  const wp_pass = document.getElementById('wp_pass').value.trim();
  const payload = { project };
  if (wp_url && wp_user && wp_pass) {
    payload.base_url = wp_url;
    payload.username = wp_user;
    payload.app_password = wp_pass;
  }
  const res = await fetch('/api/publish_wordpress', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  const data = await res.json();
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  alert('Published: '+(data.link || JSON.stringify(data)));
}

async function fetchNC() {
  const remote = document.getElementById('ncpath').value.trim();
  if (!remote) { alert('Podaj ścieżkę na Nextcloud'); return; }
  const res = await fetch('/api/fetch_nextcloud', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ remote_path: remote })});
  const data = await res.json();
  if (!res.ok) { alert('Error: '+(data.message||res.status)); return; }
  alert('Pobrano do: '+data.local_path);
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    logger.info("GET /")
    return render_template_string(INDEX_HTML)

@app.route('/output-index')
def output_index():
    # Serve the output README via Flask if nginx isn't running
    p = OUTPUT_DIR / 'README.md'
    if p.exists():
        logger.info("Serve output README", extra={"path": str(p)})
        return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/markdown; charset=utf-8'}
    return 'No output yet', 404

@app.route('/files/<path:subpath>')
def files(subpath: str):
    # Serve files from output/ directory for preview inside GUI (absolute path)
    logger.info("GET /files", extra={"subpath": subpath})
    return send_from_directory(str(OUTPUT_DIR), subpath, as_attachment=False)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        logger.info("POST /api/generate start")
        # Skip dependency verification in FAST_TEST mode to keep tests fast/deterministic
        if os.getenv("YTLITE_FAST_TEST") != "1":
            verify_dependencies()
        project = request.form.get('project') or (request.json and request.json.get('project'))
        markdown = request.form.get('markdown') or (request.json and request.json.get('markdown'))
        if not project:
            return jsonify({'message': 'Missing project'}), 400
        project = ''.join(c for c in project if c.isalnum() or c in ('_', '-', '.')).strip()
        if not project:
            return jsonify({'message': 'Invalid project name'}), 400

        # Handle .env upload (optional)
        proj_dir = Path('output/projects')/project
        proj_dir.mkdir(parents=True, exist_ok=True)
        if 'env' in request.files:
            envfile = request.files['env']
            env_path = proj_dir/'.env'
            envfile.save(str(env_path))
            load_dotenv(env_path)
            logger.info("Per-project .env uploaded and loaded", extra={"env": str(env_path)})
        else:
            # Load existing per-project .env if present
            env_path = proj_dir/'.env'
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Per-project .env loaded", extra={"env": str(env_path)})

        # Write markdown to content/episodes
        if markdown and markdown.strip():
            md_path = Path('content/episodes')/f"{project}.md"
            md_path.parent.mkdir(parents=True, exist_ok=True)
            if not markdown.lstrip().startswith('---'):
                # Build frontmatter from selections
                fm = ["---", f"title: {project}", f"date: {datetime.now().date()}"]
                v = request.form.get('voice');    t = request.form.get('template'); th = request.form.get('theme'); fs = request.form.get('font_size'); lg = request.form.get('lang')
                if th: fm.append(f"theme: {th}")
                if t: fm.append(f"template: {t}")
                if fs: fm.append(f"font_size: {fs}")
                if v: fm.append(f"voice: {v}")
                if lg: fm.append(f"lang: {lg}")
                fm.append("---\n")
                markdown = "\n".join(fm) + "\n" + markdown
            md_path.write_text(markdown, encoding='utf-8')
            logger.info("Markdown written", extra={"path": str(md_path)})
        else:
            md_path = Path('content/episodes')/f"{project}.md"
            if not md_path.exists():
                return jsonify({'message': 'No markdown provided and file does not exist'}), 400

        # Generate
        y = YTLite()
        y.generate_video(str(md_path))

        # Build URLs (served via Flask /files)
        urls = {
            'index': f"/files/projects/{project}/index.md",
            'video': f"/files/projects/{project}/video.mp4",
            'audio': f"/files/projects/{project}/audio.mp3",
            'thumb': f"/files/projects/{project}/thumbnail.jpg",
        }
        logger.info("POST /api/generate ok", extra={"project": project})
        return jsonify({'project': project, 'urls': urls})
    except Exception as e:
        console.print(f"[red]API generate error: {e}[/]")
        logger.error("POST /api/generate failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/publish_wordpress', methods=['POST'])
def api_publish_wordpress():
    try:
        data = request.get_json(silent=True) or {}
        project = data.get('project')
        status = data.get('status', 'draft')
        if not project:
            return jsonify({'message': 'Missing project'}), 400
        proj_dir = Path('output/projects')/project
        env_path = proj_dir/'.env'
        if env_path.exists():
            load_dotenv(env_path)
        logger.info("POST /api/publish_wordpress", extra={"project": project, "status": status})
        # Allow overriding creds via payload for multi-account publishing
        pub = WordPressPublisher(
            base_url=data.get('base_url'),
            username=data.get('username'),
            app_password=data.get('app_password'),
        )
        result = pub.publish_project(str(proj_dir), publish_status=status)
        if not result:
            logger.error("Publish failed", extra={"project": project})
            return jsonify({'message': 'Publish failed'}), 500
        logger.info("Publish ok", extra={"project": project, "id": result.get('id') if isinstance(result, dict) else None})
        return jsonify(result)
    except Exception as e:
        logger.error("POST /api/publish_wordpress failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/fetch_nextcloud', methods=['POST'])
def api_fetch_nextcloud():
    try:
        data = request.get_json(silent=True) or {}
        remote_path = data.get('remote_path')
        project = data.get('project')
        if not remote_path:
            return jsonify({'message': 'Missing remote_path'}), 400
        # Load per-project env if provided
        if project:
            proj_dir = Path('output/projects')/project
            env_path = proj_dir/'.env'
            if env_path.exists():
                load_dotenv(env_path)
        logger.info("POST /api/fetch_nextcloud", extra={"remote_path": remote_path, "project": project})
        # Download to content/episodes using original filename
        filename = Path(remote_path).name or 'download.md'
        local = Path('content/episodes')/filename
        client = NextcloudClient()
        ok = client.download_file(remote_path, str(local))
        if not ok:
            logger.error("Nextcloud download failed", extra={"remote_path": remote_path})
            return jsonify({'message': 'Download failed'}), 500
        logger.info("Nextcloud download ok", extra={"local": str(local)})
        return jsonify({'local_path': str(local)})
    except Exception as e:
        logger.error("POST /api/fetch_nextcloud failed", extra={"error": str(e)})
        return jsonify({'message': str(e)}), 500

@app.route('/api/progress')
def api_progress():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({}), 400
    prog = load_progress(project, OUTPUT_DIR)
    return jsonify(prog or {})

@app.route('/api/projects')
def api_projects():
    root = OUTPUT_DIR / 'projects'
    items = []
    for p in sorted(root.glob('*/')):
        name = p.name
        svg = next(p.glob('*.svg'), None)
        items.append({"name": name, "svg": svg.name if svg else None})
    return jsonify({"projects": items})

@app.route('/api/svg_meta')
def api_svg_meta():
    project = request.args.get('project', '').strip()
    if not project:
        return jsonify({}), 400
    pdir = OUTPUT_DIR / 'projects' / project
    svg = next(pdir.glob('*.svg'), None)
    if not svg:
        return jsonify({}), 404
    meta = parse_svg_meta(svg)
    return jsonify(meta or {})

@app.route('/api/svg_update', methods=['POST'])
def api_svg_update():
    data = request.get_json(silent=True) or {}
    project = data.get('project', '').strip()
    if not project:
        return jsonify({'message': 'Missing project'}), 400
    pdir = OUTPUT_DIR / 'projects' / project
    svg = next(pdir.glob('*.svg'), None)
    if not svg:
        return jsonify({'message': 'SVG not found'}), 404
    # Update media from current files if requested
    if data.get('refresh_media'):
        update_svg_media(svg, str(pdir / 'video.mp4'), str(pdir / 'audio.mp3'), str(pdir / 'thumbnail.jpg'))
    # Update JSON metadata fields partially if provided
    meta = parse_svg_meta(svg) or {}
    patch = data.get('metadata') or {}
    if patch:
        for k, v in patch.items():
            if k == 'media':
                meta.setdefault('media', {}).update(v or {})
            else:
                meta[k] = v
        # write back by injecting new JSON
        import re, json as _json
        txt = svg.read_text(encoding='utf-8')
        m = re.search(r"<script type=\"application/json\">(.*?)</script>", txt, flags=re.S)
        if not m:
            return jsonify({'message': 'SVG meta block missing'}), 500
        new_json = _json.dumps(meta, ensure_ascii=False).replace('<', '&lt;')
        new_txt = txt[:m.start(1)] + new_json + txt[m.end(1):]
        svg.write_text(new_txt, encoding='utf-8')
    return jsonify({'ok': True, 'svg': svg.name})


if __name__ == '__main__':
    # Optionally verify deps at startup
    try:
        verify_dependencies()
    except SystemExit:
        pass
    app.run(host='0.0.0.0', port=5000, debug=False)
