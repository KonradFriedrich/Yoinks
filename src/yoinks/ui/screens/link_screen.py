from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label

from yoinks.core.exceptions import ScriptError, UnsupportedURLError
from yoinks.core.wrapper import Wrapper
from yoinks.ui.screens.settings_screen import DefaultSettingsScreen

TITLE = f"""
 @@@@@@    @@@@@@@  @@@  @@@  @@@  @@@  @@@  @@@  @@@  @@@@@@@    @@@@@@   
@@@@@@@   @@@@@@@@  @@@  @@@  @@@  @@@  @@@  @@@  @@@  @@@@@@@@  @@@@@@@   
!@@       !@@       @@!  @@@  @@!  @@!  @@!  @@!  @@@  @@!  @@@  !@@       
!@!       !@!       !@!  @!@  !@!  !@!  !@!  !@!  @!@  !@!  @!@  !@!       
!!@@!!    !@!       @!@!@!@!  @!!  !!@  @!@  @!@  !@!  @!@@!@!   !!@@!!    
 !!@!!!   !!!       !!!@!!!!  !@!  !!!  !@!  !@!  !!!  !!@!!!     !!@!!!   
     !:!  :!!       !!:  !!!  !!:  !!:  !!:  !!:  !!!  !!:            !:!  
    !:!   :!:       :!:  !:!  :!:  :!:  :!:  :!:  !:!  :!:           !:!   
:::: ::    ::: :::  ::   :::   :::: :: :::   ::::: ::   ::       :::: ::   
:: : :     :: :: :   :   : :    :: :  : :     : :  :    :        :: : :    
"""


class LinkScreen(Screen):
    """First screen: a single focused input for pasting a video link."""

    CSS_PATH = "link_screen.tcss"

    def __init__(self, wrapper: Wrapper) -> None:
        super().__init__()
        self._wrapper = wrapper

    def compose(self) -> ComposeResult:
        with Vertical(id="title-box"):
            yield Label(TITLE, id="title-label")
            with Vertical(id="link-box"):
                yield Input(placeholder="https://...", id="url-input")
                yield Label("", id="error-label")

    def on_mount(self) -> None:
        self.query_one("#url-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input" and event.value.strip():
            self._fetch(event.value.strip())

    @work(exclusive=True)
    async def _fetch(self, url: str) -> None:
        url_input = self.query_one("#url-input", Input)
        error_label = self.query_one("#error-label", Label)
        error_label.update("")
        url_input.disabled = True
        try:
            info = await self._wrapper.fetch_info(url)
        except (UnsupportedURLError, ScriptError) as exc:
            error_label.update(str(exc))
            url_input.disabled = False
            url_input.focus()
        else:
            screen_cls = self._wrapper.settings_screen_for(url) or DefaultSettingsScreen
            self.app.push_screen(screen_cls(info, url, self._wrapper))
            url_input.disabled = False
