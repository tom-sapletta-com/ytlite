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
from datetime import datetime


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

    meta = {
        "name": name,
        "title": metadata.get("title", name),
        "date": metadata.get("date"),
        "theme": metadata.get("theme"),
        "tags": metadata.get("tags", []),
        "voice": metadata.get("voice"),
        "template": metadata.get("template", "classic"),
        "font_size": metadata.get("font_size"),
        "lang": metadata.get("lang"),
        "paragraphs": paragraphs,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "media": {
            "video_mp4": video_uri,
            "audio_mp3": audio_uri,
            "thumbnail_jpg": thumb_uri,
        },
    }

    # Compose SVG document
    # Visible layer uses the thumbnail as image so the SVG is also the miniaturka
    img_tag = (
        f"<image id=\"thumb\" href=\"{thumb_uri}\" x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\"/>"
        if thumb_uri else ""
    )
    desc = ("\n\n".join(paragraphs)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    meta_json = json.dumps(meta, ensure_ascii=False)
    meta_json_esc = meta_json.replace("<", "&lt;")
    svg = f"""
<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">
  <title>{metadata.get('title', name)}</title>
  <desc>{desc}</desc>
  <metadata>
    <rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">
      <rdf:Description>
        <script type=\"application/json\">{meta_json_esc}</script>
      </rdf:Description>
    </rdf:RDF>
  </metadata>
  {img_tag}
  <!-- Controls/overlays could be drawn here -->
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
        txt = re.sub(r"(<image[^>]*id=\"thumb\"[^>]*href=\")[^"]*(\")",
                     r"\\1" + new_thumb + r"\\2", txt)
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
