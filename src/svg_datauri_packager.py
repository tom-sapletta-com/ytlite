#!/usr/bin/env python3
"""
SVG DataURI Packager - Single-file SVG projects with embedded media
Creates self-contained SVG files with:
- Embedded video/audio as data URIs
- Project metadata in SVG elements
- Interactive video player
- Thumbnail integration
"""

import base64
import json
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
import xml.etree.ElementTree as ET
from datetime import datetime

from logging_setup import get_logger

logger = get_logger("svg_datauri_packager")

class SVGDataURIPackager:
    """Creates single-file SVG projects with embedded media as data URIs."""
    
    def __init__(self):
        self.namespace = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink',
            'ytlite': 'https://ytlite.com/ns'
        }
    
    def create_svg_project(self, project_name: str, metadata: Dict[str, Any], 
                          video_path: Optional[Path] = None,
                          audio_path: Optional[Path] = None,
                          thumbnail_path: Optional[Path] = None) -> str:
        """Create a complete SVG project file with embedded media."""
        
        # Create SVG root element
        svg = ET.Element('svg')
        svg.set('xmlns', self.namespace['svg'])
        svg.set('xmlns:xlink', self.namespace['xlink'])
        svg.set('xmlns:ytlite', self.namespace['ytlite'])
        svg.set('viewBox', '0 0 1920 1080')
        svg.set('width', '100%')
        svg.set('height', '100%')
        
        # Add metadata
        self._add_metadata(svg, project_name, metadata)
        
        # Add embedded media
        media_data = {}
        if video_path and video_path.exists():
            media_data['video'] = self._create_data_uri(video_path)
        if audio_path and audio_path.exists():
            media_data['audio'] = self._create_data_uri(audio_path)
        if thumbnail_path and thumbnail_path.exists():
            media_data['thumbnail'] = self._create_data_uri(thumbnail_path)
        
        # Add visual elements
        self._add_visual_elements(svg, media_data, metadata)
        
        # Add interactive player
        self._add_interactive_player(svg, media_data)
        
        # Convert to string
        return self._svg_to_string(svg)
    
    def _add_metadata(self, svg: ET.Element, project_name: str, metadata: Dict[str, Any]):
        """Add project metadata to SVG."""
        meta_group = ET.SubElement(svg, 'g')
        meta_group.set('id', 'ytlite-metadata')
        meta_group.set('display', 'none')
        
        # Project info
        project_info = {
            'name': project_name,
            'created': datetime.now().isoformat(),
            'version': '1.0',
            **metadata
        }
        
        meta_text = ET.SubElement(meta_group, 'text')
        meta_text.set('id', 'project-metadata')
        meta_text.text = json.dumps(project_info, indent=2)
    
    def _create_data_uri(self, file_path: Path) -> str:
        """Convert file to data URI."""
        mime_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        b64_data = base64.b64encode(file_data).decode('utf-8')
        return f"data:{mime_type};base64,{b64_data}"
    
    def _add_visual_elements(self, svg: ET.Element, media_data: Dict[str, str], metadata: Dict[str, Any]):
        """Add visual elements including thumbnail."""
        
        # Background
        bg_rect = ET.SubElement(svg, 'rect')
        bg_rect.set('width', '100%')
        bg_rect.set('height', '100%')
        bg_rect.set('fill', '#1a1a1a')
        
        # Thumbnail as background image if available
        if 'thumbnail' in media_data:
            thumbnail_image = ET.SubElement(svg, 'image')
            thumbnail_image.set('href', media_data['thumbnail'])
            thumbnail_image.set('width', '100%')
            thumbnail_image.set('height', '100%')
            thumbnail_image.set('preserveAspectRatio', 'xMidYMid slice')
        
        # Title overlay
        title_text = ET.SubElement(svg, 'text')
        title_text.set('x', '50%')
        title_text.set('y', '10%')
        title_text.set('text-anchor', 'middle')
        title_text.set('fill', 'white')
        title_text.set('font-size', '48')
        title_text.set('font-family', 'Arial, sans-serif')
        title_text.text = metadata.get('title', 'YTLite Project')
        
        # Play button overlay
        if 'video' in media_data:
            play_button = ET.SubElement(svg, 'circle')
            play_button.set('cx', '50%')
            play_button.set('cy', '50%')
            play_button.set('r', '60')
            play_button.set('fill', 'rgba(255,255,255,0.8)')
            play_button.set('cursor', 'pointer')
            play_button.set('onclick', 'playVideo()')
            
            play_icon = ET.SubElement(svg, 'polygon')
            play_icon.set('points', '940,520 980,540 940,560')
            play_icon.set('fill', '#333')
            play_icon.set('cursor', 'pointer')
            play_icon.set('onclick', 'playVideo()')
    
    def _add_interactive_player(self, svg: ET.Element, media_data: Dict[str, str]):
        """Add interactive video player with controls."""
        
        if 'video' not in media_data:
            return
        
        # Video player group (hidden by default)
        player_group = ET.SubElement(svg, 'g')
        player_group.set('id', 'video-player')
        player_group.set('style', 'display:none')
        
        # Video element
        video_elem = ET.SubElement(player_group, 'foreignObject')
        video_elem.set('width', '100%')
        video_elem.set('height', '100%')
        
        # HTML video player
        video_html = f'''
        <video id="ytlite-video" width="100%" height="100%" autoplay="true" controls="true" xmlns="http://www.w3.org/1999/xhtml">
            <source src="{media_data['video']}" type="video/mp4"/>
            Your browser does not support the video tag.
        </video>
        '''
        
        video_elem.text = video_html
        
        # Close button
        close_btn = ET.SubElement(player_group, 'circle')
        close_btn.set('cx', '95%')
        close_btn.set('cy', '5%')
        close_btn.set('r', '30')
        close_btn.set('fill', 'rgba(0,0,0,0.7)')
        close_btn.set('cursor', 'pointer')
        close_btn.set('onclick', 'closeVideo()')
        
        close_x = ET.SubElement(player_group, 'text')
        close_x.set('x', '95%')
        close_x.set('y', '5%')
        close_x.set('text-anchor', 'middle')
        close_x.set('dominant-baseline', 'middle')
        close_x.set('fill', 'white')
        close_x.set('font-size', '24')
        close_x.set('cursor', 'pointer')
        close_x.set('onclick', 'closeVideo()')
        close_x.text = '✕'
        
        # JavaScript for player control
        script = ET.SubElement(svg, 'script')
        script.set('type', 'text/javascript')
        script.text = '''
        function playVideo() {
            document.getElementById('video-player').style.display = 'block';
            const video = document.getElementById('ytlite-video');
            if (video) video.play();
        }
        
        function closeVideo() {
            document.getElementById('video-player').style.display = 'none';
            const video = document.getElementById('ytlite-video');
            if (video) video.pause();
        }
        
        // Show metadata in console for debugging
        function showMetadata() {
            const metaElement = document.getElementById('project-metadata');
            if (metaElement) {
                console.log('Project Metadata:', JSON.parse(metaElement.textContent));
            }
        }
        
        // Auto-show metadata on load
        document.addEventListener('DOMContentLoaded', showMetadata);
        
        // Auto-play video when SVG is loaded
        window.onload = function() {
            var video = document.getElementById('ytlite-video');
            if (video) {
                video.play();
            }
        };
        '''
    
    def _svg_to_string(self, svg: ET.Element) -> str:
        """Convert SVG element to formatted string."""
        # Register namespaces
        ET.register_namespace('', self.namespace['svg'])
        ET.register_namespace('xlink', self.namespace['xlink'])
        ET.register_namespace('ytlite', self.namespace['ytlite'])
        
        # Convert to string
        rough_string = ET.tostring(svg, encoding='unicode')
        
        # Add XML declaration and DOCTYPE
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
{rough_string}'''
        
        return svg_content
    
    def extract_metadata(self, svg_path: Path) -> Dict[str, Any]:
        """Extract metadata from SVG file."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Find metadata element
            meta_elem = root.find('.//text[@id="project-metadata"]')
            if meta_elem is not None and meta_elem.text:
                return json.loads(meta_elem.text)
            
            return {}
        except Exception as e:
            logger.error(f"Failed to extract metadata from {svg_path}: {e}")
            return {}
    
    def update_metadata(self, svg_path: Path, new_metadata: Dict[str, Any]) -> bool:
        """Update metadata in existing SVG file."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Find and update metadata
            meta_elem = root.find('.//text[@id="project-metadata"]')
            if meta_elem is not None:
                # Merge with existing metadata
                existing_meta = {}
                if meta_elem.text:
                    existing_meta = json.loads(meta_elem.text)
                
                existing_meta.update(new_metadata)
                existing_meta['modified'] = datetime.now().isoformat()
                
                meta_elem.text = json.dumps(existing_meta, indent=2)
                
                # Save back to file
                tree.write(svg_path, encoding='utf-8', xml_declaration=True)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to update metadata in {svg_path}: {e}")
            return False



if __name__ == "__main__":
    # Test the SVG DataURI packager
    test_metadata = {
        'title': 'Test Project',
        'description': 'A test SVG project with embedded media',
        'author': 'YTLite',
        'theme': 'dark'
    }
    
    # This would normally be called with real paths
    print("SVG DataURI Packager initialized")
