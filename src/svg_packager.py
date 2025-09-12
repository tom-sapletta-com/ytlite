#!/usr/bin/env python3
"""
SVG Packager: produce a single-file SVG artifact for a project with embedded metadata
and data URIs for media (video, audio, thumbnail). Also provides update helpers.

The generated SVG is visually the thumbnail image, so it serves as a miniaturka.
Metadata is stored inside <metadata> as JSON and inside <desc> for human readability.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone


def _b64_data_uri(path: Path, mime: str) -> str:
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_svg(project_dir: str | Path, metadata: dict, paragraphs: list,
              video_path: str | None, audio_path: str | None, thumb_path: str | None) -> Path:
    pdir = Path(project_dir)
    name = pdir.name
    svg_path = pdir / f"{name}.svg"

    # Visible content: thumbnail image if present
    width, height = 1280, 720
    thumb_uri = None
    if thumb_path and Path(thumb_path).exists():
        thumb_uri = _b64_data_uri(Path(thumb_path), "image/jpeg")

    # Data URIs for media
    video_uri = None
    if video_path and Path(video_path).exists():
        video_uri = _b64_data_uri(Path(video_path), "video/mp4")
    audio_uri = None
    if audio_path and Path(audio_path).exists():
        audio_uri = _b64_data_uri(Path(audio_path), "audio/mpeg")

    # Convert date objects to strings for JSON serialization
    date_val = metadata.get("date")
    if hasattr(date_val, 'isoformat'):
        date_val = date_val.isoformat()
    elif date_val:
        date_val = str(date_val)

    meta = {
        "name": name,
        "title": metadata.get("title", name),
        "date": date_val,
        "theme": metadata.get("theme"),
        "tags": metadata.get("tags", []),
        "voice": metadata.get("voice"),
        "template": metadata.get("template", "classic"),
        "font_size": metadata.get("font_size"),
        "lang": metadata.get("lang"),
        "paragraphs": paragraphs,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "media": {
            "video_mp4": video_uri,
            "audio_mp3": audio_uri,
            "thumbnail_jpg": thumb_uri,
        },
    }

    # Compose interactive SVG document with embedded video player and metadata display
    img_tag = (
        f"<image id=\"thumb\" href=\"{thumb_uri}\" x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" style=\"cursor:pointer\"/>"
        if thumb_uri else ""
    )
    desc = ("\n\n".join(paragraphs)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    meta_json = json.dumps(meta, ensure_ascii=False)
    meta_json_esc = meta_json.replace("<", "&lt;")
    
    # Create interactive SVG with embedded video player and metadata display
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>{metadata.get('title', name)}</title>
  <desc>{desc}</desc>
  <metadata>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description>
        <script type="application/json">{meta_json_esc}</script>
      </rdf:Description>
    </rdf:RDF>
  </metadata>
  
  <!-- Embedded HTML with video player and metadata -->
  <foreignObject x="0" y="0" width="{width}" height="{height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="width:100%; height:100%; font-family:Arial,sans-serif; background:#1a1a1a; color:#fff; overflow:auto;">
      <div style="padding:20px;">
        <!-- Video Player -->
        <div style="text-align:center; margin-bottom:20px;">
          <video id="mainVideo" controls="controls" autoplay="autoplay" style="max-width:100%; height:auto; background:#000;">
            <source src="{video_uri}" type="video/mp4"/>
            Your browser does not support the video tag.
          </video>
        </div>
        
        <!-- Title and Metadata -->
        <h1 style="color:#00ff88; margin:0 0 10px 0; font-size:28px;">{metadata.get('title', name)}</h1>
        <div style="background:#2a2a2a; padding:15px; border-radius:8px; margin-bottom:20px;">
          <div style="display:grid; grid-template-columns:150px 1fr; gap:10px; font-size:14px;">
            <strong>Date:</strong> <span>{meta.get('date', 'N/A')}</span>
            <strong>Theme:</strong> <span>{meta.get('theme', 'N/A')}</span>
            <strong>Template:</strong> <span>{meta.get('template', 'N/A')}</span>
            <strong>Voice:</strong> <span>{meta.get('voice', 'N/A')}</span>
            <strong>Language:</strong> <span>{meta.get('lang', 'N/A')}</span>
            <strong>Created:</strong> <span>{meta.get('created_at', 'N/A')}</span>
          </div>
        </div>
        
        <!-- Content -->
        <div style="background:#333; padding:15px; border-radius:8px; margin-bottom:20px;">
          <h3 style="color:#00ff88; margin-top:0;">Content:</h3>
          <div style="line-height:1.6;">{desc}</div>
        </div>
        
        <!-- Audio Player -->
        <div style="background:#2a2a2a; padding:15px; border-radius:8px;">
          <h3 style="color:#00ff88; margin-top:0;">Audio:</h3>
          <audio controls style="width:100%;">
            <source src="{audio_uri}" type="audio/mpeg"/>
            Your browser does not support the audio tag.
          </audio>
        </div>
      </div>
    </div>
  </foreignObject>
  
  <!-- Fallback: thumbnail image for non-browser environments -->
  {img_tag}
</svg>
""".strip()

    svg_path.write_text(svg, encoding="utf-8")
    return svg_path


def update_svg_media(svg_path: str | Path, video_path: Optional[str] = None,
                     audio_path: Optional[str] = None, thumb_path: Optional[str] = None) -> bool:
    p = Path(svg_path)
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8")
    # Naive replacement of the JSON block; parse and update
    import re
    m = re.search(r"<script type=\"application/json\">(.*?)</script>", txt, flags=re.S)
    if not m:
        return False
    js = m.group(1).replace("&lt;", "<")
    try:
        meta = json.loads(js)
    except Exception:
        return False
    if video_path and Path(video_path).exists():
        meta.setdefault("media", {})["video_mp4"] = _b64_data_uri(Path(video_path), "video/mp4")
    if audio_path and Path(audio_path).exists():
        meta.setdefault("media", {})["audio_mp3"] = _b64_data_uri(Path(audio_path), "audio/mpeg")
    if thumb_path and Path(thumb_path).exists():
        meta.setdefault("media", {})["thumbnail_jpg"] = _b64_data_uri(Path(thumb_path), "image/jpeg")
        # Also update visible image href
        new_thumb = meta["media"]["thumbnail_jpg"]
        txt = re.sub(r'(<image[^>]*id="thumb"[^>]*href=")[^"]*(")',
                     r'\1' + new_thumb + r'\2', txt)
    # Write back
    new_json = json.dumps(meta, ensure_ascii=False).replace("<", "&lt;")
    new_txt = txt[:m.start(1)] + new_json + txt[m.end(1):]
    p.write_text(new_txt, encoding="utf-8")
    return True


def parse_svg_meta(svg_path: str | Path) -> Optional[dict]:
    p = Path(svg_path)
    if not p.exists():
        return None
    import re
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"<script type=\"application/json\">(.*?)</script>", txt, flags=re.S)
    if not m:
        return None
    js = m.group(1).replace("&lt;", "<")
    try:
        return json.loads(js)
    except Exception:
        return None
