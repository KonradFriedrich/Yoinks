from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, ProgressBar, Select

from schwups.core.exceptions import ScriptError
from schwups.core.models import DownloadRequest, VideoInfo
from schwups.core.wrapper import Wrapper
from schwups.ui.formatting import format_bytes, format_duration
from schwups.ui.path_suggester import PathSuggester

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads"


class DefaultSettingsScreen(Screen):
    """Default settings screen: directory, resolution, title, MP3 option."""

    CSS_PATH = "settings_screen.tcss"

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("backspace", "pop_screen", "Back"),
    ]

    def __init__(self, info: VideoInfo, url: str, wrapper: Wrapper) -> None:
        super().__init__()
        self._info = info
        self._url = url
        self._wrapper = wrapper

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-box"):
            with Horizontal(id="video-settings-box"):
                with Vertical(id="info-box"):
                    yield Label(self._info.title, id="title-label")
                    yield Label(f"Length: {format_duration(self._info.duration)}", id="length-label")
                    yield Label(self._format_size(self._info.resolution.default or None), id="size-label")

                with Vertical(id="resolution-box"):
                    yield Label("Video resolution")
                    yield Select(
                        [(choice, choice) for choice in self._info.resolution.choices],
                        value=self._info.resolution.default or Select.NULL,
                        allow_blank=True,
                        disabled=not self._info.resolution.available,
                        id="resolution-select",
                    )
                yield Checkbox(
                    "Download as MP3",
                    value=self._info.audio_only.default,
                    disabled=not self._info.audio_only.available,
                    id="audio-checkbox",
                )

            with Vertical(id="download-settings-box"):
                yield Label("Download directory")
                yield Input(
                    value=str(DEFAULT_DOWNLOAD_DIR),
                    suggester=PathSuggester(),
                    id="dir-input",
                )
                yield Label("Download title")
                yield Input(value=self._info.default_filename, id="filename-input")

        yield Button("Download", variant="primary", id="download-button")
        yield ProgressBar(id="progress-bar")
        yield Label("", id="status-label")
        yield Button("Download another", id="start-over-button", classes="hidden")

    def on_mount(self) -> None:
        self.query_one("#download-button", Button).focus()

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "resolution-select":
            self.query_one("#size-label", Label).update(self._format_size(self._current_resolution()))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-button":
            self._download()
        elif event.button.id == "start-over-button":
            self.app.pop_screen()

    @work(exclusive=True)
    async def _download(self) -> None:
        button = self.query_one("#download-button", Button)
        status = self.query_one("#status-label", Label)
        bar = self.query_one("#progress-bar", ProgressBar)
        button.disabled = True
        bar.update(progress=0)
        status.update("Downloading…")
        request = self._build_request()
        try:
            result = await self._wrapper.download(request)
        except ScriptError as exc:
            status.update(f"Error: {exc}")
        else:
            if result.success:
                status.update(f"Saved to {result.file_path}")
                self.query_one("#start-over-button").remove_class("hidden")
            else:
                status.update(f"Error: {result.error}")
        finally:
            button.disabled = False
            button.focus()

    def _build_request(self) -> DownloadRequest:
        return DownloadRequest(
            url=self._url,
            destination_dir=Path(self.query_one("#dir-input", Input).value),
            filename=self.query_one("#filename-input", Input).value,
            resolution=self._current_resolution(),
            audio_only=self.query_one("#audio-checkbox", Checkbox).value,
            progress_hook=self._make_progress_hook(),
        )

    def _current_resolution(self) -> str | None:
        value = self.query_one("#resolution-select", Select).value
        return None if value is Select.NULL else value

    def _format_size(self, resolution: str | None) -> str:
        size = self._info.resolution.estimated_size_bytes.get(resolution) if resolution else None
        if size is not None:
            return f"Estimated size: {format_bytes(size)}"
        return "Size estimation not possible"

    def _make_progress_hook(self) -> Callable[[dict[str, Any]], None]:
        bar = self.query_one("#progress-bar", ProgressBar)

        def hook(data: dict[str, Any]) -> None:
            if data.get("status") == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                downloaded = data.get("downloaded_bytes", 0)
                if total:
                    self.app.call_from_thread(bar.update, total=total, progress=downloaded)
            elif data.get("status") == "finished":
                self.app.call_from_thread(lambda: bar.update(progress=bar.total) if bar.total else None)

        return hook
