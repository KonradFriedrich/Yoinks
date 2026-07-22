from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from schwups.core.base import DownloaderScript
from schwups.core.models import (
    AudioField,
    DownloadRequest,
    DownloadResult,
    ResolutionField,
    VideoInfo,
)


class ExampleScript(DownloaderScript):
    """Fake script for example.com (RFC 2606 reserved domain).

    Returns hardcoded info instead of hitting the network, to prove the
    registry -> wrapper -> script flow works before any real downloader
    (e.g. yt-dlp) is wired in.
    """

    name = "example"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        host = urlparse(url).hostname or ""
        return host == "example.com" or host.endswith(".example.com")

    async def fetch_info(self, url: str) -> VideoInfo:
        return VideoInfo(
            title="Example Video",
            source_url=url,
            duration=42.0,
            thumbnail_url="https://example.com/thumb.jpg",
            default_filename="Example Video",
            resolution=ResolutionField(
                choices=["1080p", "720p", "480p"],
                default="1080p",
                estimated_size_bytes={
                    "1080p": 150_000_000,
                    "720p": 80_000_000,
                    "480p": 40_000_000,
                },
            ),
            audio_only=AudioField(default=False, available=False),  # no MP3 option for example script
        )

    async def download(self, request: DownloadRequest) -> DownloadResult:
        await asyncio.sleep(0)  # simulate async I/O
        return DownloadResult(
            success=True,
            file_path=request.destination_dir / f"{request.filename}.mp4",
        )
