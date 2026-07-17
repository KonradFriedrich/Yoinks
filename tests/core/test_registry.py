import yoinks.scripts as scripts_package
from yoinks.core.registry import registry
from yoinks.scripts.example_script import ExampleScript


def test_discover_registers_example_script():
    registry.discover(scripts_package)
    assert ExampleScript in registry._scripts


def test_find_for_url_matches_example_domain():
    registry.discover(scripts_package)
    assert registry.find_for_url("https://example.com/video/123") is ExampleScript


def test_find_for_url_returns_none_for_unknown_domain():
    registry.discover(scripts_package)
    assert registry.find_for_url("https://totally-unhandled-site.test/x") is None
