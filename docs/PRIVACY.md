# Privacy

LoopNote is local-first. It stores practice notes, review history, settings, image metadata, and wallpaper history in `data/app.db`; imported and converted images are under `data/wallpapers/`; generated backups are under `data/backups/`.

There is no account, telemetry, analytics, advertising, external API call, or background upload. The server listens only on `127.0.0.1`. Choosing **Copy and open ChatGPT** writes a prompt to the clipboard and opens a website; LoopNote itself does not submit the prompt.

Delete individual notes in the UI. For a complete reset, exit LoopNote and remove `data/app.db`, `data/wallpapers/`, and `data/backups/`. Uninstall by disabling autostart, exiting the tray app, and deleting the project folder and any manually copied backups.
