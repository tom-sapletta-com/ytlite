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
import shutil


def _b64_data_uri(path: Path, mime: str) -> str:
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _backup_current_version(project_dir: Path, svg_path: Path) -> None:
    """Create a versioned backup of the current SVG file."""
    versions_dir = project_dir / 'versions'
    versions_dir.mkdir(exist_ok=True)
    
    # Find next version number
    existing_versions = list(versions_dir.glob('*.svg'))
    next_version = len(existing_versions) + 1
    
    # Create backup filename
    backup_name = f"{svg_path.stem}_v{next_version}.svg"
    backup_path = versions_dir / backup_name
    
    # Copy current SVG to versions directory
    shutil.copy2(svg_path, backup_path)
    print(f"Created version backup: {backup_path}")


def _validate_svg(svg_path: Path) -> tuple[bool, list[str]]:
    """Validate SVG file using xmllint if available."""
    try:
        import subprocess
        result = subprocess.run(['xmllint', '--noout', str(svg_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, []
        else:
            errors = [result.stderr.strip()] if result.stderr else ['XML validation failed']
            return False, errors
    except FileNotFoundError:
        # xmllint not available, do basic checks
        try:
            content = svg_path.read_text()
            if not content.strip().startswith('<svg'):
                return False, ['File does not start with <svg tag']
            if '</svg>' not in content:
                return False, ['Missing closing </svg> tag']
            return True, ['Basic validation passed (xmllint not available)']
        except Exception as e:
            return False, [f'Failed to read SVG file: {str(e)}']


def _fix_common_xml_issues(svg_content: str) -> str:
    """Fix common XML issues in SVG content."""
    import re
    
    # Fix boolean attributes that need explicit values in XML
    fixes = [
        (r'<video\s+([^>]*\s+)?controls(\s+[^>]*)?>', r'<video \1controls="controls"\2>'),
        (r'<audio\s+([^>]*\s+)?controls(\s+[^>]*)?>', r'<audio \1controls="controls"\2>'),
        (r'<video\s+([^>]*\s+)?autoplay(\s+[^>]*)?>', r'<video \1autoplay="autoplay"\2>'),
        (r'<audio\s+([^>]*\s+)?autoplay(\s+[^>]*)?>', r'<audio \1autoplay="autoplay"\2>'),
        (r'<[^>]+\s+loop(\s+[^>]*)?>', lambda m: m.group(0).replace(' loop', ' loop="loop"')),
        (r'<[^>]+\s+muted(\s+[^>]*)?>', lambda m: m.group(0).replace(' muted', ' muted="muted"')),
    ]
    
    fixed_content = svg_content
    for pattern, replacement in fixes:
        fixed_content = re.sub(pattern, replacement, fixed_content)
    
    # Escape special characters in text content
    # (This is a simplified version - in production you'd want more comprehensive escaping)
    fixed_content = fixed_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # But restore valid XML tags
    fixed_content = re.sub(r'&lt;(\/?[a-zA-Z][^&]*?)&gt;', r'<\1>', fixed_content)
    
    return fixed_content


def validate_and_fix_svg(svg_path: Path) -> tuple[bool, list[str]]:
    """Validate SVG and attempt to fix common issues if validation fails."""
    is_valid, errors = _validate_svg(svg_path)
    
    if not is_valid:
        print("🔧 Attempting to fix common XML issues...")
        content = svg_path.read_text(encoding="utf-8")
        fixed_content = _fix_common_xml_issues(content)
        
        if fixed_content != content:
            svg_path.write_text(fixed_content, encoding="utf-8")
            is_valid, errors = _validate_svg(svg_path)
            
            if is_valid:
                print(f"✓ Successfully fixed XML issues in: {svg_path}")
            else:
                print(f"⚠ Issues remain after automatic fix")
    
    return is_valid, errors


def build_svg(project_dir: str | Path, metadata: dict, paragraphs: list,
              video_path: str | None, audio_path: str | None, thumb_path: str | None) -> tuple[Path, bool, list[str]]:
    """
    Build SVG with comprehensive validation.
    Returns: (svg_path, is_valid, validation_errors)
    """
    pdir = Path(project_dir)
    name = pdir.name
    svg_path = pdir / f"{name}.svg"
    
    # Create version backup if SVG already exists
    if svg_path.exists():
        _backup_current_version(pdir, svg_path)

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
          <audio controls="controls" style="width:100%;">
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

    # Write SVG content
    svg_path.write_text(svg, encoding="utf-8")
    
    # Validate the generated SVG
    is_valid, errors = _validate_svg(svg_path)
    if is_valid:
        print(f"✓ Generated valid SVG: {svg_path}")
    else:
        print(f"⚠ SVG validation issues in {svg_path}:")
        for error in errors:
            print(f"  - {error}")
        
        # Attempt automatic fix for common issues
        print("🔧 Attempting to fix common XML issues...")
        fixed_svg = _fix_common_xml_issues(svg)
        if fixed_svg != svg:
            svg_path.write_text(fixed_svg, encoding="utf-8")
            is_valid, errors = _validate_svg(svg_path)
            if is_valid:
                print(f"✓ Successfully fixed and validated SVG: {svg_path}")
            else:
                print(f"⚠ Issues remain after automatic fix:")
                for error in errors:
                    print(f"  - {error}")
    
    return svg_path, is_valid, errors


def update_svg_media(svg_path: str | Path, video_path: Optional[str] = None,
                     audio_path: Optional[str] = None, thumb_path: Optional[str] = None) -> tuple[bool, bool, list[str]]:
    """
    Update SVG media content with validation.
    Returns: (operation_success, is_valid, validation_errors)
    """
    p = Path(svg_path)
    if not p.exists():
        return False, False, ['SVG file not found']
    
    # Create backup before editing
    if p.exists():
        _backup_current_version(p.parent, p)
    
    txt = p.read_text(encoding="utf-8")
    # Naive replacement of the JSON block; parse and update
    import re
    m = re.search(r"<script type=\"application/json\">(.*?)</script>", txt, flags=re.S)
    if not m:
        return False, False, ['No JSON metadata block found in SVG']
    
    js = m.group(1).replace("&lt;", "<")
    try:
        meta = json.loads(js)
    except Exception as e:
        return False, False, [f'Failed to parse JSON metadata: {str(e)}']
        
    # Update media content
    if video_path and Path(video_path).exists():
        meta.setdefault("media", {})["video_mp4"] = _b64_data_uri(Path(video_path), "video/mp4")
        print(f"Updated video content from {video_path}")
        
    if audio_path and Path(audio_path).exists():
        meta.setdefault("media", {})["audio_mp3"] = _b64_data_uri(Path(audio_path), "audio/mpeg")
        print(f"Updated audio content from {audio_path}")
        
    if thumb_path and Path(thumb_path).exists():
        meta.setdefault("media", {})["thumbnail_jpg"] = _b64_data_uri(Path(thumb_path), "image/jpeg")
        # Also update visible image href
        new_thumb = meta["media"]["thumbnail_jpg"]
        txt = re.sub(r'(<image[^>]*id="thumb"[^>]*href=")[^"]*(")',
                     r'\1' + new_thumb + r'\2', txt)
        print(f"Updated thumbnail from {thumb_path}")
    
    # Write back updated content
    new_json = json.dumps(meta, ensure_ascii=False).replace("<", "&lt;")
    new_txt = txt[:m.start(1)] + new_json + txt[m.end(1):]
    p.write_text(new_txt, encoding="utf-8")
    
    # Validate the updated SVG
    is_valid, errors = validate_and_fix_svg(p)
    
    if is_valid:
        print(f"✓ SVG media updated and validated: {p}")
    else:
        print(f"⚠ SVG validation issues after media update:")
        for error in errors:
            print(f"  - {error}")
    
    return True, is_valid, errors


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
