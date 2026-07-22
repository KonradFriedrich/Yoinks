from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from schwups.core.base import DownloaderScript
from schwups.core.models import AudioField, DownloadRequest, DownloadResult, ResolutionField, VideoInfo
from schwups.scripts._ytdlp_helpers import (
    _base_ytdlp_opts,
    _ffmpeg_available,
    _format_selector,
    _video_info_from_ytdlp,
)


def _is_album_url(url: str) -> bool:
    return "/a/" in urlparse(url).path


def _album_info_from_bunkr(url: str, info: dict[str, Any]) -> VideoInfo:
    entries = info.get("entries") or []
    total_duration = sum(e.get("duration") or 0 for e in entries) or None
    title = info.get("title") or "Bunkr Album"
    return VideoInfo(
        title=title,
        source_url=url,
        duration=total_duration,
        default_filename=sanitize_filename(title),
        resolution=ResolutionField(available=False),
        audio_only=AudioField(available=False),
    )


class BunkrScript(DownloaderScript):
    """Bunkr downloader for individual videos and albums, backed by yt-dlp."""

    name = "bunkr"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        host = (urlparse(url).hostname or "").removeprefix("www.")
        return host.split(".")[0] == "bunkr"

    async def fetch_info(self, url: str) -> VideoInfo:
        info = await asyncio.to_thread(self._extract, url)
        if info.get("_type") == "playlist":
            return _album_info_from_bunkr(url, info)
        return _video_info_from_ytdlp(url, info, _ffmpeg_available())

    async def download(self, request: DownloadRequest) -> DownloadResult:
        result = await asyncio.to_thread(self._run_download, request)
        if _is_album_url(request.url):
            dest = request.destination_dir / sanitize_filename(request.filename)
            return DownloadResult(success=True, file_path=dest)
        filepath = result.get("requested_downloads", [{}])[0].get("filepath")
        return DownloadResult(success=True, file_path=Path(filepath) if filepath else None)

    def _extract(self, url: str) -> dict[str, Any]:
        opts = _base_ytdlp_opts()
        opts.pop("noplaylist", None)  # allow albums through
        opts["extract_flat"] = _is_album_url(url)  # fast shallow fetch for albums
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def _run_download(self, request: DownloadRequest) -> dict[str, Any]:
        is_album = _is_album_url(request.url)
        safe_name = sanitize_filename(request.filename)
        ffmpeg_available = _ffmpeg_available()

        opts = _base_ytdlp_opts()

        if is_album:
            dest_dir = request.destination_dir / safe_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            opts.pop("noplaylist", None)
            opts["outtmpl"] = str(dest_dir / "%(title)s.%(ext)s")
        else:
            request.destination_dir.mkdir(parents=True, exist_ok=True)
            if request.audio_only and ffmpeg_available:
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"}
                ]
            else:
                height = int(request.resolution[:-1]) if request.resolution and request.resolution.endswith("p") else None
                opts["format"] = _format_selector(height, ffmpeg_available)
                if ffmpeg_available:
                    opts["merge_output_format"] = "mp4"
            opts["outtmpl"] = str(request.destination_dir / f"{safe_name}.%(ext)s")

        if request.progress_hook is not None:
            opts["progress_hooks"] = [request.progress_hook]

        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(request.url, download=True)
