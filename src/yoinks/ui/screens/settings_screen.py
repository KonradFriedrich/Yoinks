from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from yoinks.core.exceptions import ScriptError
from yoinks.core.models import DownloadRequest, VideoInfo
from yoinks.core.wrapper import Wrapper
from yoinks.ui.formatting import format_bytes, format_duration
from yoinks.ui.path_suggester import PathSuggester

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads"


class DefaultSettingsScreen(Screen):
    """Default settings screen: directory, resolution, title, subtitles."""

    DEFAULT_CSS = """
    DefaultSettingsScreen {
        align: center middle;
    }

    #settings-box {
        width: auto;
        height: auto;
        border: round $primary;
        padding: 1 2;
    }

    #settings-box Input, #settings-box Select {
        width: 50;
    }

    #info-panel {
        color: $text-muted;
        margin-bottom: 1;
    }

    #status-label {
        margin-top: 1;
    }
    """

    BINDINGS = [("escape", "pop_screen", "Back")]

    def __init__(self, info: VideoInfo, url: str, wrapper: Wrapper) -> None:
        super().__init__()
        self._info = info
        self._url = url
        self._wrapper = wrapper

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-box"):
            yield Label(self._info.title, id="title-label")
            yield Static(self._format_info_panel(self._info.resolution.default or None), id="info-panel")

            yield Label("Download directory")
            yield Input(
                value=str(DEFAULT_DOWNLOAD_DIR),
                suggester=PathSuggester(),
                id="dir-input",
            )

            yield Label("Video resolution")
            yield Select(
                [(choice, choice) for choice in self._info.resolution.choices],
                value=self._info.resolution.default or Select.NULL,
                allow_blank=True,
                disabled=not self._info.resolution.available,
                id="resolution-select",
            )

            yield Label("Download title")
            yield Input(value=self._info.default_filename, id="filename-input")

            yield Checkbox(
                "Download subtitles",
                value=self._info.subtitles.default,
                disabled=not self._info.subtitles.available,
                id="subtitles-checkbox",
            )

            yield Button("Download", variant="primary", id="download-button")
            yield Label("", id="status-label")

    def on_mount(self) -> None:
        self.query_one("#download-button", Button).focus()

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "resolution-select":
            self.query_one("#info-panel", Static).update(self._format_info_panel(self._current_resolution()))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-button":
            self._download()

    @work(exclusive=True)
    async def _download(self) -> None:
        button = self.query_one("#download-button", Button)
        status = self.query_one("#status-label", Label)
        button.disabled = True
        status.update("Downloading…")
        request = self._build_request()
        try:
            result = await self._wrapper.download(request)
        except ScriptError as exc:
            status.update(f"Error: {exc}")
        else:
            if result.success:
                status.update(f"Saved to {result.file_path}")
            else:
                status.update(f"Error: {result.error}")
        finally:
            button.disabled = False
            button.focus()  # disabling a focused button bounces focus elsewhere

    def _build_request(self) -> DownloadRequest:
        return DownloadRequest(
            url=self._url,
            destination_dir=Path(self.query_one("#dir-input", Input).value),
            filename=self.query_one("#filename-input", Input).value,
            resolution=self._current_resolution(),
            download_subtitles=self.query_one("#subtitles-checkbox", Checkbox).value,
        )

    def _current_resolution(self) -> str | None:
        value = self.query_one("#resolution-select", Select).value
        return None if value is Select.NULL else value

    def _format_info_panel(self, resolution: str | None) -> str:
        parts = [f"Length: {format_duration(self._info.duration)}"]
        size = self._info.resolution.estimated_size_bytes.get(resolution) if resolution else None
        if size is not None:
            parts.append(f"Estimated size: {format_bytes(size)}")
        return "  |  ".join(parts)
