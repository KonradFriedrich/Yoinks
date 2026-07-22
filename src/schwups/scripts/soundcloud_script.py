from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from schwups.core.base import DownloaderScript
from schwups.core.models import AudioField, DownloadRequest, DownloadResult, ResolutionField, VideoInfo
from schwups.scripts._ytdlp_helpers import _base_ytdlp_opts, _ffmpeg_available

_SOUNDCLOUD_HOSTS = {"soundcloud.com", "on.soundcloud.com"}


class SoundCloudScript(DownloaderScript):
    """SoundCloud downloader backed by yt-dlp (no API key required)."""

    name = "soundcloud"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        host = (urlparse(url).hostname or "").removeprefix("www.").removeprefix("m.")
        return host in _SOUNDCLOUD_HOSTS

    async def fetch_info(self, url: str) -> VideoInfo:
        info = await asyncio.to_thread(self._extract, url)
        title = info.get("title") or "Unknown title"
        return VideoInfo(
            title=title,
            source_url=url,
            duration=info.get("duration"),
            thumbnail_url=info.get("thumbnail"),
            default_filename=sanitize_filename(title),
            resolution=ResolutionField(available=False),
            audio_only=AudioField(available=_ffmpeg_available(), default=True),
        )

    async def download(self, request: DownloadRequest) -> DownloadResult:
        result_info = await asyncio.to_thread(self._run_download, request)
        filepath = result_info.get("requested_downloads", [{}])[0].get("filepath")
        return DownloadResult(success=True, file_path=Path(filepath) if filepath else None)

    def _extract(self, url: str) -> dict[str, Any]:
        with YoutubeDL(_base_ytdlp_opts()) as ydl:
            return ydl.extract_info(url, download=False)

    def _run_download(self, request: DownloadRequest) -> dict[str, Any]:
        request.destination_dir.mkdir(parents=True, exist_ok=True)
        opts = _base_ytdlp_opts()
        opts["format"] = "bestaudio/best"
        opts["outtmpl"] = str(request.destination_dir / f"{sanitize_filename(request.filename)}.%(ext)s")
        if request.audio_only and _ffmpeg_available():
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"}
            ]
        if request.progress_hook is not None:
            opts["progress_hooks"] = [request.progress_hook]
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(request.url, download=True)
