# LoopNote — A Desktop Practice Companion

LoopNoteは、反復練習で「今やること」をWindowsデスクトップに表示し、メモを開き直す中断を減らすローカル練習支援ツールです。OpenAI Build Week期間中に新規開発しました。応募カテゴリの第一候補は「Apps for Your Life」です。

[English README](README.md) · [審査員向けガイド](docs/JUDGE_GUIDE.md) · [開発記録](docs/BUILD_WEEK.md)

## 主な機能

- 練習メモの作成、編集、検索、タグ、お気に入り、アーカイブ、削除
- 復習結果に応じた次回復習日の計算と候補の自動選出
- 最大6件を選べる、移動・リサイズ可能な常時最前面オーバーレイ
- 透明度、クリック透過、複数モニター、ホットキー、タスクトレイ
- 画像取り込み、Windows壁紙の設定・復元、履歴
- SQLiteと設定のZIPバックアップ・復元
- Web画面の英語（既定）／日本語切替

## Windows 11で試す

1. Python 3.11以上の64-bit版をインストールします。
2. リポジトリをダウンロードまたはcloneします。
3. `launch.vbs`をダブルクリックします。初回は仮想環境と依存関係を準備します。
4. 練習メモを保存し、「常駐メモ」で選択して「設定を保存・反映」「表示」を押します。
5. 終了はLoopNoteのタスクトレイアイコンから行います。問題調査時は`start.bat`を使います。

汎用サンプルは[`demo_data/practice_notes.json`](demo_data/practice_notes.json)にあります。JSON自動取込は未実装なので、エディターへ転記してください。

## データとプライバシー

メモと設定は`data/app.db`、画像は`data/wallpapers/`へ保存されます。外部API、テレメトリ、アカウントはありません。「ChatGPTを開く」はプロンプトをクリップボードへコピーしてWebサイトを開くだけで、送信はユーザー操作です。

## 技術・テスト

Python、FastAPI、SQLite、Tkinter、Windows API、HTML/CSS/JavaScriptを使用します。

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Build Week提出物はソース配布です。署名のない実行ファイルによる警告と、`pystray`のLGPL再配布条件を慎重に扱うため、バイナリはリポジトリへ含めません。既知の制限、作者とCodex with GPT-5.6の役割分担、詳細な手順は[英語README](README.md)と[`docs/`](docs/)を参照してください。

## ライセンス

本体は[MIT License](LICENSE)です。依存ライブラリには個別のライセンスが適用されます。第三者のゲーム画像、ロゴ、音声、専用フォントは含みません。
