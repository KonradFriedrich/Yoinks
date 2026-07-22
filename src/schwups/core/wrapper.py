from __future__ import annotations

from typing import Any

from schwups.core.base import DownloaderScript
from schwups.core.exceptions import ScriptError, UnsupportedURLError
from schwups.core.models import DownloadRequest, DownloadResult, VideoInfo
from schwups.core.registry import ScriptRegistry


class Wrapper:
    """Entry point the (future) UI talks to: dispatches to the right script."""

    def __init__(self, registry: ScriptRegistry) -> None:
        self._registry = registry

    async def fetch_info(self, url: str) -> VideoInfo:
        script_cls = self._require_script(url)
        try:
            return await script_cls().fetch_info(url)
        except Exception as exc:
            raise ScriptError(script_cls.name, exc) from exc

    async def download(self, request: DownloadRequest) -> DownloadResult:
        script_cls = self._require_script(request.url)
        try:
            return await script_cls().download(request)
        except Exception as exc:
            raise ScriptError(script_cls.name, exc) from exc

    def settings_screen_for(self, url: str) -> type[Any] | None:
        return self._require_script(url).settings_screen

    def _require_script(self, url: str) -> type[DownloaderScript]:
        script_cls = self._registry.find_for_url(url)
        if script_cls is None:
            raise UnsupportedURLError(url)
        return script_cls
