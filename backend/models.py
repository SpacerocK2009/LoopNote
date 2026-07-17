from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    character: str = Field(default="", max_length=100)
    category: str = Field(default="", max_length=100)
    bullet_points: str = ""
    goal: str = ""
    notes: str = ""
    priority: Literal["low", "medium", "high"] = "medium"
    proficiency_level: int = Field(default=0, ge=0, le=3)
    last_practiced_at: str | None = None
    next_review_at: str | None = None
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    archived: bool = False
    favorite: bool = False
    tags: str = Field(default="", max_length=500)
    review_status: Literal["new", "learning", "review", "mastered"] = "new"


class PromptOptions(BaseModel):
    support_style: Literal["応援", "熱血", "落ち着き", "かわいい"] = "応援"
    text_position: Literal["左", "右", "中央"] = "右"
    theme_color: Literal["ネイビー", "ブラック", "ダークパープル", "ダークグリーン", "チャコール"] = "ネイビー"


class PromptRequest(BaseModel):
    note: NoteInput
    options: PromptOptions


class WallpaperRequest(BaseModel):
    image_id: int
    note_id: int | None = None


class ReviewInput(BaseModel):
    result: Literal["忘れていた", "少し迷った", "問題なくできた", "実戦で成功した"]
    comment: str = Field(default="", max_length=1000)


class CandidatePromptRequest(BaseModel):
    note_ids: list[int] = Field(min_length=1, max_length=5)
    options: PromptOptions


class OverlaySettings(BaseModel):
    # title/body remain readable for settings created by older versions, but the
    # overlay content is now sourced exclusively from saved strategy notes.
    overlay_title: str = Field(default="STRATEGY DECK", max_length=200)
    overlay_body: str = ""
    overlay_mode: str = Field(default="BATTLE PLAN", max_length=50)
    selected_note_ids: list[int] = Field(default_factory=list, max_length=6)
    monitor_index: int = Field(default=0, ge=0)
    position_preset: Literal["左上", "右上", "左下", "右下", "自由"] = "右上"
    x: int = 40
    y: int = 40
    width: int = Field(default=420, ge=240, le=1600)
    height: int = Field(default=300, ge=140, le=1200)
    opacity: float = Field(default=0.88, ge=0.2, le=1.0)
    always_on_top: bool = True
    click_through: bool = False
    visible: bool = False
    auto_start: bool = False
    text_size: int = Field(default=22, ge=10, le=72)
    background_color: str = Field(default="#10131c", pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str = Field(default="#f3f5ff", pattern=r"^#[0-9a-fA-F]{6}$")
    hotkeys: dict[str, str] = Field(default_factory=lambda: {
        "toggle_visible": "Ctrl+Alt+M",
        "toggle_topmost": "Ctrl+Alt+T",
        "toggle_click_through": "Ctrl+Alt+C",
        "open_editor": "Ctrl+Alt+E",
    })


class OverlayAction(BaseModel):
    action: Literal["show", "hide", "toggle_visible", "toggle_topmost", "toggle_click_through", "refresh"]
