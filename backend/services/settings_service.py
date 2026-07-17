from __future__ import annotations

import json
from typing import Any

from backend.database import db_connection


def get_setting(key: str, default: Any = None) -> Any:
    with db_connection() as db:
        row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    try:
        return json.loads(row["value"])
    except json.JSONDecodeError:
        return row["value"]


def set_setting(key: str, value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False)
    with db_connection() as db:
        db.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, encoded),
        )


def delete_setting(key: str) -> None:
    with db_connection() as db:
        db.execute("DELETE FROM settings WHERE key = ?", (key,))

