from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from backend.database import db_connection

INTERVALS = (1, 3, 7, 14, 30)
RESULTS = ("忘れていた", "少し迷った", "問題なくできた", "実戦で成功した")


def record_review(note_id: int, result: str, comment: str = "") -> dict[str, object]:
    if result not in RESULTS:
        raise ValueError("復習結果が正しくありません。")
    now = datetime.now(timezone.utc)
    with db_connection() as db:
        note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if note is None:
            raise ValueError("メモが見つかりません。")
        review_count = db.execute("SELECT COUNT(*) FROM review_history WHERE note_id = ?", (note_id,)).fetchone()[0]
        old_level = int(note["proficiency_level"])
        standard = INTERVALS[min(review_count + 1, len(INTERVALS) - 1)]
        if result == "忘れていた":
            days, level, success_delta, failure_delta = 1, max(0, old_level - 1), 0, 1
        elif result == "少し迷った":
            days, level, success_delta, failure_delta = max(2, standard // 2), old_level, 0, 1
        elif result == "問題なくできた":
            days, level, success_delta, failure_delta = standard, min(3, old_level + 1), 1, 0
        else:
            days, level, success_delta, failure_delta = min(60, standard * 2), min(3, old_level + 1), 1, 0
        next_review = (now.date() + timedelta(days=days)).isoformat()
        status = "mastered" if level == 3 else ("review" if level == 2 else "learning")
        db.execute(
            """UPDATE notes SET proficiency_level=?, last_practiced_at=?, next_review_at=?,
               success_count=success_count+?, failure_count=failure_count+?, review_status=?, updated_at=? WHERE id=?""",
            (level, now.isoformat(), next_review, success_delta, failure_delta, status, now.isoformat(), note_id),
        )
        db.execute(
            """INSERT INTO review_history(note_id, reviewed_at, result, comment, previous_proficiency,
               new_proficiency, next_review_at) VALUES(?, ?, ?, ?, ?, ?, ?)""",
            (note_id, now.isoformat(), result, comment, old_level, level, next_review),
        )
    return {"note_id": note_id, "proficiency_level": level, "next_review_at": next_review, "review_status": status, "interval_days": days}


def dashboard() -> dict[str, int]:
    today = date.today().isoformat()
    with db_connection() as db:
        row = db.execute(
            """SELECT
              SUM(CASE WHEN archived=0 AND next_review_at<=? THEN 1 ELSE 0 END) due,
              SUM(CASE WHEN archived=0 AND review_status='new' THEN 1 ELSE 0 END) new_count,
              SUM(CASE WHEN archived=0 AND review_status IN ('learning','review') THEN 1 ELSE 0 END) active,
              SUM(CASE WHEN archived=0 AND next_review_at<? THEN 1 ELSE 0 END) overdue
              FROM notes""", (today, today)
        ).fetchone()
    return {"due": row["due"] or 0, "new": row["new_count"] or 0, "active": row["active"] or 0, "overdue": row["overdue"] or 0}


def candidates(limit: int, compact: bool = False) -> list[dict[str, object]]:
    today = date.today().isoformat()
    with db_connection() as db:
        rows = db.execute("SELECT * FROM notes WHERE archived=0").fetchall()
    scored: list[tuple[int, dict[str, object]]] = []
    priority_score = {"high": 35, "medium": 18, "low": 5}
    for row in rows:
        item = dict(row)
        due = str(item["next_review_at"] or today) <= today
        score = (55 if due else 0) + (3 - int(item["proficiency_level"])) * 18
        score += priority_score.get(str(item["priority"]), 0)
        score += min(25, max(0, int(item["failure_count"]) - int(item["success_count"])) * 5)
        score += 8 if item["favorite"] else 0
        if compact and len(str(item["bullet_points"])) > 600:
            score -= 12
        scored.append((score, item))
    return [item | {"candidate_score": score} for score, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]]


def review_history(note_id: int | None = None) -> list[dict[str, object]]:
    query = "SELECT h.*, n.title note_title FROM review_history h JOIN notes n ON n.id=h.note_id"
    params: tuple[object, ...] = ()
    if note_id is not None:
        query += " WHERE h.note_id=?"; params = (note_id,)
    query += " ORDER BY h.reviewed_at DESC LIMIT 200"
    with db_connection() as db:
        return [dict(row) for row in db.execute(query, params).fetchall()]
