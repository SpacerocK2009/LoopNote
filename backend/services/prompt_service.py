from __future__ import annotations

from backend.models import NoteInput, PromptOptions


def generate_prompt(note: NoteInput, options: PromptOptions) -> str:
    bullets = note.bullet_points.strip() or "Not provided"
    return f"""Create a practical desktop wallpaper for a focused practice session.

IMPORTANT: Preserve the following text exactly. Do not omit or paraphrase names, numbers, symbols, or arrows.

Title: {note.title}
Subject: {note.character or 'Not specified'}
Category: {note.category or 'Not specified'}
Practice steps:
{bullets}
Target: {note.goal or 'Not provided'}
Notes: {note.notes or 'None'}
Priority: {note.priority}

Design requirements:
- Tone: {options.support_style}
- Full HD, 16:9, 1920x1080 desktop wallpaper
- Large, readable text organized around short bullet points
- Main text alignment: {options.text_position}
- Theme: {options.theme_color}, with a high-contrast dark background
- Energetic modern training-board aesthetic with abstract shapes only; no copyrighted characters, logos, or game assets
- Leave practical space for desktop icons and keep the hierarchy readable at a glance

After generation, compare every rendered line with the source text and correct omissions or spelling errors."""


def generate_candidate_prompt(notes: list[dict[str, object]], options: PromptOptions) -> str:
    sections = []
    for index, note in enumerate(notes, 1):
        sections.append(
            f"[DRILL {index}]\nTitle: {note['title']}\nSubject: {note['character'] or 'Not specified'}\n"
            f"Category: {note['category'] or 'Not specified'}\nSteps:\n{note['bullet_points'] or 'Not provided'}\n"
            f"Target: {note['goal'] or 'Not provided'}"
        )
    content = "\n\n".join(sections)
    return f"""Create a desktop wallpaper for today's practice review.

IMPORTANT: Preserve all text below exactly, including numbers, symbols, and arrows.

{content}

Design requirements:
- Full HD, 16:9, 1920x1080 practical desktop wallpaper
- Separate up to five drills clearly; main alignment: {options.text_position}
- Dark {options.theme_color} theme with an energetic, modern training-board aesthetic
- Use abstract shapes only; no copyrighted characters, logos, or game assets
- Preserve space for desktop icons

Compare all rendered text with the source and correct omissions or spelling errors."""
