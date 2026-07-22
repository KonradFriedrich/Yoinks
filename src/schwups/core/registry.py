from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schwups.core.base import DownloaderScript


class ScriptRegistry:
    """Holds every discovered `DownloaderScript` subclass."""

    def __init__(self) -> None:
        self._scripts: list[type[DownloaderScript]] = []

    def register(self, script_cls: type[DownloaderScript]) -> None:
        if script_cls not in self._scripts:
            self._scripts.append(script_cls)

    def find_for_url(self, url: str) -> type[DownloaderScript] | None:
        for script_cls in self._scripts:
            if script_cls.can_handle(url):
                return script_cls
        return None

    def discover(self, package: ModuleType) -> None:
        """Import every module in `package` so scripts self-register.

        `package` must be a regular (non-namespace) package, e.g. the
        `schwups.scripts` module.
        """
        for module_info in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
            importlib.import_module(module_info.name)


registry = ScriptRegistry()
