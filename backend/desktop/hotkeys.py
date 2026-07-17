from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import threading
from collections.abc import Callable

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002


class HotkeyManager:
    HOTKEYS = {1: (ord("M"), "toggle_visible"), 2: (ord("T"), "toggle_topmost"),
               3: (ord("C"), "toggle_click_through"), 4: (ord("E"), "open_editor")}

    def __init__(self, callback: Callable[[str], None]) -> None:
        self.callback = callback
        self.thread: threading.Thread | None = None
        self.thread_id: int | None = None

    def start(self) -> None:
        if os.name != "nt": return
        self.thread = threading.Thread(target=self._run, name="overlay-hotkeys", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        registered: list[int] = []
        for hotkey_id, (key, _) in self.HOTKEYS.items():
            if ctypes.windll.user32.RegisterHotKey(None, hotkey_id, MOD_CONTROL | MOD_ALT, key):
                registered.append(hotkey_id)
        message = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            if message.message == WM_HOTKEY and message.wParam in self.HOTKEYS:
                self.callback(self.HOTKEYS[message.wParam][1])
        for hotkey_id in registered:
            ctypes.windll.user32.UnregisterHotKey(None, hotkey_id)

    def stop(self) -> None:
        if self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
