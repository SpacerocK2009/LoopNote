from __future__ import annotations

import shutil
import tempfile
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from backend.database import db_connection
from backend.models import CandidatePromptRequest, NoteInput, OverlayAction, OverlaySettings, PromptOptions, PromptRequest, ReviewInput, WallpaperRequest
from backend.desktop.overlay_settings import list_monitors, load_overlay_settings, save_overlay_settings, set_auto_start
from backend.desktop.runtime import dispatch_overlay_command
from backend.services.image_service import get_image, import_image
from backend.services.prompt_service import generate_candidate_prompt, generate_prompt
from backend.services.review_service import candidates, dashboard, record_review, review_history
from backend.services.backup_service import create_backup, restore_backup
from backend.services.settings_service import get_setting, set_setting
from backend.services.wallpaper_service import restore_previous_wallpaper, set_wallpaper

router = APIRouter(prefix="/api")


def _note_dict(row: object) -> dict[str, object]:
    return dict(row)  # type: ignore[arg-type]


@router.get("/notes")
def list_notes(
    q: str = "", character: str = "", category: str = "", priority: str = "",
    proficiency: int | None = None, tag: str = "", favorite: bool | None = None,
    archive: str = Query("active", pattern="^(active|archived|all)$"),
) -> list[dict[str, object]]:
    clauses, params = [], []
    if q: clauses.append("(title LIKE ? OR bullet_points LIKE ? OR goal LIKE ? OR notes LIKE ?)"); params.extend([f"%{q}%"] * 4)
    if character: clauses.append("character=?"); params.append(character)
    if category: clauses.append("category=?"); params.append(category)
    if priority: clauses.append("priority=?"); params.append(priority)
    if proficiency is not None: clauses.append("proficiency_level=?"); params.append(proficiency)
    if tag: clauses.append("tags LIKE ?"); params.append(f"%{tag}%")
    if favorite is not None: clauses.append("favorite=?"); params.append(int(favorite))
    if archive != "all": clauses.append("archived=?"); params.append(int(archive == "archived"))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with db_connection() as db:
        rows = db.execute("SELECT * FROM notes" + where + " ORDER BY favorite DESC, updated_at DESC", params).fetchall()
    return [_note_dict(row) for row in rows]


@router.post("/notes", status_code=201)
def create_note(note: NoteInput) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    next_review = note.next_review_at or (date.today() + timedelta(days=1)).isoformat()
    with db_connection() as db:
        cursor = db.execute(
            """INSERT INTO notes(title, character, category, bullet_points, goal, notes, priority, created_at, updated_at,
               proficiency_level,last_practiced_at,next_review_at,success_count,failure_count,archived,favorite,tags,review_status)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (note.title,note.character,note.category,note.bullet_points,note.goal,note.notes,note.priority,now,now,
             note.proficiency_level,note.last_practiced_at,next_review,note.success_count,note.failure_count,int(note.archived),
             int(note.favorite),note.tags,note.review_status),
        )
        row = db.execute("SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _note_dict(row)


@router.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteInput) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    with db_connection() as db:
        cursor = db.execute(
            """UPDATE notes SET title=?, character=?, category=?, bullet_points=?, goal=?, notes=?, priority=?,
               proficiency_level=?,last_practiced_at=?,next_review_at=COALESCE(?,next_review_at),success_count=?,failure_count=?,archived=?,favorite=?,
               tags=?,review_status=?,updated_at=?
               WHERE id=?""",
            (note.title,note.character,note.category,note.bullet_points,note.goal,note.notes,note.priority,note.proficiency_level,
             note.last_practiced_at,note.next_review_at,note.success_count,note.failure_count,int(note.archived),int(note.favorite),
             note.tags,note.review_status,now,note_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "メモが見つかりません。")
        row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return _note_dict(row)


@router.delete("/notes/{note_id}")
def delete_note(note_id: int) -> dict[str, str]:
    with db_connection() as db:
        cursor = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cursor.rowcount == 0:
        raise HTTPException(404, "メモが見つかりません。")
    return {"message": "メモを削除しました。"}


@router.get("/settings/prompt")
def get_prompt_options() -> PromptOptions:
    return PromptOptions(**get_setting("prompt_options", {}))


@router.post("/prompt")
def create_prompt(request: PromptRequest) -> dict[str, str]:
    set_setting("prompt_options", request.options.model_dump())
    return {"prompt": generate_prompt(request.note, request.options)}


@router.post("/prompt/candidates")
def create_candidate_prompt(request: CandidatePromptRequest) -> dict[str, str]:
    placeholders = ",".join("?" for _ in request.note_ids)
    with db_connection() as db:
        rows = db.execute(f"SELECT * FROM notes WHERE id IN ({placeholders})", request.note_ids).fetchall()
    by_id = {row["id"]: dict(row) for row in rows}
    ordered = [by_id[note_id] for note_id in request.note_ids if note_id in by_id]
    if not ordered: raise HTTPException(404, "候補メモが見つかりません。")
    set_setting("prompt_options", request.options.model_dump())
    return {"prompt": generate_candidate_prompt(ordered, request.options)}


@router.post("/images", status_code=201)
def upload_image(file: UploadFile = File(...), note_id: int | None = None) -> dict[str, object]:
    filename = Path(file.filename or "upload").name
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temporary:
            shutil.copyfileobj(file.file, temporary)
            temp_path = Path(temporary.name)
        return import_image(temp_path, filename, note_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(500, f"画像を保存できませんでした: {exc}") from exc
    finally:
        file.file.close()
        if "temp_path" in locals():
            temp_path.unlink(missing_ok=True)


@router.post("/wallpaper")
def apply_wallpaper(request: WallpaperRequest) -> dict[str, str]:
    try:
        path = get_image(request.image_id)
        message = set_wallpaper(path)
        with db_connection() as db:
            db.execute("INSERT INTO wallpaper_history(image_id,note_id,image_path,set_at) VALUES(?,?,?,?)",
                       (request.image_id,request.note_id,str(path),datetime.now(timezone.utc).isoformat()))
        return {"message": message}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(500, str(exc)) from exc


@router.post("/wallpaper/restore")
def restore_wallpaper() -> dict[str, str]:
    try:
        return {"message": restore_previous_wallpaper()}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(500, str(exc)) from exc


@router.get("/overlay/settings")
def get_overlay_settings() -> OverlaySettings:
    return load_overlay_settings()


@router.put("/overlay/settings")
def update_overlay_settings(settings: OverlaySettings) -> dict[str, object]:
    settings.selected_note_ids = list(dict.fromkeys(settings.selected_note_ids))
    if settings.selected_note_ids:
        placeholders = ",".join("?" for _ in settings.selected_note_ids)
        with db_connection() as db:
            found = {row["id"] for row in db.execute(
                f"SELECT id FROM notes WHERE archived=0 AND id IN ({placeholders})", settings.selected_note_ids
            ).fetchall()}
        if any(note_id not in found for note_id in settings.selected_note_ids):
            raise HTTPException(400, "選択した戦略メモの一部が見つかりません。")
    previous = load_overlay_settings()
    if previous.auto_start != settings.auto_start:
        try:
            set_auto_start(settings.auto_start)
        except (OSError, RuntimeError, KeyError) as exc:
            raise HTTPException(400, f"自動起動設定を変更できませんでした: {exc}") from exc
    save_overlay_settings(settings)
    running = dispatch_overlay_command("refresh")
    return {"message": "常駐メモ設定を保存しました。", "desktop_running": running}


@router.get("/overlay/monitors")
def get_overlay_monitors() -> list[dict[str, object]]:
    return list_monitors()


@router.post("/overlay/action")
def overlay_action(request: OverlayAction) -> dict[str, object]:
    settings = load_overlay_settings()
    if request.action == "show": settings.visible = True
    elif request.action == "hide": settings.visible = False
    elif request.action == "toggle_visible": settings.visible = not settings.visible
    elif request.action == "toggle_topmost": settings.always_on_top = not settings.always_on_top
    elif request.action == "toggle_click_through": settings.click_through = not settings.click_through
    save_overlay_settings(settings)
    running = dispatch_overlay_command("refresh")
    message = "常駐メモを更新しました。" if running else "設定を保存しました。デスクトップ機能は次回通常起動時に反映されます。"
    return {"message": message, "settings": settings.model_dump(), "desktop_running": running}


@router.get("/review/dashboard")
def review_dashboard() -> dict[str, int]: return dashboard()


@router.get("/review/today")
def today_review() -> list[dict[str, object]]:
    today = date.today().isoformat()
    with db_connection() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM notes WHERE archived=0 AND next_review_at<=? ORDER BY next_review_at, priority='high' DESC", (today,)
        ).fetchall()]


@router.post("/notes/{note_id}/review")
def submit_review(note_id: int, review: ReviewInput) -> dict[str, object]:
    try: return record_review(note_id, review.result, review.comment)
    except ValueError as exc: raise HTTPException(404, str(exc)) from exc


@router.get("/review/history")
def get_review_history(note_id: int | None = None) -> list[dict[str, object]]: return review_history(note_id)


@router.get("/candidates/wallpaper")
def wallpaper_candidates() -> list[dict[str, object]]: return candidates(5)


@router.get("/candidates/overlay")
def overlay_candidates() -> list[dict[str, object]]: return candidates(3, compact=True)


@router.get("/templates")
def list_templates() -> list[dict[str, object]]:
    with db_connection() as db: return [dict(row) for row in db.execute("SELECT * FROM templates ORDER BY id").fetchall()]


@router.get("/images/history")
def image_history() -> list[dict[str, object]]:
    with db_connection() as db:
        rows = db.execute("""SELECT i.*,n.title note_title FROM images i LEFT JOIN notes n ON n.id=i.note_id
                           ORDER BY i.created_at DESC LIMIT 200""").fetchall()
    return [dict(row) | {"preview_url": f"/media/current/{Path(row['png_path']).name}"} for row in rows]


@router.get("/wallpaper/history")
def get_wallpaper_history() -> list[dict[str, object]]:
    with db_connection() as db:
        rows = db.execute("""SELECT h.*,n.title note_title FROM wallpaper_history h LEFT JOIN notes n ON n.id=h.note_id
                           ORDER BY h.set_at DESC LIMIT 200""").fetchall()
    return [dict(row) | {"preview_url": f"/media/current/{Path(row['image_path']).name}"} for row in rows]


@router.post("/wallpaper/history/{history_id}/apply")
def reapply_wallpaper(history_id: int) -> dict[str, str]:
    with db_connection() as db: row = db.execute("SELECT * FROM wallpaper_history WHERE id=?", (history_id,)).fetchone()
    if row is None: raise HTTPException(404, "壁紙履歴が見つかりません。")
    try:
        message = set_wallpaper(Path(row["image_path"]))
        with db_connection() as db: db.execute("INSERT INTO wallpaper_history(image_id,note_id,image_path,set_at) VALUES(?,?,?,?)", (row["image_id"],row["note_id"],row["image_path"],datetime.now(timezone.utc).isoformat()))
        return {"message": message}
    except (ValueError,RuntimeError,OSError) as exc: raise HTTPException(400, str(exc)) from exc


@router.post("/wallpaper/history/{history_id}/favorite")
def favorite_wallpaper(history_id: int) -> dict[str, str]:
    with db_connection() as db:
        row=db.execute("SELECT favorite FROM wallpaper_history WHERE id=?",(history_id,)).fetchone()
        if row is None: raise HTTPException(404,"壁紙履歴が見つかりません。")
        db.execute("UPDATE wallpaper_history SET favorite=? WHERE id=?",(0 if row["favorite"] else 1,history_id))
    return {"message":"お気に入りを更新しました。"}


@router.get("/backup")
def download_backup() -> FileResponse:
    path=create_backup(); return FileResponse(path,filename=path.name,media_type="application/zip")


@router.post("/backup/restore")
def upload_backup(file: UploadFile = File(...)) -> dict[str,str]:
    if not (file.filename or "").lower().endswith(".zip"): raise HTTPException(400,"ZIPバックアップを選択してください。")
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".zip") as temporary:
            shutil.copyfileobj(file.file,temporary); path=Path(temporary.name)
        restore_backup(path); return {"message":"バックアップを復元しました。画面を再読み込みしてください。"}
    except (ValueError,OSError,zipfile.BadZipFile) as exc: raise HTTPException(400,str(exc)) from exc
    finally:
        file.file.close()
        if "path" in locals(): path.unlink(missing_ok=True)
