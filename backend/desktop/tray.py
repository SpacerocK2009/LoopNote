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
    draw.text((17, 18), "SF6", fill="white")
    return image


class TrayController:
    def __init__(self, dispatch: Callable[[str], None], toggle_auto_start: Callable[[], None]) -> None:
        self.dispatch = dispatch
        self.toggle_auto_start = toggle_auto_start
        self.icon = pystray.Icon("SF6StrategyBoard", _icon_image(), "SF6 Strategy Board", menu=pystray.Menu(
            pystray.MenuItem("メイン画面を開く", lambda *_: dispatch("open_editor"), default=True),
            pystray.MenuItem("常駐メモを表示", lambda *_: dispatch("show")),
            pystray.MenuItem("常駐メモを隠す", lambda *_: dispatch("hide")),
            pystray.MenuItem("最前面切替", lambda *_: dispatch("toggle_topmost")),
            pystray.MenuItem("クリック透過切替", lambda *_: dispatch("toggle_click_through")),
            pystray.MenuItem("表示内容を更新", lambda *_: dispatch("refresh")),
            pystray.MenuItem("自動起動", self._toggle_auto, checked=lambda _: load_overlay_settings().auto_start),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("終了", lambda *_: dispatch("quit")),
        ))

    def _toggle_auto(self, *_: object) -> None:
        self.toggle_auto_start()
        self.icon.update_menu()

    def start(self) -> None:
        threading.Thread(target=self.icon.run, name="overlay-tray", daemon=True).start()

    def stop(self) -> None:
        self.icon.stop()
