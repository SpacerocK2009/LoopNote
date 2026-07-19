from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with db_connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                character TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '',
                bullet_points TEXT NOT NULL DEFAULT '',
                goal TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low', 'medium', 'high')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name TEXT NOT NULL,
                original_path TEXT NOT NULL,
                png_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                reviewed_at TEXT NOT NULL,
                result TEXT NOT NULL,
                comment TEXT NOT NULL DEFAULT '',
                previous_proficiency INTEGER NOT NULL DEFAULT 0,
                new_proficiency INTEGER NOT NULL DEFAULT 0,
                next_review_at TEXT NOT NULL,
                FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wallpaper_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                note_id INTEGER,
                image_path TEXT NOT NULL,
                set_at TEXT NOT NULL,
                favorite INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE SET NULL,
                FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                bullet_points TEXT NOT NULL,
                goal TEXT NOT NULL DEFAULT ''
            );
            """
        )
        _upgrade_schema(db)
        _seed_templates(db)


def _upgrade_schema(db: sqlite3.Connection) -> None:
    note_columns = {row["name"] for row in db.execute("PRAGMA table_info(notes)")}
    additions = {
        "proficiency_level": "INTEGER NOT NULL DEFAULT 0",
        "last_practiced_at": "TEXT",
        "next_review_at": "TEXT",
        "success_count": "INTEGER NOT NULL DEFAULT 0",
        "failure_count": "INTEGER NOT NULL DEFAULT 0",
        "archived": "INTEGER NOT NULL DEFAULT 0",
        "favorite": "INTEGER NOT NULL DEFAULT 0",
        "tags": "TEXT NOT NULL DEFAULT ''",
        "review_status": "TEXT NOT NULL DEFAULT 'new'",
    }
    for name, definition in additions.items():
        if name not in note_columns:
            db.execute(f"ALTER TABLE notes ADD COLUMN {name} {definition}")
    db.execute(
        "UPDATE notes SET next_review_at = date(substr(created_at, 1, 10), '+1 day') "
        "WHERE next_review_at IS NULL OR next_review_at = ''"
    )

    image_columns = {row["name"] for row in db.execute("PRAGMA table_info(images)")}
    if "note_id" not in image_columns:
        db.execute("ALTER TABLE images ADD COLUMN note_id INTEGER")
    if "favorite" not in image_columns:
        db.execute("ALTER TABLE images ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0")


def _seed_templates(db: sqlite3.Connection) -> None:
    templates = [
        ("Reaction drill", "Reaction", "Trigger:\nResponse:\nSuccess condition:\nCommon mistake:", "Ten clean repetitions"),
        ("Timing practice", "Timing", "Setup:\nTiming cue:\nAction:\nRecovery:", "Complete five in a row"),
        ("Defensive response", "Defense", "Situation:\nPrimary response:\nFallback:\nReview point:", "Choose the response without hesitation"),
        ("コンボ", "コンボ", "開始条件：\n入力：\n締め：\n使う場面：\n次の起き攻め：", "安定して出せたら成功"),
        ("セットプレイ", "セットプレイ", "始動条件：\n重ねる技：\nヒット時：\nガード時：\n暴れ対応：", "状況別に迷わず選ぶ"),
        ("キャラ対策", "キャラ対策", "警戒技：\n確定反撃：\n意識ポイント：", "対戦中に1つ実行する"),
        ("実戦課題", "実戦課題", "今日意識すること：\nやらないこと：\n成功条件：", "1回できたら成功"),
    ]
    db.executemany(
        "INSERT OR IGNORE INTO templates(name, category, bullet_points, goal) VALUES(?, ?, ?, ?)", templates
    )
