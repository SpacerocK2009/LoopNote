# Public asset checklist

## Repository audit

- [x] No game screenshots, character art, official logos, audio, or video are tracked.
- [x] No proprietary fonts are bundled; UI uses installed system fonts.
- [x] Runtime images, SQLite data, logs, backups, virtual environments, build output, `.env`, and IDE files are ignored.
- [x] Demo data uses generic English practice language and no character or move names.
- [x] Source scan found no API key, credential, email address, or Windows user path in tracked content.
- [x] Dependency licenses are summarized in `THIRD_PARTY_NOTICES.md`.

## Screenshots to capture manually

| Filename | Screen | Resolution / privacy | README placement |
|---|---|---|---|
| `docs/images/loopnote-overview.png` | Main screen with generic demo notes | 1600×900; hide browser profile, taskbar notifications, paths | After README introduction |
| `docs/images/note-editor.png` | English practice-note editor | 1400×900; generic text only | Features |
| `docs/images/desktop-overlay.png` | Overlay over a neutral app/window | 1920×1080; no game/client content | Features |
| `docs/images/overlay-settings.png` | Multi-select and display settings | 1400×900; monitor names must be generic | Judge quick start |
| `docs/images/backup-review.png` | Review result and backup controls | 1400×900; no downloaded filename path | Data and privacy |

Before publishing an image, inspect the full frame for usernames, avatars, emails, local paths, API keys, credit information, private Codex conversations, game assets, and notifications. Do not add placeholders if captures are unavailable.
