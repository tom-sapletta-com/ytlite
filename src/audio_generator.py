#!/usr/bin/env python3
"""
YTLite Audio Generator Module
Handles TTS and audio generation
"""

import os
import asyncio
import subprocess
import edge_tts
import imageio_ffmpeg
from pathlib import Path
from rich.console import Console
from logging_setup import get_logger

console = Console()
logger = get_logger("audio")

class AudioGenerator:
    def __init__(self, config):
        self.config = config
        self.voice = config.get("voice", "pl-PL-MarekNeural")
        
    async def generate_audio_async(self, text: str, output_path: str):
        """Generate audio from text using edge-tts"""
        console.print(f"[cyan]Generating audio with voice: {self.voice}...[/]")
        logger.info("Generating audio via edge-tts", extra={"voice": self.voice, "output": output_path})
        
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        
        console.print(f"[green]✓ Audio saved: {output_path}[/]")
        logger.info("Audio saved", extra={"output": output_path})
        
    def generate_audio(self, text: str, output_path: str):
        """Synchronous wrapper for audio generation.
        If YTLITE_FAST_TEST=1, generate a 1s silent MP3 using bundled ffmpeg for fast E2E tests.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        if os.getenv("YTLITE_FAST_TEST") == "1":
            try:
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                logger.info("FAST_TEST enabled: generating silent MP3 via ffmpeg", extra={"ffmpeg": ffmpeg, "output": output_path})
                cmd = [
                    ffmpeg, "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "1",
                    "-q:a", "9",
                    output_path,
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                console.print(f"[green]✓ (FAST_TEST) Audio saved: {output_path}[/]")
                return output_path
            except Exception as e:
                logger.warning("FAST_TEST ffmpeg generation failed, falling back to edge-tts", extra={"error": str(e)})
                # fall through to normal path
        asyncio.run(self.generate_audio_async(text, output_path))
        return output_path
    
    def combine_text_for_audio(self, paragraphs: list) -> str:
        """Combine paragraphs for audio generation"""
        # Add pauses between paragraphs
        return " ... ".join(paragraphs)
