# Testing

## Automated

Run `python -m compileall -q app.py backend tests`, `pytest -q`, and `node --check frontend/app.js frontend/i18n.js`. Tests cover prompt preservation, monitor clamping, JPEG-to-PNG conversion, note CRUD, overlay settings/actions, reviews, candidates, and templates. Windows wallpaper mutation is intentionally excluded from automation.

## Manual Windows matrix

- First launch and normal hidden launch; diagnostic `start.bat` launch.
- Create, edit, save, delete, restart, and verify SQLite persistence.
- Select multiple overlay notes; move, resize, change opacity, topmost, and click-through; verify saved position.
- Confirm all three click-through recovery paths: hotkey, tray, web UI.
- Test primary/secondary monitors, a monitor left of the primary, unplug/reconnect, and 100%/125%/150% scaling.
- Test Japanese text and a repository path containing Japanese characters.
- Import valid PNG/JPEG/WebP and reject a corrupt or unsupported file.
- Download backup, inspect contents, restore a disposable copy, and verify invalid ZIP rejection.
- Exit from tray and confirm the local port closes.

## Build status

The submission uses a reproducible source distribution. A PyInstaller executable is not currently produced or claimed as tested. This avoids shipping an unsigned binary and allows dependency license review—especially LGPL-3.0 `pystray`—before binary redistribution.
