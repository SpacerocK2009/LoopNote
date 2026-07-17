from __future__ import annotations

import ctypes
import os
import queue
import tkinter as tk
from collections.abc import Callable

from backend.desktop.overlay_settings import list_monitors, load_overlay_settings, save_overlay_settings
from backend.database import db_connection
from backend.models import OverlaySettings

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x20
WS_EX_LAYERED = 0x80000
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010


def clamp_to_monitor(x: int, y: int, width: int, height: int, monitor: dict[str, object]) -> tuple[int, int]:
    """Keep the whole overlay inside the selected monitor's visible bounds."""
    left, top = int(monitor["x"]), int(monitor["y"])
    right, bottom = left + int(monitor["width"]), top + int(monitor["height"])
    return max(left, min(x, right - width)), max(top, min(y, bottom - height))


class MemoOverlay:
    def __init__(self, command_queue: queue.Queue[str], on_close: Callable[[], None]) -> None:
        self.command_queue = command_queue
        self.on_close = on_close
        self.settings = load_overlay_settings()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.configure(bg=self.settings.background_color)
        self._drag_origin: tuple[int, int, int, int] | None = None
        self._resize_origin: tuple[int, int, int, int] | None = None
        self.kicker_label = tk.Label(self.root, text="▰  BATTLE PLAN / STRATEGY DECK", anchor="w", padx=18, pady=9, font=("Segoe UI", 9, "bold"))
        self.header_label = tk.Label(self.root, text="MATCH OBJECTIVES", anchor="w", padx=18, pady=6, font=("Yu Gothic UI", 17, "bold"))
        self.deck_frame = tk.Frame(self.root, padx=12, pady=8)
        self.kicker_label.pack(fill="x")
        self.header_label.pack(fill="x")
        self.deck_frame.pack(fill="both", expand=True)
        self.resize_handle = tk.Label(
            self.root, text="◢", anchor="se", padx=3, pady=1,
            font=("Segoe UI Symbol", 13), cursor="size_nw_se",
        )
        self.resize_handle.place(relx=1.0, rely=1.0, anchor="se", width=24, height=24)
        self.resize_handle.bind("<ButtonPress-1>", self._start_resize)
        self.resize_handle.bind("<B1-Motion>", self._resize)
        self.resize_handle.bind("<ButtonRelease-1>", self._end_resize)
        self._bind_drag(self.root, self.kicker_label, self.header_label, self.deck_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.apply_settings(self.settings, reposition=True)
        self.root.after(100, self._process_commands)

    def run(self) -> None:
        self.root.mainloop()

    def apply_settings(self, settings: OverlaySettings, reposition: bool = False) -> None:
        self.settings = settings
        if reposition or settings.position_preset != "自由":
            self._calculate_position()
        monitor = self._configured_monitor()
        settings.x, settings.y = clamp_to_monitor(
            settings.x, settings.y, settings.width, settings.height, monitor
        )
        self._set_geometry(settings.x, settings.y, settings.width, settings.height)
        self.root.attributes("-alpha", settings.opacity)
        self.root.attributes("-topmost", settings.always_on_top)
        self.root.configure(bg=settings.background_color)
        self.kicker_label.configure(bg="#ec3154", fg="#ffffff")
        self.header_label.configure(bg=settings.background_color, fg=settings.text_color)
        self.deck_frame.configure(bg=settings.background_color)
        self._render_strategy_cards()
        self.resize_handle.configure(bg=settings.background_color, fg="#6ee7f2")
        self.root.update_idletasks()
        self._set_click_through(settings.click_through)
        if settings.visible:
            self.show()
        else:
            self.hide(persist=False)

    def _bind_drag(self, *widgets: tk.Widget) -> None:
        for widget in widgets:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)

    def _selected_notes(self) -> list[dict[str, object]]:
        ids = self.settings.selected_note_ids
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with db_connection() as db:
            rows = db.execute(f"SELECT * FROM notes WHERE id IN ({placeholders})", ids).fetchall()
        by_id = {row["id"]: dict(row) for row in rows}
        return [by_id[note_id] for note_id in ids if note_id in by_id]

    def _render_strategy_cards(self) -> None:
        for child in self.deck_frame.winfo_children():
            child.destroy()
        notes = self._selected_notes()
        if not notes:
            empty = tk.Label(self.deck_frame, text="NO STRATEGY SELECTED\nWeb画面から戦略メモを選択してください", justify="center", font=("Yu Gothic UI", 12, "bold"), bg=self.settings.background_color, fg="#788297")
            empty.pack(fill="both", expand=True, pady=24)
            self._bind_drag(empty)
            return
        compact_size = max(10, min(self.settings.text_size, 18 if len(notes) > 2 else 22))
        for index, note in enumerate(notes, 1):
            card = tk.Frame(self.deck_frame, bg="#171d28", highlightbackground="#323b4d", highlightthickness=1)
            card.pack(fill="x", pady=(0, 7))
            accent = tk.Frame(card, width=5, bg="#65e5ee" if note["priority"] != "high" else "#ec3154")
            accent.pack(side="left", fill="y")
            content = tk.Frame(card, bg="#171d28", padx=11, pady=7)
            content.pack(side="left", fill="both", expand=True)
            meta = f"{index:02d}  {(note['character'] or 'ALL').upper()} / {(note['category'] or 'GENERAL').upper()}"
            meta_label = tk.Label(content, text=meta, anchor="w", bg="#171d28", fg="#65e5ee", font=("Segoe UI", 8, "bold"))
            title = tk.Label(content, text=str(note["title"]), anchor="w", justify="left", bg="#171d28", fg=self.settings.text_color, font=("Yu Gothic UI", compact_size, "bold"), wraplength=max(160, self.settings.width - 70))
            detail_parts = [str(note["bullet_points"]).strip()]
            if note["goal"]: detail_parts.append(f"TARGET  {note['goal']}")
            detail = tk.Label(content, text="\n".join(part for part in detail_parts if part), anchor="nw", justify="left", bg="#171d28", fg="#cbd3df", font=("Yu Gothic UI", max(9, compact_size - 4)), wraplength=max(160, self.settings.width - 70))
            meta_label.pack(fill="x"); title.pack(fill="x", pady=(2, 1)); detail.pack(fill="x")
            self._bind_drag(card, accent, content, meta_label, title, detail)

    def _calculate_position(self) -> None:
        monitor = self._configured_monitor()
        margin = 30
        preset = self.settings.position_preset
        if preset == "自由":
            return
        self.settings.x = int(monitor["x"]) + (margin if "左" in preset else int(monitor["width"]) - self.settings.width - margin)
        self.settings.y = int(monitor["y"]) + (margin if "上" in preset else int(monitor["height"]) - self.settings.height - margin)

    def _configured_monitor(self) -> dict[str, object]:
        monitors = list_monitors()
        return monitors[min(self.settings.monitor_index, len(monitors) - 1)]

    def _monitor_at(self, x: int, y: int) -> dict[str, object]:
        monitors = list_monitors()
        for index, monitor in enumerate(monitors):
            if (int(monitor["x"]) <= x < int(monitor["x"]) + int(monitor["width"]) and
                    int(monitor["y"]) <= y < int(monitor["y"]) + int(monitor["height"])):
                self.settings.monitor_index = index
                return monitor
        return self._configured_monitor()

    def _window_handle(self) -> int:
        hwnd = self.root.winfo_id()
        if os.name == "nt":
            parent = ctypes.windll.user32.GetParent(hwnd)
            return parent or hwnd
        return hwnd

    def _set_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """Set absolute virtual-screen coordinates; Tk treats negative values as edge offsets."""
        self.root.update_idletasks()
        if os.name == "nt":
            ctypes.windll.user32.SetWindowPos(
                self._window_handle(), 0, x, y, width, height, SWP_NOZORDER | SWP_NOACTIVATE
            )
        else:
            self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _set_click_through(self, enabled: bool) -> None:
        if os.name != "nt" or not self.root.winfo_exists():
            return
        hwnd = self._window_handle()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_LAYERED | WS_EX_TRANSPARENT) if enabled else (style & ~WS_EX_TRANSPARENT)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def show(self, persist: bool = True) -> None:
        self.root.deiconify()
        self.root.lift()
        self.settings.visible = True
        if persist: save_overlay_settings(self.settings)

    def hide(self, persist: bool = True) -> None:
        self.root.withdraw()
        self.settings.visible = False
        if persist: save_overlay_settings(self.settings)

    def toggle_visible(self) -> None:
        self.hide() if self.settings.visible else self.show()

    def toggle_topmost(self) -> None:
        self.settings.always_on_top = not self.settings.always_on_top
        self.root.attributes("-topmost", self.settings.always_on_top)
        save_overlay_settings(self.settings)

    def toggle_click_through(self) -> None:
        self.settings.click_through = not self.settings.click_through
        self._set_click_through(self.settings.click_through)
        save_overlay_settings(self.settings)

    def refresh(self) -> None:
        self.apply_settings(load_overlay_settings())

    def _process_commands(self) -> None:
        try:
            while True:
                command = self.command_queue.get_nowait()
                if command == "quit":
                    self.on_close(); self.root.quit(); return
                if command == "open_editor":
                    import webbrowser
                    webbrowser.open("http://127.0.0.1:8765/#overlay-settings")
                elif hasattr(self, command):
                    getattr(self, command)()
        except queue.Empty:
            pass
        self.root.after(100, self._process_commands)

    def _start_drag(self, event: tk.Event) -> None:
        if not self.settings.click_through:
            self._drag_origin = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())

    def _drag(self, event: tk.Event) -> None:
        if self._drag_origin:
            ex, ey, wx, wy = self._drag_origin
            x, y = wx + event.x_root - ex, wy + event.y_root - ey
            monitor = self._monitor_at(event.x_root, event.y_root)
            x, y = clamp_to_monitor(x, y, self.settings.width, self.settings.height, monitor)
            self._set_geometry(x, y, self.settings.width, self.settings.height)

    def _end_drag(self, _: tk.Event) -> None:
        if self._drag_origin:
            self.settings.x, self.settings.y = self.root.winfo_x(), self.root.winfo_y()
            self.settings.position_preset = "自由"
            save_overlay_settings(self.settings)
            self._drag_origin = None

    def _start_resize(self, event: tk.Event) -> str:
        if not self.settings.click_through:
            self._resize_origin = (event.x_root, event.y_root, self.root.winfo_width(), self.root.winfo_height())
        return "break"

    def _resize(self, event: tk.Event) -> str:
        if self._resize_origin:
            ex, ey, original_width, original_height = self._resize_origin
            monitor = self._monitor_at(self.root.winfo_x(), self.root.winfo_y())
            available_width = int(monitor["x"]) + int(monitor["width"]) - self.root.winfo_x()
            available_height = int(monitor["y"]) + int(monitor["height"]) - self.root.winfo_y()
            width = max(240, min(1600, available_width, original_width + event.x_root - ex))
            height = max(140, min(1200, available_height, original_height + event.y_root - ey))
            self.settings.width, self.settings.height = int(width), int(height)
            self._render_strategy_cards()
            self._set_geometry(self.root.winfo_x(), self.root.winfo_y(), self.settings.width, self.settings.height)
        return "break"

    def _end_resize(self, _: tk.Event) -> str:
        if self._resize_origin:
            self.settings.x, self.settings.y = self.root.winfo_x(), self.root.winfo_y()
            self.settings.position_preset = "自由"
            save_overlay_settings(self.settings)
            self._resize_origin = None
        return "break"
