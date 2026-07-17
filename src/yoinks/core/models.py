from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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
class SubtitleField:
    """Subtitle download setting for the default settings screen."""

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
    subtitles: SubtitleField = field(default_factory=SubtitleField)


@dataclass
class DownloadRequest:
    url: str
    destination_dir: Path
    filename: str
    resolution: str | None = None
    download_subtitles: bool = False


@dataclass
class DownloadResult:
    success: bool
    file_path: Path | None = None
    error: str | None = None
