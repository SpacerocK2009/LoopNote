# LoopNote — A Desktop Practice Companion

LoopNote keeps the practice drills you are trying to remember visible on your Windows desktop, so you can stay in the loop without reopening notes between repetitions.

> Built as a new project during OpenAI Build Week. **Target track: Apps for Your Life.**

[日本語 README](README_JA.md) · [5-minute judge guide](docs/JUDGE_GUIDE.md) · [Build Week story](docs/BUILD_WEEK.md) · [Devpost draft](docs/DEVPOST_SUBMISSION.md)

## The problem and the solution

Repeated practice breaks down when the current objective is hidden in another window. LoopNote stores structured practice notes, schedules lightweight reviews, and places up to six selected notes in a movable, always-on-top desktop overlay. It works locally and requires no account, API key, telemetry, or cloud service.

## Features

- Create, edit, search, tag, favorite, archive, and delete practice notes.
- Record four review outcomes and calculate the next review date.
- Rank wallpaper and overlay suggestions from due date, proficiency, priority, and results.
- Show selected notes in a resizable multi-monitor overlay with opacity, topmost, and click-through controls.
- Control the overlay with global hotkeys and a system-tray menu.
- Import PNG/JPEG/WebP images and apply or restore Windows wallpaper.
- Export and restore a ZIP containing SQLite data and readable settings.
- Switch the web interface between English (default) and Japanese.

## Screenshots

Screenshots are intentionally not fabricated. See [the asset checklist](docs/ASSET_CHECKLIST.md) for the exact capture list and safe framing guidance.

## Judge quick start (Windows 11)

1. Install 64-bit Python 3.11 or later with the Python launcher.
2. Clone or download this repository.
3. Double-click `launch.vbs`. First launch creates `.venv` and installs dependencies; the console stays hidden.
4. Open `http://127.0.0.1:8765` if the browser does not open automatically.
5. Create a practice note, choose it under **Desktop practice overlay**, then select **Save and apply** and **Show**.
6. Exit from the LoopNote tray icon. For diagnostics, run `start.bat` instead.

See [JUDGE_GUIDE.md](docs/JUDGE_GUIDE.md) for a five-minute walkthrough. Generic samples are in [`demo_data/practice_notes.json`](demo_data/practice_notes.json); copy their fields into the editor. Automatic JSON import is not implemented.

## Run from source

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

The local server binds only to `127.0.0.1:8765`.

## Data and privacy

Notes and settings are stored in `data/app.db`; imported images are stored under `data/wallpapers/`. Runtime data is ignored by Git. LoopNote sends no telemetry and calls no external API. The optional **Copy and open ChatGPT** action only copies a generated prompt and opens the website; the user decides whether to paste or submit it. Read [PRIVACY.md](docs/PRIVACY.md).

## Technology

Python 3.11+, FastAPI, Uvicorn, SQLite, Tkinter, Windows APIs, Pillow, pystray, screeninfo, and dependency-free HTML/CSS/JavaScript. Supported OS: Windows 11. The web API can run elsewhere, but overlay, hotkeys, autostart, and wallpaper integration are Windows-specific.

## Test and build

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app.py backend tests
```

The supported distribution for Build Week is source ZIP/clone. An unsigned executable is not committed or released: it would add Windows reputation warnings and requires careful redistribution notices for LGPL-licensed `pystray`. Reproducible source setup is documented in [TESTING.md](docs/TESTING.md).

## Built during OpenAI Build Week

The creator identified the practice-memory problem, defined the product concept and priorities, made UI/UX decisions, performed hands-on Windows checks, and retained final decision authority. Codex with GPT-5.6 supported architecture, implementation, debugging, review, automated tests, localization, and documentation. This repository does not claim that AI independently created the product. Details are in [BUILD_WEEK.md](docs/BUILD_WEEK.md).

## Known limitations

- Windows 11 only for desktop integration; unsigned source distribution requires Python.
- Overlay interaction can be hidden behind exclusive fullscreen applications; borderless window mode is recommended.
- Hotkeys may conflict with other applications.
- Backup ZIP excludes image binaries; copy `data/wallpapers/` separately for a complete backup.
- English localization covers the primary web UI; some API validation messages and legacy template values remain Japanese.
- Display scaling at 125%/150% and unusual multi-monitor layouts require manual verification.

## License

LoopNote source is licensed under the [MIT License](LICENSE). Third-party packages keep their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No game assets, logos, audio, or proprietary fonts are included.
