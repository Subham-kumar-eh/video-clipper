"""
Core logic for fetching video info and cutting out a specific time range.

The trick that makes this fast: yt-dlp can be told to only fetch the
fragments/byte-ranges that fall inside a given time window (download_ranges),
and to re-encode just the cut edges so the clip starts and ends exactly on
your mark (force_keyframes_at_cuts). Everything in between stays untouched,
original-quality video, so a 10-second clip out of a 2-hour video doesn't
require downloading 2 hours of footage.
"""

import threading
from pathlib import Path

import yt_dlp
from yt_dlp.utils import download_range_func

# In-memory job store. Fine for a local, single-user tool.
# job = {"status", "percent", "message", "file", "error"}
JOBS = {}
JOBS_LOCK = threading.Lock()

FORMAT_MAP = {
    "best": "bv*+ba/b",
    "1080p": "bv*[height<=1080]+ba/b[height<=1080]",
    "720p": "bv*[height<=720]+ba/b[height<=720]",
    "480p": "bv*[height<=480]+ba/b[height<=480]",
}


def get_video_info(url: str) -> dict:
    """Fetch title/duration/thumbnail without downloading anything."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        raise RuntimeError("Could not read that video. Check the link and try again.")

    return {
        "title": info.get("title") or "Untitled",
        "duration": info.get("duration"),  # seconds, may be None for live streams
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader"),
    }


def _set_job(job_id: str, **kwargs):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(kwargs)


def run_clip_job(job_id: str, url: str, start: float, end: float, quality: str, download_dir: str):
    """
    Runs in a background thread. Downloads only the [start, end] window
    (in seconds) and writes the result into download_dir, named with the
    job_id as a prefix so we can find it afterwards regardless of what
    extension yt-dlp settles on.
    """

    def progress_hook(d):
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            percent = int(downloaded / total * 90) if total else 0
            _set_job(job_id, status="downloading", percent=percent,
                      message=f"Downloading segment... {percent}%")
        elif status == "finished":
            _set_job(job_id, status="processing", percent=92,
                      message="Cutting and merging with ffmpeg...")

    def pp_hook(d):
        if d.get("status") == "started":
            _set_job(job_id, percent=95, message=f"Running {d.get('postprocessor', 'ffmpeg')}...")
        elif d.get("status") == "finished":
            _set_job(job_id, percent=99, message="Finishing up...")

    outtmpl = str(Path(download_dir) / f"{job_id}_%(title).60s.%(ext)s")
    fmt = FORMAT_MAP.get(quality, FORMAT_MAP["best"])

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": fmt,
        "outtmpl": outtmpl,
        "download_ranges": download_range_func(None, [(start, end)]),
        "force_keyframes_at_cuts": True,
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [pp_hook],
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    try:
        _set_job(job_id, status="downloading", percent=0, message="Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        output_file = _find_output_file(download_dir, job_id)
        if not output_file:
            raise RuntimeError("Download finished but the output file went missing.")

        _set_job(job_id, status="done", percent=100, message="Done!", file=output_file)

    except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
        _set_job(job_id, status="error", percent=0, message="Failed", error=str(exc))


def _find_output_file(download_dir: str, job_id: str):
    matches = sorted(Path(download_dir).glob(f"{job_id}_*"))
    return matches[-1].name if matches else None
