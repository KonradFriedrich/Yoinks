from __future__ import annotations

import os
from pathlib import Path

from textual.suggester import Suggester


class PathSuggester(Suggester):
    """Suggests directory completions for a path Input, stdlib-only.

    Returns the first alphabetically matching subdirectory as a ghost-text
    suggestion (accepted with -> / End), the same UX Textual's Suggester API
    is built for elsewhere in the app.
    """

    def __init__(self) -> None:
        super().__init__(use_cache=False, case_sensitive=True)

    async def get_suggestion(self, value: str) -> str | None:
        path = Path(value).expanduser()
        if value.endswith(os.sep):
            parent, prefix = path, ""
        else:
            parent, prefix = path.parent, path.name

        try:
            candidates = sorted(
                entry.name for entry in parent.iterdir() if entry.is_dir() and entry.name.startswith(prefix)
            )
        except OSError:
            return None

        if not candidates:
            return None

        return value + candidates[0][len(prefix) :] + os.sep
