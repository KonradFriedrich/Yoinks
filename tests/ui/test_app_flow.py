from textual.widgets import Button, Checkbox, Label

from yoinks.ui.app import YoinksApp
from yoinks.ui.screens.settings_screen import DefaultSettingsScreen


async def test_paste_link_reaches_settings_screen_and_downloads():
    app = YoinksApp()
    async with app.run_test() as pilot:
        for char in "https://example.com/watch?v=abc":
            await pilot.press(char)
        await pilot.press("enter")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert isinstance(app.screen, DefaultSettingsScreen)
        assert app.screen.query_one("#subtitles-checkbox", Checkbox).disabled is True
        assert app.screen.query_one(Button).has_focus

        await pilot.press("enter")
        await app.workers.wait_for_complete()
        await pilot.pause()

        status = app.screen.query_one("#status-label", Label)
        assert str(status.content).startswith("Saved to")
