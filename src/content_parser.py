#!/usr/bin/env python3
"""
YTLite Content Parser Module
Handles markdown parsing and content extraction
"""

import frontmatter
from pathlib import Path
from datetime import datetime
from rich.console import Console
from logging_setup import get_logger

console = Console()
logger = get_logger("content_parser")

class ContentParser:
    def __init__(self):
        pass
    
    def parse_markdown(self, file_path: str):
        """Parse markdown file with frontmatter"""
        console.print(f"[cyan]Parsing {file_path}...[/]")
        logger.info("parse_markdown start", extra={"file": file_path})
        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        # Try robust frontmatter parse; fall back to raw content if YAML is invalid
        post_meta = {}
        post_content = ""
        try:
            post = frontmatter.loads(raw_text)
            post_meta = post.metadata or {}
            post_content = (post.content or "").strip()
        except Exception as e:
            console.print(f"[yellow]Warning: Invalid frontmatter in {file_path}: {e}. Falling back to raw content.[/]")
            logger.warning("Invalid frontmatter, fallback to raw content", extra={"file": file_path, "error": str(e)})
            # Remove frontmatter block if present (--- ... ---)
            text = raw_text
            lines = text.splitlines()
            if lines and lines[0].strip() == '---':
                # find closing '---'
                idx = 1
                while idx < len(lines) and lines[idx].strip() != '---':
                    idx += 1
                if idx < len(lines):
                    post_content = "\n".join(lines[idx+1:]).strip()
                else:
                    post_content = "\n".join(lines[1:]).strip()
            else:
                post_content = text.strip()

        # Extract metadata with defaults
        metadata = {
            'title': post_meta.get('title', Path(file_path).stem),
            'date': post_meta.get('date', datetime.now().strftime('%Y-%m-%d')),
            'theme': post_meta.get('theme', 'tech'),
            'tags': post_meta.get('tags', []),
        }
        
        # Split content into paragraphs
        content = post_content
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            console.print("[yellow]Warning: No content found in markdown file[/]")
            paragraphs = [metadata['title']]
        logger.info("parse_markdown done", extra={"title": metadata.get('title'), "paragraphs": len(paragraphs)})
        
        return metadata, paragraphs
    
    def prepare_content_for_video(self, paragraphs: list, max_chars: int = 200):
        """Prepare text for video slides"""
        slides = []
        
        for paragraph in paragraphs:
            # Split long paragraphs
            if len(paragraph) > max_chars:
                words = paragraph.split()
                current_slide = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > max_chars:
                        slides.append(' '.join(current_slide))
                        current_slide = [word]
                        current_length = len(word)
                    else:
                        current_slide.append(word)
                        current_length += len(word) + 1
                
                if current_slide:
                    slides.append(' '.join(current_slide))
            else:
                slides.append(paragraph)
        
        return slides
