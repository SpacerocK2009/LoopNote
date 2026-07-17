from __future__ import annotations

import os
from pathlib import Path

from screeninfo import get_monitors

from backend.database import BASE_DIR
from backend.models import OverlaySettings
from backend.services.settings_service import get_setting, set_setting

SETTINGS_KEY = "overlay_settings"


def load_overlay_settings() -> OverlaySettings:
    raw = get_setting(SETTINGS_KEY, {})
    try:
        return OverlaySettings(**raw)
    except (TypeError, ValueError):
        return OverlaySettings()


def save_overlay_settings(settings: OverlaySettings) -> None:
    set_setting(SETTINGS_KEY, settings.model_dump())


def list_monitors() -> list[dict[str, object]]:
    try:
        monitors = get_monitors()
        return [
            {
                "index": index,
                "name": getattr(monitor, "name", None) or f"モニター {index + 1}",
                "x": monitor.x,
                "y": monitor.y,
                "width": monitor.width,
                "height": monitor.height,
                "primary": bool(getattr(monitor, "is_primary", index == 0)),
            }
            for index, monitor in enumerate(monitors)
        ]
    except Exception:
        return [{"index": 0, "name": "メインモニター", "x": 0, "y": 0, "width": 1920, "height": 1080, "primary": True}]


def set_auto_start(enabled: bool) -> None:
    if os.name != "nt":
        raise RuntimeError("自動起動設定はWindowsでのみ利用できます。")
    startup = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    launcher = startup / "SF6StrategyBoard.cmd"
    if enabled:
        start_bat = BASE_DIR / "start.bat"
        launcher.write_text(f'@echo off\nstart "" /min "{start_bat}"\n', encoding="utf-8")
    else:
        launcher.unlink(missing_ok=True)
