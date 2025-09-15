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

# Tunables via environment
def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

MEDIA_SILENCE_DB_DEFAULT = _env_float("MEDIA_SILENCE_DB", -50.0)
MEDIA_SILENCE_MIN_MS_DEFAULT = _env_int("MEDIA_SILENCE_MIN_MS", 800)  # min contiguous silence to consider problematic
MEDIA_SILENCE_FRACTION_DEFAULT = _env_float("MEDIA_SILENCE_FRACTION", 0.8)  # fraction of total duration

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


def _parse_silencedetect(stderr: str) -> list[tuple[float, float]]:
    """Parse ffmpeg silencedetect stderr output.
    Returns list of (start, end) in seconds for each detected silence segment.
    """
    segs: list[tuple[float, float]] = []
    current_start: Optional[float] = None
    for line in stderr.splitlines():
        line = line.strip()
        if line.startswith("silence_start:"):
            try:
                current_start = float(line.split(":", 1)[1].strip())
            except Exception:
                current_start = None
        elif line.startswith("silence_end:"):
            try:
                # format: silence_end: X | silence_duration: Y
                parts = line.split("silence_end:", 1)[1].strip()
                # parts like: '12.345 | silence_duration: 0.800'
                end_str = parts.split("|", 1)[0].strip()
                end = float(end_str)
                if current_start is not None and end > current_start:
                    segs.append((current_start, end))
            except Exception:
                pass
            finally:
                current_start = None
    return segs


def _get_duration_seconds(path: Path, is_video: bool) -> Optional[float]:
    """Get media duration using MoviePy. Returns None on failure."""
    try:
        if is_video:
            from moviepy.video.io.VideoFileClip import VideoFileClip
            clip = VideoFileClip(str(path))
        else:
            from moviepy.audio.io.AudioFileClip import AudioFileClip
            clip = AudioFileClip(str(path))
        try:
            d = float(clip.duration or 0.0)
        finally:
            try:
                clip.close()
            except Exception:
                pass
        return d
    except Exception:
        return None


def _ffmpeg_silence_stats(path: Path, threshold_db: float, min_silence_sec: float, is_video: bool) -> dict:
    """Run ffmpeg silencedetect and compute stats.
    Returns dict with: total_silence (s), longest_silence_ms (ms), fraction (0..1).
    """
    stats = {"total_silence": 0.0, "longest_silence_ms": 0.0, "fraction": 0.0}
    if not _FFMPEG_BIN:
        return stats
    cmd = [
        _FFMPEG_BIN, "-hide_banner", "-nostats",
        "-i", str(path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence_sec}",
        "-f", "null", "-",
    ]
    code, out, err = _run_ffmpeg(cmd)
    segs = _parse_silencedetect(err)
    total_sil = 0.0
    longest = 0.0
    for (s, e) in segs:
        dur = max(0.0, e - s)
        total_sil += dur
        if dur > longest:
            longest = dur
    duration = _get_duration_seconds(path, is_video) or 0.0
    fraction = (total_sil / duration) if duration > 0 else 0.0
    stats.update({
        "total_silence": total_sil,
        "longest_silence_ms": longest * 1000.0,
        "fraction": fraction,
    })
    return stats


def check_audio_silence(audio_path: Path, silence_threshold_db: float = -50.0) -> Dict[str, Any]:
    """Check if an audio file (wav/mp3) is silent.
    Returns dict with keys: exists, mean_db, silent, method, error(optional)
    """
    # ENV override
    try:
        silence_threshold_db = float(os.getenv("MEDIA_SILENCE_DB", str(silence_threshold_db)))
    except Exception:
        pass
    min_ms = _env_int("MEDIA_SILENCE_MIN_MS", MEDIA_SILENCE_MIN_MS_DEFAULT)
    frac_needed = _env_float("MEDIA_SILENCE_FRACTION", MEDIA_SILENCE_FRACTION_DEFAULT)
    res: Dict[str, Any] = {"file": str(audio_path), "exists": audio_path.exists(), "silent": True, "method": None}
    if not audio_path.exists():
        res["error"] = "audio_not_found"
        return res

    # Prefer ffmpeg volumedetect + silencedetect
    if _FFMPEG_BIN:
        cmd = [_FFMPEG_BIN, "-hide_banner", "-loglevel", "info", "-i", str(audio_path), "-af", "volumedetect", "-f", "null", "-"]
        code, out, err = _run_ffmpeg(cmd)
        mv = _parse_mean_volume(err)
        stats = _ffmpeg_silence_stats(audio_path, silence_threshold_db, max(0.001, min_ms / 1000.0), is_video=False)
        res["method"] = "ffmpeg_volumedetect+silencedetect"
        res["mean_db"] = mv
        res["silence_fraction"] = stats.get("fraction")
        res["longest_silence_ms"] = stats.get("longest_silence_ms")
        if mv is not None:
            apparent_silent = (mv < silence_threshold_db) or math.isinf(mv)
            res["silent"] = bool(apparent_silent and (stats.get("fraction", 0.0) >= frac_needed or stats.get("longest_silence_ms", 0.0) >= min_ms))
            return res
        # fallthrough to moviepy if parsing failed

    # Fallback: sample via moviepy with multiple short windows
    try:
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        clip = AudioFileClip(str(audio_path))
        duration = max(0.1, float(clip.duration or 0.1))
        win = max(0.05, min(0.25, duration / 4.0))  # 50-250ms
        # 4 windows across the file
        sample_points = [0.0, duration * 0.33, duration * 0.66, max(0.0, duration - win)]
        below = 0
        longest_ms = 0.0
        current_streak = 0
        vals = []
        for t in sample_points:
            try:
                sub = clip.subclip(t, min(duration, t + win))
                arr = sub.to_soundarray(fps=8000, buffersize=8000, nbytes=2)
                try:
                    sub.close()
                except Exception:
                    pass
                import numpy as np
                if arr.size == 0:
                    continue
                s = arr[: min(len(arr), 8000)]
                rms = float(np.sqrt(np.mean(np.square(s), dtype=np.float64)))
                db = 20.0 * math.log10(max(rms, 1e-8))
                vals.append(db)
                if db < silence_threshold_db:
                    below += 1
                    current_streak += 1
                    longest_ms = max(longest_ms, current_streak * win * 1000.0)
                else:
                    current_streak = 0
            except Exception:
                continue
        try:
            clip.close()
        except Exception:
            pass
        if vals:
            mean_db = float(sum(vals) / len(vals))
            fraction = below / max(1, len(sample_points))
            res["method"] = "moviepy_sample"
            res["mean_db"] = mean_db
            res["silence_fraction"] = fraction
            res["longest_silence_ms"] = longest_ms
            res["silent"] = bool(fraction >= frac_needed or longest_ms >= min_ms)
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
    min_ms = _env_int("MEDIA_SILENCE_MIN_MS", MEDIA_SILENCE_MIN_MS_DEFAULT)
    frac_needed = _env_float("MEDIA_SILENCE_FRACTION", MEDIA_SILENCE_FRACTION_DEFAULT)
    res: Dict[str, Any] = {"file": str(video_path), "exists": video_path.exists(), "has_audio": False, "silent": True, "method": None}
    if not video_path.exists():
        res["error"] = "video_not_found"
        return res

    # Try ffmpeg volumedetect + silencedetect on video
    if _FFMPEG_BIN:
        cmd = [_FFMPEG_BIN, "-hide_banner", "-loglevel", "info", "-i", str(video_path), "-af", "volumedetect", "-f", "null", "-"]
        code, out, err = _run_ffmpeg(cmd)
        mv = _parse_mean_volume(err)
        if "Stream #" in err and "Audio" in err:
            res["has_audio"] = True
        stats = _ffmpeg_silence_stats(video_path, silence_threshold_db, max(0.001, min_ms / 1000.0), is_video=True)
        res["method"] = "ffmpeg_volumedetect+silencedetect"
        if mv is not None:
            res["mean_db"] = mv
            res["silence_fraction"] = stats.get("fraction")
            res["longest_silence_ms"] = stats.get("longest_silence_ms")
            apparent_silent = (mv < silence_threshold_db) or math.isinf(mv)
            res["silent"] = bool((not res["has_audio"]) or (apparent_silent and (stats.get("fraction", 0.0) >= frac_needed or stats.get("longest_silence_ms", 0.0) >= min_ms)))
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
        win = max(0.05, min(0.25, duration / 4.0))
        sample_points = [0.0, duration * 0.33, duration * 0.66, max(0.0, duration - win)]
        vals = []
        below = 0
        longest_ms = 0.0
        current_streak = 0
        try:
            import numpy as np
        except Exception:
            np = None
        for t in sample_points:
            try:
                sub = clip.audio.subclip(t, min(duration, t + win))
                arr = sub.to_soundarray(fps=8000, buffersize=8000, nbytes=2)
                try:
                    sub.close()
                except Exception:
                    pass
                if arr.size == 0:
                    continue
                s = arr[: min(len(arr), 8000)]
                if np is not None:
                    rms = float((np.sqrt(np.mean(np.square(s), dtype=np.float64))))
                else:
                    import math as _m
                    rms = float(_m.sqrt(sum(float(x)**2 for x in s.flatten()) / s.size))
                db = 20.0 * math.log10(max(rms, 1e-8))
                vals.append(db)
                if db < silence_threshold_db:
                    below += 1
                    current_streak += 1
                    longest_ms = max(longest_ms, current_streak * win * 1000.0)
                else:
                    current_streak = 0
            except Exception:
                continue
        try:
            clip.close()
        except Exception:
            pass
        if vals:
            mean_db = float(sum(vals) / len(vals))
            fraction = below / max(1, len(sample_points))
            res["method"] = "moviepy_sample"
            res["mean_db"] = mean_db
            res["silence_fraction"] = fraction
            res["longest_silence_ms"] = longest_ms
            res["silent"] = bool(fraction >= frac_needed or longest_ms >= min_ms)
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
