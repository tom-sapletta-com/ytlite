#!/usr/bin/env python3
"""
YTLite Audio Generator Module
Handles TTS and audio generation
"""

import asyncio
import edge_tts
from pathlib import Path
from rich.console import Console

console = Console()

class AudioGenerator:
    def __init__(self, config):
        self.config = config
        self.voice = config.get("voice", "pl-PL-MarekNeural")
        
    async def generate_audio_async(self, text: str, output_path: str):
        """Generate audio from text using edge-tts"""
        console.print(f"[cyan]Generating audio with voice: {self.voice}...[/]")
        
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        
        console.print(f"[green]✓ Audio saved: {output_path}[/]")
        
    def generate_audio(self, text: str, output_path: str):
        """Synchronous wrapper for audio generation"""
        asyncio.run(self.generate_audio_async(text, output_path))
        return output_path
    
    def combine_text_for_audio(self, paragraphs: list) -> str:
        """Combine paragraphs for audio generation"""
        # Add pauses between paragraphs
        return " ... ".join(paragraphs)
