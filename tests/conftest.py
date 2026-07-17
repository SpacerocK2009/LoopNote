from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    """Keep automated tests completely separate from the user's live database and images."""
    from backend import database
    from backend.services import image_service

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "app.db")
    wallpaper_dir = tmp_path / "wallpapers"
    monkeypatch.setattr(image_service, "WALLPAPER_DIR", wallpaper_dir)
    monkeypatch.setattr(image_service, "ORIGINALS_DIR", wallpaper_dir / "originals")
    monkeypatch.setattr(image_service, "CURRENT_DIR", wallpaper_dir / "current")
    monkeypatch.setattr(image_service, "HISTORY_DIR", wallpaper_dir / "history")
    database.initialize_database()
