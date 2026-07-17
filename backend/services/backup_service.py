from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from backend.database import BASE_DIR, DB_PATH, db_connection, initialize_database

BACKUP_DIR = BASE_DIR / "data" / "backups"


def create_backup() -> Path:
    initialize_database()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = BACKUP_DIR / f"sf6_strategy_backup_{stamp}.zip"
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        db_copy = temp_dir / "app.db"
        source = sqlite3.connect(DB_PATH)
        target = sqlite3.connect(db_copy)
        try: source.backup(target)
        finally: source.close(); target.close()
        with db_connection() as db:
            settings = {row["key"]: json.loads(row["value"]) for row in db.execute("SELECT key,value FROM settings")}
        (temp_dir / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
        (temp_dir / "README.txt").write_text("SF6 Strategy Board backup. Images are not included.\n", encoding="utf-8")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for file in temp_dir.iterdir(): bundle.write(file, file.name)
    return archive


def restore_backup(archive: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        if "app.db" not in names or any(".." in Path(name).parts for name in names):
            raise ValueError("有効なバックアップファイルではありません。")
        with tempfile.TemporaryDirectory() as temp:
            bundle.extract("app.db", temp)
            restored = Path(temp) / "app.db"
            check = sqlite3.connect(restored)
            try:
                if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("バックアップDBの整合性確認に失敗しました。")
            finally: check.close()
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(restored, DB_PATH)
    initialize_database()
