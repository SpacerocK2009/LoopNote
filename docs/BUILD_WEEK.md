# OpenAI Build Week

LoopNote was started as a new project during OpenAI Build Week, not as a retrofit of an earlier product. The trigger was a personal problem: during repetitive practice, the current objective was easy to forget and reopening a note or image repeatedly broke concentration.

The work progressed from a local CRUD note board, to image and wallpaper support, to a native Windows overlay, and then to review scheduling, suggestions, history, backup, localization, and submission hardening. The current Git history begins with the first consolidated working application; it does not claim to reconstruct earlier conversations or artificial dates.

The creator selected the problem, product concept, feature order, Windows-first scope, overlay behavior, visual direction, and acceptance criteria, then performed practical checks and made final decisions. Codex with GPT-5.6 assisted with architecture, implementation, debugging, review, tests, localization, repository auditing, and documentation.

Key technical challenges included coordinating FastAPI with a Tkinter desktop runtime, negative coordinates across monitors, safe recovery from click-through mode, schema upgrades without deleting notes, and keeping user data out of Git. The result is a local practice loop that can remain visible without a cloud account.

Limitations remain: source-based setup needs Python and internet access on first install; exclusive fullscreen apps can cover the overlay; global hotkeys can conflict; display scaling and unusual monitor layouts need manual tests; backup ZIPs omit image binaries; and no signed installer is currently shipped.

Next steps include a signed Windows release, first-class demo-data import, broader accessibility testing, complete localization of API messages, and more flexible spaced-practice policies.
