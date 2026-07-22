from schwups.scripts.soundcloud_script import SoundCloudScript


def test_can_handle_accepts_soundcloud_variants():
    assert SoundCloudScript.can_handle("https://soundcloud.com/artist/track")
    assert SoundCloudScript.can_handle("https://www.soundcloud.com/artist/track")
    assert SoundCloudScript.can_handle("https://m.soundcloud.com/artist/track")
    assert SoundCloudScript.can_handle("https://on.soundcloud.com/abc123")


def test_can_handle_rejects_other_domains():
    assert not SoundCloudScript.can_handle("https://youtube.com/watch?v=abc")
    assert not SoundCloudScript.can_handle("https://example.com/track")
    assert not SoundCloudScript.can_handle("https://soundcloud.fake/track")


FAKE_SC_INFO = {
    "title": "My Track",
    "duration": 210.0,
    "thumbnail": "https://i1.sndcdn.com/artworks-abc.jpg",
    "formats": [],
}


async def test_fetch_info_shape(monkeypatch):
    import asyncio
    from schwups.scripts.soundcloud_script import SoundCloudScript

    script = SoundCloudScript()
    monkeypatch.setattr(
        "schwups.scripts.soundcloud_script.SoundCloudScript._extract",
        lambda self, url: FAKE_SC_INFO,
    )

    info = await script.fetch_info("https://soundcloud.com/artist/track")

    assert info.title == "My Track"
    assert info.duration == 210.0
    assert info.resolution.available is False  # audio platform, no resolution choice
    assert info.audio_only.default is True     # MP3 is the natural goal for SoundCloud
