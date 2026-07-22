from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ResolutionField:
    """Video resolution setting for the default settings screen.

    `available=False` means this script/video doesn't support choosing a
    resolution — the UI should show the field disabled rather than hide it.
    """

    choices: list[str] = field(default_factory=list)
    default: str = ""
    estimated_size_bytes: dict[str, int] = field(default_factory=dict)
    available: bool = True


@dataclass
class AudioField:
    """'Download as MP3' setting for the default settings screen.

    `available=False` greys the checkbox out (e.g. when ffmpeg is missing
    or the content is already audio and no conversion is needed/supported).
    """

    default: bool = False
    available: bool = True


@dataclass
class VideoInfo:
    title: str
    source_url: str
    duration: float | None = None
    thumbnail_url: str | None = None
    default_filename: str = ""
    resolution: ResolutionField = field(default_factory=ResolutionField)
    audio_only: AudioField = field(default_factory=AudioField)


@dataclass
class DownloadRequest:
    url: str
    destination_dir: Path
    filename: str
    resolution: str | None = None
    audio_only: bool = False
    progress_hook: Callable[[dict[str, Any]], None] | None = None


@dataclass
class DownloadResult:
    success: bool
    file_path: Path | None = None
    error: str | None = None
