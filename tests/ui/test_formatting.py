import pytest

from schwups.ui.formatting import format_bytes, format_duration


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (None, "Unknown length"),
        (0, "0:00"),
        (5, "0:05"),
        (65, "1:05"),
        (3599, "59:59"),
        (3600, "1:00:00"),
        (3725, "1:02:05"),
    ],
)
def test_format_duration(seconds, expected):
    assert format_duration(seconds) == expected


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (0, "0 B"),
        (500, "500 B"),
        (1024, "1.0 KB"),
        (1_536_000, "1.5 MB"),
        (150_000_000, "143.1 MB"),
        (5 * 1024**3, "5.0 GB"),
    ],
)
def test_format_bytes(n, expected):
    assert format_bytes(n) == expected
