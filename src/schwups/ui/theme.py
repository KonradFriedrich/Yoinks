from __future__ import annotations

import tomllib
from pathlib import Path

from textual.theme import Theme

OMARCHY_COLORS_PATH = Path.home() / ".config" / "omarchy" / "current" / "theme" / "colors.toml"

#: Plain black-and-white theme used when Omarchy isn't installed/configured.
#: surface/panel are left unset so Textual derives its own (still achromatic)
#: shades for them -- pinning them to literal black collapses widgets like
#: checkboxes that rely on a surface/panel tone distinct from the background
#: to stay visible.
FALLBACK_THEME = Theme(
    name="schwups-fallback",
    primary="#ffffff",
    secondary="#ffffff",
    accent="#ffffff",
    warning="#ffffff",
    error="#ffffff",
    success="#ffffff",
    foreground="#ffffff",
    background="#000000",
    dark=True,
)


def _relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance, used to decide whether a background is dark."""
    hex_color = hex_color.lstrip("#")
    channels = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def linearize(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linearize(c) for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _load_omarchy_colors(path: Path) -> dict[str, str] | None:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None


def build_omarchy_theme(path: Path = OMARCHY_COLORS_PATH) -> Theme | None:
    """Build a Textual Theme from the active Omarchy theme's colors.toml.

    Returns None if Omarchy isn't installed/configured or its colors.toml
    is missing required keys — callers should fall back to FALLBACK_THEME.
    """
    colors = _load_omarchy_colors(path)
    if colors is None:
        return None
    if not all(key in colors for key in ("accent", "foreground", "background")):
        return None

    return Theme(
        name="omarchy",
        primary=colors["accent"],
        secondary=colors.get("color4", colors["accent"]),
        accent=colors.get("color5", colors["accent"]),
        warning=colors.get("color3", colors["accent"]),
        error=colors.get("color1", colors["accent"]),
        success=colors.get("color2", colors["accent"]),
        foreground=colors["foreground"],
        background=colors["background"],
        surface=colors.get("color0", colors["background"]),
        panel=colors.get("color8", colors["background"]),
        dark=_relative_luminance(colors["background"]) < 0.5,
    )
