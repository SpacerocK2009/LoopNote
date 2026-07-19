from __future__ import annotations

import threading
from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw

from backend.desktop.overlay_settings import load_overlay_settings


def _icon_image() -> Image.Image:
    image = Image.new("RGB", (64, 64), "#111522")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((7, 7, 57, 57), 9, fill="#6375f5")
    draw.text((12, 18), "LOOP", fill="white")
    return image


class TrayController:
    def __init__(self, dispatch: Callable[[str], None], toggle_auto_start: Callable[[], None]) -> None:
        self.dispatch = dispatch
        self.toggle_auto_start = toggle_auto_start
        self.icon = pystray.Icon("LoopNote", _icon_image(), "LoopNote", menu=pystray.Menu(
            pystray.MenuItem("Open LoopNote", lambda *_: dispatch("open_editor"), default=True),
            pystray.MenuItem("Show overlay", lambda *_: dispatch("show")),
            pystray.MenuItem("Hide overlay", lambda *_: dispatch("hide")),
            pystray.MenuItem("Toggle always on top", lambda *_: dispatch("toggle_topmost")),
            pystray.MenuItem("Toggle click-through", lambda *_: dispatch("toggle_click_through")),
            pystray.MenuItem("Refresh content", lambda *_: dispatch("refresh")),
            pystray.MenuItem("Start with Windows", self._toggle_auto, checked=lambda _: load_overlay_settings().auto_start),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda *_: dispatch("quit")),
        ))

    def _toggle_auto(self, *_: object) -> None:
        self.toggle_auto_start()
        self.icon.update_menu()

    def start(self) -> None:
        threading.Thread(target=self.icon.run, name="overlay-tray", daemon=True).start()

    def stop(self) -> None:
        self.icon.stop()
