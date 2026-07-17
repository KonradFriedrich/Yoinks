from __future__ import annotations

from textual.app import App

import yoinks.scripts as scripts_package
from yoinks.core.registry import registry
from yoinks.core.wrapper import Wrapper
from yoinks.ui.screens.link_screen import LinkScreen
from yoinks.ui.theme import FALLBACK_THEME, build_omarchy_theme


class YoinksApp(App):
    """TUI entry point: paste a link, review settings, download."""

    TITLE = "Yoinks"

    def __init__(self) -> None:
        super().__init__()
        registry.discover(scripts_package)
        self.wrapper = Wrapper(registry)

        omarchy_theme = build_omarchy_theme()
        self.register_theme(FALLBACK_THEME)
        if omarchy_theme is not None:
            self.register_theme(omarchy_theme)
        self.theme = omarchy_theme.name if omarchy_theme is not None else FALLBACK_THEME.name

    def on_mount(self) -> None:
        self.push_screen(LinkScreen(self.wrapper))
