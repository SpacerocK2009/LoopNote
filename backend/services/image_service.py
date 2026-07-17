from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from backend.database import BASE_DIR, db_connection

WALLPAPER_DIR = BASE_DIR / "data" / "wallpapers"
ORIGINALS_DIR = WALLPAPER_DIR / "originals"
CURRENT_DIR = WALLPAPER_DIR / "current"
HISTORY_DIR = WALLPAPER_DIR / "history"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_image_directories() -> None:
    for directory in (ORIGINALS_DIR, CURRENT_DIR, HISTORY_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def import_image(source_path: Path, original_name: str, note_id: int | None = None) -> dict[str, object]:
    ensure_image_directories()
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("PNG / JPG / JPEG / WebP の画像を選択してください。")

    token = uuid.uuid4().hex
    original_path = ORIGINALS_DIR / f"{token}{suffix}"
    png_path = CURRENT_DIR / f"{token}.png"
    shutil.copy2(source_path, original_path)
    try:
        with Image.open(original_path) as image:
            image.load()
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (20, 20, 24))
                background.paste(image, mask=image.getchannel("A"))
                image = background
            image.save(png_path, "PNG", optimize=True)
    except (UnidentifiedImageError, OSError) as exc:
        original_path.unlink(missing_ok=True)
        png_path.unlink(missing_ok=True)
        raise ValueError("画像を読み込めませんでした。ファイルが破損していないか確認してください。") from exc

    created_at = datetime.now(timezone.utc).isoformat()
    with db_connection() as db:
        cursor = db.execute(
            "INSERT INTO images(original_name, original_path, png_path, created_at, note_id) VALUES(?, ?, ?, ?, ?)",
            (original_name, str(original_path), str(png_path), created_at, note_id),
        )
        image_id = cursor.lastrowid
    return {"id": image_id, "original_name": original_name, "preview_url": f"/media/current/{png_path.name}", "created_at": created_at}


def get_image(image_id: int) -> Path:
    with db_connection() as db:
        row = db.execute("SELECT png_path FROM images WHERE id = ?", (image_id,)).fetchone()
    if row is None:
        raise ValueError("指定された画像が見つかりません。")
    path = Path(row["png_path"])
    if not path.is_file():
        raise ValueError("画像ファイルが見つかりません。再度取り込んでください。")
    return path
