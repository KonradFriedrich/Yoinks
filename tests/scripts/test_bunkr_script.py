from schwups.scripts.bunkr_script import BunkrScript, _album_info_from_bunkr, _is_album_url
from schwups.scripts._ytdlp_helpers import _video_info_from_ytdlp


def test_can_handle_accepts_all_bunkr_tlds():
    for tld in ("si", "sk", "ru", "la", "to", "fi", "ph", "ac", "cr"):
        assert BunkrScript.can_handle(f"https://bunkr.{tld}/v/somevideo"), f"failed for bunkr.{tld}"


def test_can_handle_rejects_cdn_subdomains():
    assert not BunkrScript.can_handle("https://cdn.bunkr.ru/file.mp4")
    assert not BunkrScript.can_handle("https://i-burger.bunkr.ru/file.mp4")


def test_can_handle_rejects_other_domains():
    assert not BunkrScript.can_handle("https://example.com/v/video")
    assert not BunkrScript.can_handle("https://youtube.com/watch?v=abc")


def test_is_album_url():
    assert _is_album_url("https://bunkr.si/a/myalbum")
    assert not _is_album_url("https://bunkr.si/v/myvideo")


FAKE_ALBUM_INFO = {
    "title": "My Album",
    "entries": [
        {"title": "clip1", "duration": 30.0},
        {"title": "clip2", "duration": 45.0},
        {"title": "clip3", "duration": None},
    ],
}

FAKE_VIDEO_INFO = {
    "title": "Bunkr Video",
    "duration": 60.0,
    "thumbnail": "https://bunkr.si/thumb.jpg",
    "formats": [
        {"format_id": "mp4", "height": 720, "vcodec": "avc1", "acodec": "mp4a", "filesize": 30_000_000, "tbr": 2000},
    ],
}


def test_album_info_aggregates_duration():
    info = _album_info_from_bunkr("https://bunkr.si/a/myalbum", FAKE_ALBUM_INFO)

    assert info.title == "My Album"
    assert info.duration == 75.0  # 30 + 45 + 0 (None treated as 0)
    assert info.resolution.available is False
    assert info.audio_only.available is False


def test_album_info_title_sanitized():
    info = _album_info_from_bunkr("https://bunkr.si/a/x", {"title": "Bad/Title", "entries": []})
    assert "/" not in info.default_filename


def test_single_video_info_uses_ytdlp_helper():
    info = _video_info_from_ytdlp("https://bunkr.si/v/vid", FAKE_VIDEO_INFO, ffmpeg_available=False)

    assert info.title == "Bunkr Video"
    assert info.resolution.choices == ["720p"]
    assert info.resolution.available is True
