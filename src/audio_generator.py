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
    def __init__(self, config=None):
        self.config = config or {}
        self.voice = self.config.get("voice", "pl-PL-MarekNeural")
        
    def set_voice(self, voice: str):
        """Update the voice for audio generation"""
        self.voice = voice
        logger.info(f"Voice set to: {self.voice}")
        
    async def generate_audio_async(self, text: str, output_path: str):
        """Generate audio from text using edge-tts"""
        console.print(f"[cyan]Generating audio with voice: {self.voice}...[/]")
        logger.info("Generating audio via edge-tts", extra={"voice": self.voice, "output": output_path})
        
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        
        console.print(f"[green]✓ Audio saved: {output_path}[/]")
        logger.info("Audio saved", extra={"output": output_path})
        
    def generate_audio(self, text: str, output_path: str, voice: str = None):
        """Synchronous wrapper for audio generation.
        If YTLITE_FAST_TEST=1, generate a 1s silent MP3 using bundled ffmpeg for fast E2E tests.
        
        Args:
            text: The text to convert to speech
            output_path: Path to save the generated audio
            voice: Optional voice to use (overrides instance voice)
        """
        # Use the provided voice if specified, otherwise use the instance voice
        current_voice = voice or self.voice
        self.voice = current_voice  # Update instance voice for future calls
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        if os.getenv("YTLITE_FAST_TEST") == "1":
            try:
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                logger.info("FAST_TEST enabled: generating 1s sine tone MP3 via ffmpeg (non-silent)", extra={"ffmpeg": ffmpeg, "output": output_path})
                # Generate a 1kHz sine tone for 1 second so media validator does not flag silence
                cmd = [
                    ffmpeg, "-y",
                    "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=44100:duration=1",
                    "-ac", "1", "-ar", "44100",
                    "-q:a", "4",
                    output_path,
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                console.print(f"[green]✓ (FAST_TEST) Tone audio saved: {output_path}[/]")
                return output_path
            except Exception as e:
                logger.warning("FAST_TEST ffmpeg tone generation failed, falling back to edge-tts", extra={"error": str(e)})
                # fall through to normal path
        asyncio.run(self.generate_audio_async(text, output_path))
        return output_path
    
    def combine_text_for_audio(self, paragraphs: list) -> str:
        """Combine paragraphs for audio generation"""
        # Add pauses between paragraphs
        return " ... ".join(paragraphs)
