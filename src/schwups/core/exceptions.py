from __future__ import annotations


class SchwupsError(Exception):
    """Base for all errors raised by the wrapper."""


class UnsupportedURLError(SchwupsError):
    def __init__(self, url: str) -> None:
        super().__init__(f"No script registered to handle URL: {url}")
        self.url = url


class ScriptError(SchwupsError):
    def __init__(self, script_name: str, original: Exception) -> None:
        super().__init__(f"Script '{script_name}' failed: {original}")
        self.script_name = script_name
        self.original = original
