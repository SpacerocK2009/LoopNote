from __future__ import annotations

import ctypes
import os
import shutil
from datetime import datetime
from pathlib import Path

from backend.services.image_service import HISTORY_DIR, ensure_image_directories
from backend.services.settings_service import delete_setting, get_setting, set_setting

SPI_GETDESKWALLPAPER = 0x0073
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x0001
SPIF_SENDCHANGE = 0x0002


def _require_windows() -> None:
    if os.name != "nt":
        raise RuntimeError("壁紙設定は Windows 11 でのみ利用できます。")


def get_current_wallpaper() -> Path | None:
    _require_windows()
    buffer = ctypes.create_unicode_buffer(32768)
    ok = ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, len(buffer), buffer, 0)
    if not ok or not buffer.value:
        return None
    return Path(buffer.value)


def _apply_wallpaper(path: Path) -> None:
    ok = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, str(path.resolve()), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if not ok:
        error_code = ctypes.get_last_error()
        raise OSError(error_code, "Windows が壁紙を設定できませんでした。")


def set_wallpaper(path: Path) -> str:
    _require_windows()
    ensure_image_directories()
    current = get_current_wallpaper()
    if current and current.is_file() and current.resolve() != path.resolve():
        suffix = current.suffix or ".img"
        backup = HISTORY_DIR / f"wallpaper_{datetime.now():%Y%m%d_%H%M%S_%f}{suffix}"
        try:
            shutil.copy2(current, backup)
            set_setting("previous_wallpaper_backup", str(backup))
        except OSError as exc:
            raise OSError(f"現在の壁紙をバックアップできませんでした: {exc}") from exc
    _apply_wallpaper(path)
    return "壁紙を設定しました。"


def restore_previous_wallpaper() -> str:
    _require_windows()
    raw_path = get_setting("previous_wallpaper_backup")
    if not raw_path:
        raise ValueError("戻せる壁紙のバックアップがありません。")
    backup = Path(raw_path)
    if not backup.is_file():
        delete_setting("previous_wallpaper_backup")
        raise ValueError("バックアップ画像が見つかりません。")
    _apply_wallpaper(backup)
    delete_setting("previous_wallpaper_backup")
    return "前の壁紙に戻しました。"

