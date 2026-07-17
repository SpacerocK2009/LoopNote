from __future__ import annotations

from backend.models import NoteInput, PromptOptions


def generate_prompt(note: NoteInput, options: PromptOptions) -> str:
    bullets = note.bullet_points.strip() or "（未入力）"
    return f"""ストリートファイター6の練習用PC壁紙画像を作成してください。

【最重要】以下の日本語テキストは省略せず、勝手に言い換えず、そのまま正確に画像内へ記載してください。技名、数字、記号、矢印も可能な限り正確に描画してください。

タイトル：{note.title}
キャラクター：{note.character or '未指定'}
カテゴリ：{note.category or '未指定'}
練習内容：
{bullets}
今日の目標：{note.goal or '（未入力）'}
補足：{note.notes or '（なし）'}
優先度：{note.priority}

デザイン要件：
- いーきゅんがプレイヤーを「{options.support_style}」スタイルで応援している
- フルHD、16:9、1920x1080想定のPC壁紙
- 日本語テキストを大きく、読みやすく、箇条書き中心で整理する
- 文字配置は「{options.text_position}」を中心にする
- テーマカラーは「{options.theme_color}」、背景は見やすいダーク系
- 壁紙として実用的で、デスクトップアイコンを置ける十分な余白を確保する
- いーきゅんは文字に重ならず、内容の邪魔をしない位置とサイズにする
- 情報の優先順位が一目で分かり、練習中に素早く確認できるレイアウト
- Street Fighter 6の熱量を感じる、洗練されたゲームトレーニングボード風

画像内の文章を生成後に読み直し、上記テキストとの欠落・誤字・文字化けがないようにしてください。"""


def generate_candidate_prompt(notes: list[dict[str, object]], options: PromptOptions) -> str:
    sections = []
    for index, note in enumerate(notes, 1):
        sections.append(
            f"【課題 {index}】\nタイトル：{note['title']}\nキャラクター：{note['character'] or '未指定'}\n"
            f"カテゴリ：{note['category'] or '未指定'}\n内容：\n{note['bullet_points'] or '（未入力）'}\n"
            f"今日の目標：{note['goal'] or '（未入力）'}"
        )
    content = "\n\n".join(sections)
    return f"""ストリートファイター6の「今日の復習」用PC壁紙画像を作成してください。

【最重要】下記の日本語テキストを省略・言い換えせず、技名、数字、矢印を正確に記載してください。

{content}

デザイン要件：
- いーきゅんが「{options.support_style}」スタイルで応援する
- フルHD、16:9、1920x1080の実用的なPC壁紙
- 最大5課題を明確に区切り、文字配置は「{options.text_position}」中心
- テーマカラーは「{options.theme_color}」のダーク系
- 箇条書き中心で、デスクトップアイコン用の余白を確保
- いーきゅんは文字を隠さない

生成後に全テキストを照合し、欠落・誤字・文字化けを修正してください。"""
