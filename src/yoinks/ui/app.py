from __future__ import annotations

from textual.app import App

import yoinks.scripts as scripts_package
from yoinks.core.registry import registry
from yoinks.core.wrapper import Wrapper
from yoinks.ui.screens.link_screen import LinkScreen


class YoinksApp(App):
    """TUI entry point: paste a link, review settings, download."""

    TITLE = "Yoinks"

    def __init__(self) -> None:
        super().__init__()
        registry.discover(scripts_package)
        self.wrapper = Wrapper(registry)

    def on_mount(self) -> None:
        self.push_screen(LinkScreen(self.wrapper))
