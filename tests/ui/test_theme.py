from pathlib import Path

from schwups.ui.theme import FALLBACK_THEME, _relative_luminance, build_omarchy_theme

GRUVBOX_COLORS = """
accent = "#7daea3"
cursor = "#bdae93"
foreground = "#d4be98"
background = "#282828"
selection_foreground = "#ebdbb2"
selection_background = "#d65d0e"

color0 = "#3c3836"
color1 = "#ea6962"
color2 = "#a9b665"
color3 = "#d8a657"
color4 = "#7daea3"
color5 = "#d3869b"
color6 = "#89b482"
color7 = "#d4be98"
color8 = "#3c3836"
color9 = "#ea6962"
color10 = "#a9b665"
color11 = "#d8a657"
color12 = "#7daea3"
color13 = "#d3869b"
color14 = "#89b482"
color15 = "#d4be98"
"""

LIGHT_COLORS = """
accent = "#6e6e6e"
foreground = "#000000"
background = "#ffffff"
"""


def test_build_omarchy_theme_returns_none_when_file_missing(tmp_path: Path):
    assert build_omarchy_theme(tmp_path / "does-not-exist.toml") is None


def test_build_omarchy_theme_returns_none_for_malformed_toml(tmp_path: Path):
    path = tmp_path / "colors.toml"
    path.write_text("this is not valid toml [[[")
    assert build_omarchy_theme(path) is None


def test_build_omarchy_theme_returns_none_when_required_keys_missing(tmp_path: Path):
    path = tmp_path / "colors.toml"
    path.write_text('cursor = "#ffffff"\n')
    assert build_omarchy_theme(path) is None


def test_build_omarchy_theme_maps_dark_palette(tmp_path: Path):
    path = tmp_path / "colors.toml"
    path.write_text(GRUVBOX_COLORS)

    theme = build_omarchy_theme(path)

    assert theme is not None
    assert theme.name == "omarchy"
    assert theme.primary == "#7daea3"  # accent
    assert theme.error == "#ea6962"  # color1
    assert theme.warning == "#d8a657"  # color3
    assert theme.success == "#a9b665"  # color2
    assert theme.background == "#282828"
    assert theme.dark is True


def test_build_omarchy_theme_detects_light_background(tmp_path: Path):
    path = tmp_path / "colors.toml"
    path.write_text(LIGHT_COLORS)

    theme = build_omarchy_theme(path)

    assert theme is not None
    assert theme.dark is False


def test_build_omarchy_theme_falls_back_to_accent_for_missing_ansi_colors(tmp_path: Path):
    path = tmp_path / "colors.toml"
    path.write_text('accent = "#123456"\nforeground = "#ffffff"\nbackground = "#000000"\n')

    theme = build_omarchy_theme(path)

    assert theme is not None
    assert theme.error == "#123456"
    assert theme.warning == "#123456"
    assert theme.success == "#123456"


def test_relative_luminance_black_and_white():
    assert _relative_luminance("#000000") == 0.0
    assert _relative_luminance("#ffffff") == 1.0


def test_fallback_theme_is_pure_black_and_white():
    assert FALLBACK_THEME.background == "#000000"
    assert FALLBACK_THEME.foreground == "#ffffff"
    assert FALLBACK_THEME.primary == "#ffffff"
