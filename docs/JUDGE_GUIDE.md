# Five-minute judge guide

## Requirements

Windows 11, 64-bit Python 3.11+, internet access for first dependency installation, and a normal desktop session. No API key or account is required.

## Walkthrough

1. Download/clone the repository and double-click `launch.vbs`. If setup fails, run `start.bat` to see diagnostics.
2. In the web UI, select **EN**. Create a note such as “Reaction practice,” enter two short steps and “Ten successful repetitions,” then save.
3. Under **Desktop practice overlay**, select the saved note, enable **Always on top**, save, and click **Show**.
4. Drag the overlay, resize it from the lower-right handle, and change opacity. Save and refresh to confirm persistence.
5. Use `Ctrl+Alt+M` to hide/show. If click-through is enabled, recover with `Ctrl+Alt+C`.
6. Record a result in **Today’s review** and observe the next review date and proficiency update.
7. Download a backup ZIP. It contains `app.db` and `settings.json`; image binaries are intentionally excluded. Restore only a disposable backup during judging because restore replaces the current database.
8. Exit from the LoopNote tray icon.

Generic source examples are in `demo_data/practice_notes.json`; there is no automatic JSON importer. Exclusive fullscreen software can cover the overlay, so use a borderless/windowed app for the demo. If a hotkey is unavailable, use the tray menu or web controls.
