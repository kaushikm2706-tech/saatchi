import subprocess, json
from pathlib import Path


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {p.stderr[-500:]}")
    return p.stdout


def probe(video: str) -> dict:
    out = _run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", video])
    return json.loads(out)


def duration_s(video: str) -> float:
    return float(probe(video)["format"]["duration"])


def extract_wav(video: str, out_wav: str) -> str:
    """Mono 16-bit PCM 24 kHz WAV, as required by Muse Voice Transcribe (<=10 min, <=32 MB)."""
    _run(["ffmpeg", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "24000",
          "-c:a", "pcm_s16le", "-map_metadata", "-1", out_wav])
    size = Path(out_wav).stat().st_size
    if size > 32 * 1024 * 1024:
        raise ValueError("WAV exceeds the documented 32 MB limit; trim the clip.")
    if duration_s(video) > 600:
        raise ValueError("Audio exceeds the documented 10 minute limit; trim the clip.")
    return out_wav


def make_sam_copy(video: str, out_mp4: str, fps: int = 15) -> str:
    """H.264 MP4 at reduced fps: SAM is billed per frame, so fewer frames = cheaper."""
    _run(["ffmpeg", "-y", "-i", video, "-vf", f"fps={fps}", "-an", "-c:v", "libx264",
          "-preset", "veryfast", "-pix_fmt", "yuv420p", out_mp4])
    return out_mp4
