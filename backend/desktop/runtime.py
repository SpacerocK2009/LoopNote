from __future__ import annotations

import queue
import threading

from backend.desktop.hotkeys import HotkeyManager
from backend.desktop.memo_overlay import MemoOverlay
from backend.desktop.overlay_settings import load_overlay_settings, save_overlay_settings, set_auto_start
from backend.desktop.tray import TrayController


class DesktopRuntime:
    def __init__(self) -> None:
        self.commands: queue.Queue[str] = queue.Queue()
        self.hotkeys = HotkeyManager(self.dispatch)
        self.tray = TrayController(self.dispatch, self.toggle_auto_start)

    def dispatch(self, command: str) -> None:
        self.commands.put(command)

    def toggle_auto_start(self) -> None:
        settings = load_overlay_settings()
        settings.auto_start = not settings.auto_start
        set_auto_start(settings.auto_start)
        save_overlay_settings(settings)

    def run(self) -> None:
        self.hotkeys.start()
        self.tray.start()
        MemoOverlay(self.commands, self.stop_helpers).run()

    def stop_helpers(self) -> None:
        self.hotkeys.stop()
        self.tray.stop()


_runtime: DesktopRuntime | None = None
_lock = threading.Lock()


def set_runtime(runtime: DesktopRuntime | None) -> None:
    global _runtime
    with _lock: _runtime = runtime


def dispatch_overlay_command(command: str) -> bool:
    with _lock: runtime = _runtime
    if runtime is None: return False
    runtime.dispatch(command)
    return True
