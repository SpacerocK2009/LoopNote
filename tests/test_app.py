from __future__ import annotations

from pathlib import Path

from PIL import Image
from fastapi.testclient import TestClient

from app import app
from backend.database import initialize_database
from backend.models import NoteInput, PromptOptions
from backend.services.image_service import import_image
from backend.services.prompt_service import generate_prompt
from backend.desktop.memo_overlay import clamp_to_monitor


def test_public_product_name_and_generic_prompt() -> None:
    assert app.title == "LoopNote — A Desktop Practice Companion"
    note = NoteInput(title="Reaction drill", bullet_points="Watch the cue", goal="Ten repetitions")
    prompt = generate_prompt(note, PromptOptions())
    assert "Reaction drill" in prompt
    assert "copyrighted characters" in prompt
    assert "Street Fighter" not in prompt


def test_prompt_preserves_note_text() -> None:
    note = NoteInput(title="対空確認", character="ジュリ", bullet_points="・2HP → 強風破\n・ダメージ 1200", goal="3回成功")
    prompt = generate_prompt(note, PromptOptions(support_style="熱血", text_position="左", theme_color="ブラック"))
    assert "2HP → 強風破" in prompt
    assert "ダメージ 1200" in prompt
    assert "3回成功" in prompt
    assert "熱血" in prompt


def test_overlay_position_is_clamped_to_monitor() -> None:
    monitor = {"x": 0, "y": 0, "width": 1920, "height": 1080}
    assert clamp_to_monitor(50, -100, 420, 300, monitor) == (50, 0)
    assert clamp_to_monitor(1800, 1000, 420, 300, monitor) == (1500, 780)
    left_monitor = {"x": -1920, "y": 0, "width": 1920, "height": 1080}
    assert clamp_to_monitor(-2100, -20, 420, 300, left_monitor) == (-1920, 0)


def test_import_converts_jpeg_to_png(tmp_path: Path) -> None:
    initialize_database()
    source = tmp_path / "sample.jpg"
    Image.new("RGB", (32, 18), "red").save(source, "JPEG")
    result = import_image(source, "sample.jpg")
    png_name = str(result["preview_url"]).rsplit("/", 1)[-1]
    from backend.services.image_service import CURRENT_DIR
    with Image.open(CURRENT_DIR / png_name) as image:
        assert image.format == "PNG"
        assert image.size == (32, 18)


def test_note_crud_api() -> None:
    payload = {
        "title": "CRUD確認用メモ",
        "character": "リュウ",
        "category": "対空",
        "bullet_points": "・2HPを出す",
        "goal": "5回成功",
        "notes": "テスト",
        "priority": "high",
    }
    with TestClient(app) as client:
        created = client.post("/api/notes", json=payload)
        assert created.status_code == 201
        note_id = created.json()["id"]

        payload["goal"] = "10回成功"
        updated = client.put(f"/api/notes/{note_id}", json=payload)
        assert updated.status_code == 200
        assert updated.json()["goal"] == "10回成功"
        assert any(item["id"] == note_id for item in client.get("/api/notes").json())
        assert client.delete(f"/api/notes/{note_id}").status_code == 200


def test_overlay_settings_api() -> None:
    with TestClient(app) as client:
        settings = client.get("/api/overlay/settings").json()
        settings.update({
            "selected_note_ids": [],
            "opacity": 0.75,
            "click_through": False,
            "auto_start": False,
        })
        saved = client.put("/api/overlay/settings", json=settings)
        assert saved.status_code == 200
        loaded = client.get("/api/overlay/settings").json()
        assert loaded["selected_note_ids"] == []
        assert loaded["opacity"] == 0.75
        monitors = client.get("/api/overlay/monitors")
        assert monitors.status_code == 200
        assert len(monitors.json()) >= 1
        assert client.post("/api/overlay/action", json={"action": "show"}).status_code == 200
        assert client.post("/api/overlay/action", json={"action": "hide"}).status_code == 200


def test_phase3_review_candidates_and_templates() -> None:
    payload = {
        "title": "復習ロジック確認",
        "character": "舞",
        "category": "コンボ",
        "bullet_points": "4HKヒット確認",
        "goal": "1回成功",
        "notes": "",
        "priority": "high",
        "next_review_at": "2000-01-01",
        "tags": "テスト,確認",
    }
    with TestClient(app) as client:
        created = client.post("/api/notes", json=payload)
        assert created.status_code == 201
        note_id = created.json()["id"]
        assert any(n["id"] == note_id for n in client.get("/api/review/today").json())
        reviewed = client.post(f"/api/notes/{note_id}/review", json={"result": "問題なくできた", "comment": "安定"})
        assert reviewed.status_code == 200
        assert reviewed.json()["proficiency_level"] == 1
        assert reviewed.json()["interval_days"] == 3
        history = client.get(f"/api/review/history?note_id={note_id}").json()
        assert history[0]["result"] == "問題なくできた"
        assert any(t["name"] == "コンボ" for t in client.get("/api/templates").json())
        assert any(n["id"] == note_id for n in client.get("/api/candidates/wallpaper").json())
        assert client.delete(f"/api/notes/{note_id}").status_code == 200
