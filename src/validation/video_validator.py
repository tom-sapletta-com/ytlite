#!/usr/bin/env python3
"""
Video Validation Module for YTLite
Handles video validation using Whisper STT and video analysis
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from datetime import datetime
import logging

console = Console()
logger = logging.getLogger(__name__)

try:
    import whisper
except ImportError:
    console.print("[yellow]Whisper not installed. Installing...[/]")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    import whisper

try:
    # MoviePy 1.x path
    from moviepy.editor import VideoFileClip
except Exception as e:
    try:
        # MoviePy 2.x path
        from moviepy import VideoFileClip
    except Exception as inner_e:
        console.print(f"[yellow]MoviePy not found. Installing...[/]")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy==1.0.3"])
            from moviepy.editor import VideoFileClip
        except Exception as install_e:
            console.print(f"[bold red]MoviePy import failed after install: {install_e}[/]")
            logger.error(f"MoviePy import failed after install", extra={"error": str(install_e)})
            raise Exception(f"Failed to import MoviePy: {e} (inner error: {inner_e})")


class VideoValidator:
    def __init__(self):
        self.whisper_model = None
        self.results = {}
        
    def _load_whisper_model(self, model_size="base"):
        """Load Whisper model for STT"""
        if self.whisper_model is None:
            console.print(f"[cyan]Loading Whisper model ({model_size})...[/]")
            self.whisper_model = whisper.load_model(model_size)
        return self.whisper_model
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file using ffmpeg."""
        try:
            temp_audio_path = "/tmp/extracted_audio_{}.wav".format(os.path.basename(video_path).replace(".mp4", ""))
            
            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ac", "1", "-ar", "16000", 
                "-f", "wav", temp_audio_path
            ]
            
            result = subprocess.run(cmd, 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=120)
            
            if result.returncode != 0:
                console.print(f"[red]ffmpeg failed: {result.stderr}[/]")
                return None
                
            if not os.path.exists(temp_audio_path):
                console.print(f"[red]Audio extraction failed - output file not created[/]")
                return None
                
            console.print(f"[green]Audio extracted to {temp_audio_path}[/]")
            return temp_audio_path
            
        except subprocess.TimeoutExpired:
            console.print(f"[red]Audio extraction timed out for {video_path}[/]")
            return None
        except Exception as e:
            console.print(f"[red]Error extracting audio: {e}[/]")
            print(f"Error extracting audio from video {video_path}. Exception: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio using Whisper STT"""
        model = self._load_whisper_model()
        console.print(f"[cyan]Transcribing {audio_path}...[/]")
        
        result = model.transcribe(audio_path)
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
        }
    
    def analyze_video_properties(self, video_path: str) -> Dict:
        """Analyze video properties"""
        video = VideoFileClip(video_path)
        
        properties = {
            "duration": video.duration,
            "fps": video.fps,
            "size": video.size,
            "has_audio": video.audio is not None,
            "aspect_ratio": video.size[0] / video.size[1] if video.size[1] != 0 else 0
        }
        
        video.close()
        return properties
    
    def extract_frames_info(self, video_path: str, num_samples: int = 5) -> List[Dict]:
        """Extract sample frames for analysis"""
        video = VideoFileClip(video_path)
        duration = video.duration
        
        frames_info = []
        for i in range(num_samples):
            timestamp = (duration / num_samples) * i
            try:
                frame = video.get_frame(timestamp)
                frames_info.append({
                    "timestamp": timestamp,
                    "shape": frame.shape,
                    "mean_brightness": frame.mean()
                })
            except Exception as e:
                console.print(f"[yellow]Could not extract frame at {timestamp}s: {e}[/]")
        
        video.close()
        return frames_info
    
    def validate_video(self, video_path: str, expected_content: Optional[str] = None, detailed: bool = False) -> Dict:
        """Complete video validation"""
        console.print(f"[bold cyan]Validating {video_path}[/]")
        
        if not os.path.exists(video_path):
            return {
                "video_path": video_path,
                "status": "failed",
                "error": "Video file not found",
                "timestamp": datetime.now().isoformat()
            }
        
        result = {
            "video_path": video_path,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown"
        }
        
        try:
            # Analyze video properties
            properties = self.analyze_video_properties(video_path)
            result["properties"] = properties
            
            # Extract and transcribe audio
            audio_path = self.extract_audio_from_video(video_path)
            if audio_path:
                transcription = self.transcribe_audio(audio_path)
                result["transcription"] = transcription
                
                # Clean up temp audio file
                try:
                    os.remove(audio_path)
                except:
                    pass
            else:
                result["transcription"] = {"error": "Failed to extract audio"}
            
            # Extract frames info if detailed
            if detailed:
                frames = self.extract_frames_info(video_path)
                result["frames"] = frames
            else:
                result["frames"] = []
            
            # Check content match if expected content provided
            if expected_content and "transcription" in result and "text" in result["transcription"]:
                content_match = self._check_content_match(
                    result["transcription"]["text"],
                    expected_content
                )
                result["content_match"] = content_match
            
            # Calculate quality score
            quality = self._calculate_quality_score(
                result["properties"],
                result.get("transcription", {}),
                result.get("frames", [])
            )
            result["quality"] = quality
            
            # Overall status
            if result["properties"]["has_audio"] and "text" in result.get("transcription", {}):
                if len(result["transcription"]["text"].strip()) > 10:
                    result["status"] = "passed"
                else:
                    result["status"] = "warning - short transcription"
            else:
                result["status"] = "failed - no audio or transcription"
                
        except Exception as e:
            console.print(f"[red]Validation failed: {e}[/]")
            result.update({
                "status": "error",
                "error": str(e),
                "path": video_path
            })
    
        return result
    
    def _check_content_match(self, transcribed_text: str, expected_content: str) -> Dict:
        """Check if transcribed content matches expected"""
        import difflib
        
        # Clean and normalize text
        transcribed_clean = transcribed_text.lower().strip()
        expected_clean = expected_content.lower().strip()
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, transcribed_clean, expected_clean).ratio()
        
        return {
            "similarity": similarity,
            "transcribed_length": len(transcribed_clean),
            "expected_length": len(expected_clean),
            "match_quality": "excellent" if similarity > 0.8 else 
                           "good" if similarity > 0.6 else 
                           "fair" if similarity > 0.4 else 
                           "poor" if similarity > 0.3 else "failed"
        }
    
    def _calculate_quality_score(self, properties: Dict, transcription: Dict, frames: List[Dict]) -> Dict:
        """Calculate overall quality score"""
        scores = {}
        
        # Audio quality score
        if properties.get("has_audio"):
            if "text" in transcription and len(transcription["text"].strip()) > 10:
                scores["audio"] = 0.8
            elif "error" in transcription:
                scores["audio"] = 0.0
            else:
                scores["audio"] = 0.3
        else:
            scores["audio"] = 0.0
        
        # Video quality score
        if properties.get("duration", 0) > 5:
            scores["duration"] = 0.8
        elif properties.get("duration", 0) > 1:
            scores["duration"] = 0.5
        else:
            scores["duration"] = 0.2
        
        # Frame quality (if available)
        if frames:
            avg_brightness = sum(f.get("mean_brightness", 0) for f in frames) / len(frames)
            if 50 < avg_brightness < 200:  # Good brightness range
                scores["video"] = 0.8
            else:
                scores["video"] = 0.5
        else:
            scores["video"] = 0.6  # Default if no frame analysis
        
        # Overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        
        return {
            "scores": scores,
            "overall": overall_score,
            "grade": "A" if overall_score > 0.8 else 
                    "B" if overall_score > 0.6 else 
                    "C" if overall_score > 0.4 else "F"
        }


def validate_all_videos(video_dir: str = "output/videos", content_dir: str = "content/episodes", detailed: bool = False):
    """Validate all videos in directory"""
    validator = VideoValidator()
    video_path = Path(video_dir)
    
    if not video_path.exists():
        console.print(f"[red]Video directory {video_dir} not found[/]")
        return {}
    
    results = []
    video_files = list(video_path.glob("*.mp4"))
    
    if not video_files:
        console.print(f"[yellow]No MP4 files found in {video_dir}[/]")
        return {}
    
    for video_file in video_files:
        # Try to find corresponding content file
        expected_content = None
        content_file = Path(content_dir) / f"{video_file.stem}.md"
        if content_file.exists():
            try:
                expected_content = content_file.read_text()
            except Exception as e:
                console.print(f"[yellow]Could not read content file {content_file}: {e}[/]")
        
        # Validate video
        result = validator.validate_video(str(video_file), expected_content, detailed)
        results.append(result)
    
    # Generate report
    report = validator.generate_report(results, detailed=detailed)
    return report
