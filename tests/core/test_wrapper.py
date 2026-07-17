from pathlib import Path

import pytest

import yoinks.scripts as scripts_package
from yoinks.core.exceptions import UnsupportedURLError
from yoinks.core.models import DownloadRequest
from yoinks.core.registry import registry
from yoinks.core.wrapper import Wrapper


@pytest.fixture
def wrapper() -> Wrapper:
    registry.discover(scripts_package)
    return Wrapper(registry)


async def test_fetch_info_returns_video_info_with_fixed_fields(wrapper: Wrapper):
    info = await wrapper.fetch_info("https://example.com/video/123")

    assert info.title == "Example Video"
    assert info.resolution.choices == ["1080p", "720p", "480p"]
    assert info.resolution.available is True
    assert info.subtitles.available is False


async def test_fetch_info_raises_for_unsupported_url(wrapper: Wrapper):
    with pytest.raises(UnsupportedURLError):
        await wrapper.fetch_info("https://totally-unhandled-site.test/x")


async def test_download_returns_successful_result(wrapper: Wrapper, tmp_path: Path):
    request = DownloadRequest(
        url="https://example.com/video/123",
        destination_dir=tmp_path,
        filename="my-clip",
        resolution="720p",
        download_subtitles=False,
    )

    result = await wrapper.download(request)

    assert result.success is True
    assert result.file_path == tmp_path / "my-clip.mp4"
