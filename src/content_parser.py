#!/usr/bin/env python3
"""
YTLite Content Parser Module
Handles markdown parsing and content extraction
"""

import frontmatter
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

class ContentParser:
    def __init__(self):
        pass
    
    def parse_markdown(self, file_path: str):
        """Parse markdown file with frontmatter"""
        console.print(f"[cyan]Parsing {file_path}...[/]")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract metadata
        metadata = {
            'title': post.metadata.get('title', Path(file_path).stem),
            'date': post.metadata.get('date', datetime.now().strftime('%Y-%m-%d')),
            'theme': post.metadata.get('theme', 'tech'),
            'tags': post.metadata.get('tags', []),
        }
        
        # Split content into paragraphs
        content = post.content.strip()
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            console.print("[yellow]Warning: No content found in markdown file[/]")
            paragraphs = [metadata['title']]
        
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
