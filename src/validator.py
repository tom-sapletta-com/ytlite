#!/usr/bin/env python3
"""
YTLite Video Validator Module
Tests generated videos using STT and video analysis
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
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
except Exception:
    try:
        # MoviePy 2.x path
        from moviepy import VideoFileClip
    except Exception as e:
        console.print("[yellow]MoviePy not found. Installing...[/]")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
            from moviepy import VideoFileClip
        except Exception as inner_e:
            console.print(f"[bold red]MoviePy import failed after install: {inner_e}[/]")
            raise

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
        """Extract audio from video for STT analysis"""
        video = VideoFileClip(video_path)
        audio_path = f"/tmp/extracted_audio_{Path(video_path).stem}.wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
        return audio_path
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio using Whisper STT"""
        model = self._load_whisper_model()
        console.print(f"[cyan]Transcribing {audio_path}...[/]")
        
        result = model.transcribe(audio_path)
        
        return {
            "text": result["text"],
            "language": result["language"],
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
            "aspect_ratio": video.w / video.h if video.h > 0 else 0,
            "has_audio": video.audio is not None,
            "file_size": os.path.getsize(video_path)
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
            frame = video.get_frame(timestamp)
            
            frames_info.append({
                "timestamp": timestamp,
                "shape": frame.shape,
                "mean_brightness": float(frame.mean()),
                "has_content": frame.std() > 10  # Simple content detection
            })
        
        video.close()
        return frames_info
    
    def validate_video(self, video_path: str, expected_content: Optional[str] = None, detailed: bool = False) -> Dict:
        """Complete video validation"""
        console.print(f"[bold cyan]Validating {video_path}[/]")
        
        if not os.path.exists(video_path):
            return {
                "status": "error",
                "message": "Video file not found",
                "path": video_path
            }
        
        try:
            # Analyze video properties
            properties = self.analyze_video_properties(video_path)
            
            # Extract and transcribe audio
            audio_path = self.extract_audio_from_video(video_path)
            transcription = self.transcribe_audio(audio_path)
            
            # Analyze frames
            frames = self.extract_frames_info(video_path)
            
            # Content validation
            content_match = None
            if expected_content:
                content_match = self._check_content_match(
                    transcription["text"], 
                    expected_content
                )
            
            result = {
                "status": "success",
                "path": video_path,
                "timestamp": datetime.now().isoformat(),
                "properties": properties,
                "transcription": transcription,
                "frames": frames,
                "content_match": content_match,
                "quality_score": self._calculate_quality_score(properties, transcription, frames)
            }
            
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            if detailed:
                logger.info(f"Validated video: {video_path}", extra={"status": "Valid", "duration": properties["duration"]})
            return result
            
        except Exception as e:
            if detailed:
                logger.error(f"Error validating video {video_path}: {e}", extra={"error": str(e)})
            else:
                logger.error(f"Error validating video {video_path}", extra={"error": str(e)})
            return {
                "status": "error",
                "message": str(e),
                "path": video_path
            }
    
    def _check_content_match(self, transcribed_text: str, expected_content: str) -> Dict:
        """Check if transcribed content matches expected"""
        import difflib
        
        similarity = difflib.SequenceMatcher(
            None, 
            transcribed_text.lower().strip(), 
            expected_content.lower().strip()
        ).ratio()
        
        return {
            "similarity": similarity,
            "transcribed": transcribed_text,
            "expected": expected_content,
            "match_quality": "excellent" if similarity > 0.8 else 
                           "good" if similarity > 0.6 else
                           "poor" if similarity > 0.3 else "failed"
        }
    
    def _calculate_quality_score(self, properties: Dict, transcription: Dict, frames: List[Dict]) -> Dict:
        """Calculate overall quality score"""
        scores = {}
        
        # Duration score (prefer 30s - 10min videos)
        duration = properties["duration"]
        if 30 <= duration <= 600:
            scores["duration"] = 1.0
        elif duration < 30:
            scores["duration"] = max(0.5, duration / 30)
        else:
            scores["duration"] = max(0.5, 600 / duration)
        
        # Audio quality (based on transcription confidence)
        audio_segments = len(transcription.get("segments", []))
        scores["audio"] = min(1.0, audio_segments / 10) if audio_segments > 0 else 0.0
        
        # Visual quality (based on frame analysis)
        content_frames = sum(1 for f in frames if f["has_content"])
        scores["visual"] = content_frames / len(frames) if frames else 0.0
        
        # Technical quality
        scores["technical"] = 1.0 if properties["has_audio"] else 0.5
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "overall": overall_score,
            "breakdown": scores,
            "grade": "A" if overall_score > 0.8 else
                    "B" if overall_score > 0.6 else
                    "C" if overall_score > 0.4 else "F"
        }
    
    def generate_report(self, results: List[Dict], output_path: str = "output/validation_report.json", detailed: bool = False):
        """Generate comprehensive validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_videos": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
                "average_quality": sum(r.get("quality_score", {}).get("overall", 0) 
                                     for r in results if r["status"] == "success") / 
                                   max(1, len([r for r in results if r["status"] == "success"]))
            },
            "results": results
        }
        
        # Save JSON report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[green]✓ Report saved to {output_path}[/]")
        
        if detailed:
            logger.info("Detailed validation report saved", extra={"report_path": output_path, "results": results})
        else:
            logger.info("Validation report saved", extra={"report_path": output_path})
        
        # Display summary table
        self._display_summary_table(report)
        
        return report
    
    def _display_summary_table(self, report: Dict):
        """Display validation results in a table"""
        table = Table(title="Video Validation Report")
        
        table.add_column("Video", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Quality", style="magenta")
        table.add_column("Audio Match", style="blue")
        
        for result in report["results"]:
            if result["status"] == "success":
                name = Path(result["path"]).stem
                status = "✓ OK"
                duration = f"{result['properties']['duration']:.1f}s"
                quality = result["quality_score"]["grade"]
                audio_match = result.get("content_match", {}).get("match_quality", "N/A")
            else:
                name = Path(result["path"]).stem
                status = "✗ Error"
                duration = "N/A"
                quality = "F"
                audio_match = "N/A"
            
            table.add_row(name, status, duration, quality, audio_match)
        
        console.print(table)

class Validator:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.reports_dir = os.path.join(project_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def validate_app(self):
        """Validate the application setup and dependencies."""
        results = []
        try:
            # Check for required dependencies
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
            installed_packages = result.stdout
            required_packages = ['requests', 'wordpress-xmlrpc', 'python-dotenv', 'webdavclient3']
            for pkg in required_packages:
                if pkg in installed_packages:
                    results.append({'check': f"{pkg} installed", 'status': 'PASS'})
                else:
                    results.append({'check': f"{pkg} installed", 'status': 'FAIL', 'message': f"{pkg} is not installed."})

            # Check for Tauri app build
            tauri_build_result = subprocess.run(['cargo', 'build'], cwd=os.path.join(self.project_dir, 'tauri-youtube-oauth', 'src-tauri'), capture_output=True, text=True)
            if tauri_build_result.returncode == 0:
                results.append({'check': 'Tauri app build', 'status': 'PASS'})
            else:
                results.append({'check': 'Tauri app build', 'status': 'FAIL', 'message': tauri_build_result.stderr})

            # Check for frontend build
            frontend_build_result = subprocess.run(['npm', 'run', 'build:frontend'], cwd=os.path.join(self.project_dir, 'tauri-youtube-oauth'), capture_output=True, text=True)
            if frontend_build_result.returncode == 0:
                results.append({'check': 'Frontend build', 'status': 'PASS'})
            else:
                results.append({'check': 'Frontend build', 'status': 'FAIL', 'message': frontend_build_result.stderr})

        except Exception as e:
            results.append({'check': 'App validation', 'status': 'ERROR', 'message': str(e)})

        report = {
            'validation_type': 'app',
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        report_path = os.path.join(self.reports_dir, f'app_validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        summary = self.summarize_report(report)
        return summary, report_path

    def validate_data(self, content_path, detailed: bool = False):
        """Validate the data integrity for content files."""
        results = []
        try:
            # Check if content path exists
            if not os.path.exists(content_path):
                results.append({'check': 'Content path existence', 'status': 'FAIL', 'message': f"Content path {content_path} does not exist."})
            else:
                results.append({'check': 'Content path existence', 'status': 'PASS'})

                # Check for markdown files
                md_files = [f for f in os.listdir(content_path) if f.endswith('.md')]
                if not md_files:
                    results.append({'check': 'Markdown files presence', 'status': 'FAIL', 'message': "No markdown files found in content path."})
                else:
                    results.append({'check': 'Markdown files presence', 'status': 'PASS', 'message': f"Found {len(md_files)} markdown files."})

                    # Validate content of each markdown file
                    for md_file in md_files:
                        with open(os.path.join(content_path, md_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            if not content.strip():
                                results.append({'check': f"Content validation for {md_file}", 'status': 'FAIL', 'message': f"{md_file} is empty."})
                            else:
                                results.append({'check': f"Content validation for {md_file}", 'status': 'PASS'})

        except Exception as e:
            results.append({'check': 'Data validation', 'status': 'ERROR', 'message': str(e)})

        report = {
            'validation_type': 'data',
            'timestamp': datetime.now().isoformat(),
            'content_path': content_path,
            'results': results
        }
        report_path = os.path.join(self.reports_dir, f'data_validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        if detailed:
            logger.info("Detailed data validation report saved", extra={"report_path": report_path, "results": results})
        else:
            logger.info("Data validation report saved", extra={"report_path": report_path})

        summary = self.summarize_report(report)
        return summary, report_path

    def summarize_report(self, report):
        """Summarize the validation report into a concise format."""
        summary = f"Validation Type: {report['validation_type'].capitalize()}\nTimestamp: {report['timestamp']}\n"
        pass_count = sum(1 for r in report['results'] if r['status'] == 'PASS')
        fail_count = sum(1 for r in report['results'] if r['status'] == 'FAIL')
        error_count = sum(1 for r in report['results'] if r['status'] == 'ERROR')
        summary += f"Results: {pass_count} Passed, {fail_count} Failed, {error_count} Errors\n"
        for result in report['results']:
            if result['status'] != 'PASS':
                summary += f"- {result['check']}: {result['status']}"
                if 'message' in result:
                    summary += f" ({result['message'][:100]}...)"
                summary += "\n"
        return summary

def validate_all_videos(video_dir: str = "output/videos", content_dir: str = "content/episodes", detailed: bool = False):
    """Validate all videos in directory"""
    validator = VideoValidator()
    video_path = Path(video_dir)
    content_path = Path(content_dir)
    
    if not video_path.exists():
        console.print(f"[red]Video directory {video_dir} not found[/]")
        return
    
    video_files = list(video_path.glob("*.mp4"))
    if not video_files:
        console.print(f"[yellow]No MP4 files found in {video_dir}[/]")
        return
    
    results = []
    for video_file in video_files:
        # Try to find corresponding markdown file
        md_file = content_path / f"{video_file.stem}.md"
        expected_content = None
        
        if md_file.exists():
            try:
                with open(md_file, 'r') as f:
                    import frontmatter
                    post = frontmatter.load(f)
                    expected_content = post.content.strip()
            except:
                pass
        
        result = validator.validate_video(str(video_file), expected_content, detailed)
        results.append(result)
    
    # Generate report
    report = validator.generate_report(results, detailed=detailed)
    return report

def main():
    validator = Validator('/home/tom/github/tom-sapletta-com/ytlite')
    app_summary, app_report_path = validator.validate_app()
    print("App Validation Summary:\n", app_summary)
    print(f"Full report at: {app_report_path}\n")

    data_summary, data_report_path = validator.validate_data('/home/tom/github/tom-sapletta-com/ytlite/content/episodes')
    print("Data Validation Summary:\n", data_summary)
    print(f"Full report at: {data_report_path}\n")

if __name__ == "__main__":
    main()
