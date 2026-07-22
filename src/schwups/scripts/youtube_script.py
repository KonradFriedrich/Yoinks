from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from schwups.core.base import DownloaderScript
from schwups.core.models import DownloadRequest, DownloadResult, VideoInfo
from schwups.scripts._ytdlp_helpers import (
    _base_ytdlp_opts,
    _ffmpeg_available,
    _format_selector,
    _video_info_from_ytdlp,
)

_YOUTUBE_HOSTS = {"youtube.com", "youtu.be", "music.youtube.com"}


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

        opts = _base_ytdlp_opts()
        opts["outtmpl"] = str(request.destination_dir / f"{sanitize_filename(request.filename)}.%(ext)s")

        if request.audio_only:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"}
            ]
        else:
            height = int(request.resolution[:-1]) if request.resolution and request.resolution.endswith("p") else None
            opts["format"] = _format_selector(height, ffmpeg_available)
            if ffmpeg_available:
                opts["merge_output_format"] = "mp4"

        if request.progress_hook is not None:
            opts["progress_hooks"] = [request.progress_hook]

        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(request.url, download=True)
