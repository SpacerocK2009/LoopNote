# Devpost submission draft

## Project name
LoopNote

## Tagline
Keep the next repetition visible and your practice loop moving.

## Inspiration
During repetitive practice, the correction that matters most is often hidden in a note, image, or another window. Reopening it interrupts the session; relying on memory makes the drill drift.

## What it does
LoopNote stores structured practice drills, schedules lightweight reviews, ranks useful next items, and displays selected notes in a movable Windows overlay. The overlay supports multiple monitors, opacity, always-on-top, click-through, hotkeys, and tray controls. Data remains local and can be backed up as ZIP.

## How we built it
The application combines FastAPI and SQLite with a dependency-free web interface. A Tkinter desktop runtime receives commands from the local API and integrates with Windows hotkeys, wallpaper APIs, startup, and the system tray.

## How Codex and GPT-5.6 were used
The creator owned the problem, concept, priorities, UI/UX choices, testing observations, and final decisions. Codex with GPT-5.6 assisted with architecture, implementation, debugging, code review, automated tests, localization, repository auditing, and submission documentation.

## Challenges we ran into
Keeping Tkinter responsive beside a local web server, handling negative multi-monitor coordinates, guaranteeing recovery from click-through mode, migrating SQLite without deleting notes, and preparing a privacy-safe public repository.

## Accomplishments that we're proud of
A practical local workflow from note creation to persistent overlay, review scheduling, smart suggestions, backup, and bilingual presentation—without an account, cloud backend, telemetry, or API key.

## What we learned
Desktop utility UX depends as much on safe escape routes, persistence, and startup behavior as it does on the main feature. Small local tools also benefit from explicit privacy and asset boundaries.

## What's next for LoopNote
A signed Windows release, demo-data import, broader accessibility/scaling tests, complete backend localization, and customizable review policies.

## Built with
Python, FastAPI, Uvicorn, SQLite, Tkinter, Windows API, Pillow, pystray, screeninfo, HTML, CSS, JavaScript, Codex, and GPT-5.6.

## Target track
Apps for Your Life

## Short description
LoopNote is a private Windows practice companion that keeps selected drills visible in a configurable desktop overlay and brings them back through lightweight review scheduling.

## Long description
LoopNote helps people sustain deliberate practice when the current objective would otherwise disappear behind another window. Users create structured notes, select up to six for an always-on-top overlay, and control the overlay without leaving their practice flow. Review outcomes update proficiency and future dates, while smart suggestions surface useful drills. Images and wallpapers are optional; ZIP backup protects the local SQLite data. LoopNote is English/Japanese, local-only, and designed for general repetitive practice rather than any specific game.
