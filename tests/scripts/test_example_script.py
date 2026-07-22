from schwups.scripts.example_script import ExampleScript


def test_can_handle_matches_example_domain():
    assert ExampleScript.can_handle("https://example.com/foo")
    assert ExampleScript.can_handle("https://sub.example.com/foo")


def test_can_handle_rejects_other_domains():
    assert not ExampleScript.can_handle("https://youtube.com/watch?v=123")


async def test_fetch_info_populates_resolution_and_audio_fields():
    script = ExampleScript()
    info = await script.fetch_info("https://example.com/foo")

    assert info.default_filename == "Example Video"
    assert set(info.resolution.estimated_size_bytes) == set(info.resolution.choices)
    assert info.audio_only.available is False
