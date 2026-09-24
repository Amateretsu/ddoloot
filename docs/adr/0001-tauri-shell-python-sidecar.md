# Tauri shell with a Python sidecar and a web UI

DDOLoot ships as a Tauri 2 desktop app. The UI is React + Vite + TypeScript. The backend is the existing Python code, exposed as a FastAPI service on loopback (random port, per-launch token) and frozen with PyInstaller as a per-OS sidecar. The UI talks to the backend only through that HTTP API.

## Why

- Tauri is the only web-shell option with a built-in signed updater on Windows, macOS and Linux, and auto-update should be on-track from day one.
- A web UI gives the richer table and filter experience the search feature needs.
- Because the UI only speaks HTTP, it can be reused for a future hosted mode.
- Python stays the language for all catalog and data logic.

## Considered options

- **PySide6**: lowest risk and reuses `ddoloot_ui`, but weaker table/filter UX, no UI reuse for hosted mode. `ddoloot_ui` is retired once the web UI reaches parity.
- **pywebview**: all-Python, but no installer or updater; we would build both ourselves.
- **Electron**: free updater lacks Linux support; heavier.

## Consequences

- Three languages (Python, TypeScript, Rust) and Rust/Node toolchains in the repo.
- PyInstaller cannot cross-compile: one CI runner per OS.
- v1 may ship unsigned; Windows signing and macOS notarization are deferred.
