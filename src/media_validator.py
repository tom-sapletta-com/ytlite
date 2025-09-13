#!/usr/bin/env python3
"""
Media validation utilities: detect whether audio tracks contain sound or are silent.
- Works for WAV/MP3 files and MP4 videos (checks audio stream and its loudness)
- Uses ffmpeg (volumedetect) when available; falls back to MoviePy sampling.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import shlex
import os
import math

from logging_setup import get_logger

logger = get_logger("media_validator")

# Try to locate ffmpeg/ffprobe
_FFMPEG_BIN: Optional[str] = os.getenv("IMAGEIO_FFMPEG_EXE")
if not _FFMPEG_BIN:
    try:
        import imageio_ffmpeg
        _FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        _FFMPEG_BIN = None


def _run_ffmpeg(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


def _parse_mean_volume(ffmpeg_stderr: str) -> Optional[float]:
    """Parse mean_volume from ffmpeg volumedetect output. Returns dB value or None."""
    mv = None
    for line in ffmpeg_stderr.splitlines():
        line = line.strip()
        if line.startswith("mean_volume:"):
            # format: mean_volume: -23.0 dB
            try:
                parts = line.split()
                mv = float(parts[1])
                break
            except Exception:
                continue
    return mv


def check_audio_silence(audio_path: Path, silence_threshold_db: float = -50.0) -> Dict[str, Any]:
    """Check if an audio file (wav/mp3) is silent.
    Returns dict with keys: exists, mean_db, silent, method, error(optional)
    """
    # ENV override
    try:
        silence_threshold_db = float(os.getenv("MEDIA_SILENCE_DB", str(silence_threshold_db)))
    except Exception:
        pass
    res: Dict[str, Any] = {"file": str(audio_path), "exists": audio_path.exists(), "silent": True, "method": None}
    if not audio_path.exists():
        res["error"] = "audio_not_found"
        return res

    # Prefer ffmpeg volumedetect
    if _FFMPEG_BIN:
        cmd = [_FFMPEG_BIN, "-hide_banner", "-loglevel", "info", "-i", str(audio_path), "-af", "volumedetect", "-f", "null", "-"]
        code, out, err = _run_ffmpeg(cmd)
        mv = _parse_mean_volume(err)
        res["method"] = "ffmpeg_volumedetect"
        res["mean_db"] = mv
        if mv is not None:
            res["silent"] = (mv < silence_threshold_db) or math.isinf(mv)
            return res
        # fallthrough to moviepy if parsing failed

    # Fallback: sample via moviepy
    try:
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        clip = AudioFileClip(str(audio_path))
        duration = max(0.1, float(clip.duration or 0.1))
        # Sample 3 windows evenly across the file (up to 3 seconds total at 8kHz)
        sample_points = [duration * 0.1, duration * 0.5, max(0.0, duration - 0.1)]
        vals = []
        for t in sample_points:
            try:
                arr = clip.to_soundarray(fps=8000, buffersize=8000, nbytes=2)
                # Compute RMS
                import numpy as np
                if arr.size == 0:
                    continue
                # Take a slice for robustness
                s = arr[: min(len(arr), 8000)]
                rms = float(np.sqrt(np.mean(np.square(s), dtype=np.float64)))
                # Convert to dBFS-like scale assuming peak=1.0
                db = 20.0 * math.log10(max(rms, 1e-8))
                vals.append(db)
            except Exception:
                continue
        clip.close()
        if vals:
            mean_db = float(sum(vals) / len(vals))
            res["method"] = "moviepy_sample"
            res["mean_db"] = mean_db
            res["silent"] = mean_db < silence_threshold_db
            return res
        else:
            res["method"] = "moviepy_sample"
            res["error"] = "no_samples"
            res["silent"] = True
            return res
    except Exception as e:
        res["method"] = "error"
        res["error"] = str(e)
        res["silent"] = True
        return res


def check_video_audio_silence(video_path: Path, silence_threshold_db: float = -50.0) -> Dict[str, Any]:
    """Check if an MP4 video has an audio stream and whether it is silent.
    Returns dict with keys: exists, has_audio, mean_db(optional), silent, method, error(optional)
    """
    # ENV override
    try:
        silence_threshold_db = float(os.getenv("MEDIA_SILENCE_DB", str(silence_threshold_db)))
    except Exception:
        pass
    res: Dict[str, Any] = {"file": str(video_path), "exists": video_path.exists(), "has_audio": False, "silent": True, "method": None}
    if not video_path.exists():
        res["error"] = "video_not_found"
        return res

    # Try ffmpeg volumedetect directly on video
    if _FFMPEG_BIN:
        cmd = [_FFMPEG_BIN, "-hide_banner", "-loglevel", "info", "-i", str(video_path), "-af", "volumedetect", "-f", "null", "-"]
        code, out, err = _run_ffmpeg(cmd)
        mv = _parse_mean_volume(err)
        res["method"] = "ffmpeg_volumedetect"
        if "Stream #" in err and "Audio" in err:
            res["has_audio"] = True
        if mv is not None:
            res["mean_db"] = mv
            res["silent"] = (mv < silence_threshold_db) or math.isinf(mv)
            return res
        # fallthrough to moviepy

    # Fallback: MoviePy
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        clip = VideoFileClip(str(video_path))
        res["has_audio"] = clip.audio is not None
        if clip.audio is None:
            res["method"] = "moviepy_meta"
            res["silent"] = True
            try:
                clip.close()
            except Exception:
                pass
            return res
        # Sample audio
        duration = max(0.1, float(clip.duration or 0.1))
        sample_points = [duration * 0.1, duration * 0.5, max(0.0, duration - 0.1)]
        vals = []
        try:
            import numpy as np
        except Exception:
            np = None
        for t in sample_points:
            try:
                arr = clip.audio.to_soundarray(fps=8000, buffersize=8000, nbytes=2)
                if arr.size == 0:
                    continue
                s = arr[: min(len(arr), 8000)]
                if np is not None:
                    rms = float((np.sqrt(np.mean(np.square(s), dtype=np.float64))))
                else:
                    # simple fallback without numpy
                    import math as _m
                    rms = float(_m.sqrt(sum(float(x)**2 for x in s.flatten()) / s.size))
                db = 20.0 * math.log10(max(rms, 1e-8))
                vals.append(db)
            except Exception:
                continue
        try:
            clip.close()
        except Exception:
            pass
        if vals:
            mean_db = float(sum(vals) / len(vals))
            res["method"] = "moviepy_sample"
            res["mean_db"] = mean_db
            res["silent"] = mean_db < silence_threshold_db
            return res
        else:
            res["method"] = "moviepy_sample"
            res["error"] = "no_samples"
            res["silent"] = True
            return res
    except Exception as e:
        res["method"] = "error"
        res["error"] = str(e)
        res["silent"] = True
        return res
