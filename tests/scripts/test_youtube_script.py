from schwups.scripts._ytdlp_helpers import _format_selector, _video_info_from_ytdlp
from schwups.scripts.youtube_script import YouTubeScript


def test_can_handle_accepts_youtube_url_variants():
    assert YouTubeScript.can_handle("https://www.youtube.com/watch?v=abc")
    assert YouTubeScript.can_handle("https://youtube.com/watch?v=abc")
    assert YouTubeScript.can_handle("https://m.youtube.com/watch?v=abc")
    assert YouTubeScript.can_handle("https://youtu.be/abc")
    assert YouTubeScript.can_handle("https://music.youtube.com/watch?v=abc")


def test_can_handle_rejects_other_domains():
    assert not YouTubeScript.can_handle("https://example.com/watch?v=abc")
    assert not YouTubeScript.can_handle("https://vimeo.com/12345")


FAKE_INFO = {
    "title": "My Video / Cool",
    "duration": 120.0,
    "thumbnail": "https://example.com/thumb.jpg",
    "formats": [
        # storyboard sprite, must be excluded entirely
        {"format_id": "sb1", "height": 45, "vcodec": "none", "acodec": "none"},
        # video-only streams (need ffmpeg to merge)
        {"format_id": "137", "height": 1080, "vcodec": "avc1", "acodec": "none", "filesize": 100_000_000, "tbr": 500},
        {"format_id": "136", "height": 720, "vcodec": "avc1", "acodec": "none", "filesize": 50_000_000, "tbr": 300},
        # pre-muxed streams (work without ffmpeg)
        {
            "format_id": "18",
            "height": 360,
            "vcodec": "avc1",
            "acodec": "mp4a",
            "filesize": None,
            "filesize_approx": 20_000_000,
            "tbr": 100,
        },
        # best audio-only, used when merging
        {"format_id": "140", "height": None, "vcodec": "none", "acodec": "mp4a", "filesize": 5_000_000, "abr": 128},
    ],
}


def test_video_info_with_ffmpeg_includes_full_ladder_and_merged_sizes():
    info = _video_info_from_ytdlp("https://youtube.com/watch?v=x", FAKE_INFO, ffmpeg_available=True)

    assert info.resolution.choices == ["1080p", "720p", "360p"]
    assert info.resolution.default == "1080p"
    assert info.resolution.available is True
    # 1080p is video-only (100MB) + best audio (5MB) since it needs merging
    assert info.resolution.estimated_size_bytes["1080p"] == 105_000_000
    # 360p is already pre-muxed, so it's just its own size
    assert info.resolution.estimated_size_bytes["360p"] == 20_000_000


def test_video_info_without_ffmpeg_restricts_to_premuxed_formats():
    info = _video_info_from_ytdlp("https://youtube.com/watch?v=x", FAKE_INFO, ffmpeg_available=False)

    assert info.resolution.choices == ["360p"]
    assert info.resolution.default == "360p"
    assert info.resolution.estimated_size_bytes["360p"] == 20_000_000


def test_video_info_sanitizes_default_filename():
    info = _video_info_from_ytdlp("https://youtube.com/watch?v=x", FAKE_INFO, ffmpeg_available=True)

    assert "/" not in info.default_filename


def test_video_info_audio_only_field():
    info_with = _video_info_from_ytdlp("https://youtube.com/watch?v=x", FAKE_INFO, ffmpeg_available=True)
    assert info_with.audio_only.available is True
    assert info_with.audio_only.default is False

    info_without = _video_info_from_ytdlp("https://youtube.com/watch?v=x", FAKE_INFO, ffmpeg_available=False)
    assert info_without.audio_only.available is False


def test_format_selector_with_ffmpeg_merges_streams():
    assert _format_selector(1080, ffmpeg_available=True) == "bestvideo[height<=1080]+bestaudio/best[height<=1080]"


def test_format_selector_without_ffmpeg_stays_premuxed():
    assert _format_selector(720, ffmpeg_available=False) == "best[height<=720][acodec!=none][vcodec!=none]"


def test_format_selector_with_no_resolution_falls_back_to_best():
    assert _format_selector(None, ffmpeg_available=True) == "bestvideo+bestaudio/best"
    assert _format_selector(None, ffmpeg_available=False) == "best[acodec!=none][vcodec!=none]"
