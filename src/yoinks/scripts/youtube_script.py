from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from yoinks.core.base import DownloaderScript
from yoinks.core.models import (
    DownloadRequest,
    DownloadResult,
    ResolutionField,
    SubtitleField,
    VideoInfo,
)

_YOUTUBE_HOSTS = {"youtube.com", "youtu.be", "music.youtube.com"}


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
        # Already muxed with audio (or no merge is happening), so the video
        # format's own size is the whole download.
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

    subtitles = info.get("subtitles") or {}
    automatic_captions = info.get("automatic_captions") or {}
    subtitles_available = bool(subtitles.get("en")) or bool(automatic_captions.get("en"))

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
        subtitles=SubtitleField(default=False, available=subtitles_available),
    )


def _format_selector(height: int | None, ffmpeg_available: bool) -> str:
    if height is None:
        return "bestvideo+bestaudio/best" if ffmpeg_available else "best[acodec!=none][vcodec!=none]"
    if ffmpeg_available:
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
    return f"best[height<={height}][acodec!=none][vcodec!=none]"


class YouTubeScript(DownloaderScript):
    """Real YouTube downloader backed by yt-dlp."""

    name = "youtube"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        host = (urlparse(url).hostname or "").removeprefix("www.").removeprefix("m.")
        return host in _YOUTUBE_HOSTS

    async def fetch_info(self, url: str) -> VideoInfo:
        info = await asyncio.to_thread(self._extract, url)
        return _video_info_from_ytdlp(url, info, _ffmpeg_available())

    async def download(self, request: DownloadRequest) -> DownloadResult:
        result_info = await asyncio.to_thread(self._run_download, request)
        filepath = result_info.get("requested_downloads", [{}])[0].get("filepath")
        return DownloadResult(success=True, file_path=Path(filepath) if filepath else None)

    def _extract(self, url: str) -> dict[str, Any]:
        with YoutubeDL(_base_ytdlp_opts()) as ydl:
            return ydl.extract_info(url, download=False)

    def _run_download(self, request: DownloadRequest) -> dict[str, Any]:
        request.destination_dir.mkdir(parents=True, exist_ok=True)
        ffmpeg_available = _ffmpeg_available()
        height = int(request.resolution[:-1]) if request.resolution and request.resolution.endswith("p") else None

        opts = _base_ytdlp_opts()
        opts["format"] = _format_selector(height, ffmpeg_available)
        opts["outtmpl"] = str(request.destination_dir / f"{sanitize_filename(request.filename)}.%(ext)s")
        if ffmpeg_available:
            opts["merge_output_format"] = "mp4"
        if request.download_subtitles:
            opts.update(
                writesubtitles=True,
                writeautomaticsub=True,
                subtitleslangs=["en"],
                subtitlesformat="srt",
            )

        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(request.url, download=True)
