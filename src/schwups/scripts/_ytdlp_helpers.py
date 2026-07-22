from __future__ import annotations

import shutil
from typing import Any

from yt_dlp.utils import sanitize_filename

from schwups.core.models import AudioField, ResolutionField, VideoInfo


class _SilentLogger:
    """Swallows yt-dlp's log output so it can't corrupt the Textual screen."""

    def debug(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _base_ytdlp_opts() -> dict[str, Any]:
    return {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "noplaylist": True,
    }


def _best_format_for_height(formats: list[dict[str, Any]], height: int) -> dict[str, Any]:
    candidates = [f for f in formats if f.get("height") == height and f.get("vcodec") not in (None, "none")]
    candidates.sort(key=lambda f: f.get("tbr") or 0, reverse=True)
    return candidates[0] if candidates else {}


def _best_audio_only(formats: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [f for f in formats if f.get("vcodec") in (None, "none") and f.get("acodec") not in (None, "none")]
    candidates.sort(key=lambda f: f.get("abr") or 0, reverse=True)
    return candidates[0] if candidates else {}


def _format_size(fmt: dict[str, Any]) -> int | None:
    size = fmt.get("filesize") or fmt.get("filesize_approx")
    return int(size) if size else None


def _estimate_size(formats: list[dict[str, Any]], height: int, ffmpeg_available: bool) -> int | None:
    video = _best_format_for_height(formats, height)
    video_size = _format_size(video)
    if video_size is None:
        return None
    if not ffmpeg_available or video.get("acodec") not in (None, "none"):
        return video_size
    audio_size = _format_size(_best_audio_only(formats)) or 0
    return video_size + audio_size


def _resolution_heights(formats: list[dict[str, Any]], ffmpeg_available: bool) -> list[int]:
    candidates = formats if ffmpeg_available else [f for f in formats if f.get("acodec") not in (None, "none")]
    heights = {f["height"] for f in candidates if f.get("height") and f.get("vcodec") not in (None, "none")}
    return sorted(heights, reverse=True)


def _video_info_from_ytdlp(url: str, info: dict[str, Any], ffmpeg_available: bool) -> VideoInfo:
    formats = info.get("formats", [])
    heights = _resolution_heights(formats, ffmpeg_available)
    choices = [f"{h}p" for h in heights]
    estimated_sizes = {
        f"{h}p": size for h in heights if (size := _estimate_size(formats, h, ffmpeg_available)) is not None
    }

    title = info.get("title") or "Unknown title"
    return VideoInfo(
        title=title,
        source_url=url,
        duration=info.get("duration"),
        thumbnail_url=info.get("thumbnail"),
        default_filename=sanitize_filename(title),
        resolution=ResolutionField(
            choices=choices,
            default=choices[0] if choices else "",
            estimated_size_bytes=estimated_sizes,
            available=bool(choices),
        ),
        audio_only=AudioField(default=False, available=ffmpeg_available),
    )


def _format_selector(height: int | None, ffmpeg_available: bool) -> str:
    if height is None:
        return "bestvideo+bestaudio/best" if ffmpeg_available else "best[acodec!=none][vcodec!=none]"
    if ffmpeg_available:
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
    return f"best[height<={height}][acodec!=none][vcodec!=none]"
