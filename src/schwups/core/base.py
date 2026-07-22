from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from schwups.core.models import DownloadRequest, DownloadResult, VideoInfo
from schwups.core.registry import registry


class DownloaderScript(ABC):
    """Base class for a per-site download script.

    Subclassing this (anywhere under `schwups.scripts`) automatically
    registers the script with the global registry — no decorator needed.
    """

    name: ClassVar[str]

    #: Optional full replacement for the default settings screen. Left as
    #: `type[Any]` (rather than a concrete Textual type) so this module has
    #: no dependency on `textual` — the real base screen class is defined
    #: once the UI is built. `None` means: use the default 4-field screen.
    settings_screen: ClassVar[type[Any] | None] = None

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        registry.register(cls)

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        """Return True if this script can download the given URL."""

    @abstractmethod
    async def fetch_info(self, url: str) -> VideoInfo:
        """Fetch title/duration/available options for the given URL."""

    @abstractmethod
    async def download(self, request: DownloadRequest) -> DownloadResult:
        """Download the video according to the given request."""
