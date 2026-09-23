# Cross-platform desktop stack options for a Python-first DDOLoot app

Research for issue #9 (part of map #6). Terms follow `CONTEXT.md`. Findings are from first-party docs fetched 2026-09-23; anything not verified is marked **unverified**.

## Candidates

1. **PySide6 + PyInstaller** (native Qt widgets, all Python; existing `src/ddoloot_ui/` is this).
2. **Tauri + web UI + bundled Python sidecar** (PyInstaller-frozen core).
3. **Electron + web UI + bundled Python core.**
4. **pywebview + Python** (native webview window, JS-to-Python bridge, all Python).
5. **BeeWare Briefcase** (packaging tool, pairs with Toga or others).

## Verified facts by source

### PyInstaller (packaging for 1, 2, 3, 4)
- No cross-compilation: output is specific to the OS and Python version it was built on, so CI needs one runner per OS/arch. [operating-mode](https://pyinstaller.org/en/stable/operating-mode.html)
- One-folder is faster to start; one-file is a single executable but slower and extracts to temp `_MEI*` folders (left behind on crash). Linux one-file fails if `/tmp` is noexec. Same page.
- Linux: system libraries are not bundled, assumed present. Same page.

### Tauri
- Uses the system webview, not a bundled browser; "a minimal Tauri app can be less than 600KB". [start](https://v2.tauri.app/start/)
- Linux formats: AppImage, deb, rpm, Flatpak, Snap, AUR; macOS DMG; Windows via Store or installers. [distribute](https://v2.tauri.app/distribute/)
- Python is not native: bundle as an `externalBin` sidecar named per target triple; the naming helper does not work cross-arch. [sidecar](https://v2.tauri.app/develop/sidecar/)
- Updater: built in, works on Windows/Linux/macOS; update signatures are mandatory, and losing the private key permanently blocks updates to existing installs. [updater](https://v2.tauri.app/plugin/updater/)
- macOS: notarization needs a paid Apple Developer account ($99/yr) and Apple hardware; required with Developer ID certs. [macOS signing](https://v2.tauri.app/distribute/sign/macos/)
- Windows: signing avoids SmartScreen warnings; EV certs no longer confer instant reputation; options are OV cert, Azure Key Vault, Azure Artifact Signing; reputation accrues per certificate. [Windows signing](https://v2.tauri.app/distribute/sign/windows/)

### Electron
- Update options: static storage, update.electronjs.org (macOS/Windows only, public GitHub repo with Releases, macOS builds must be signed), or custom servers. Linux is not covered by the free service. [updates](https://www.electronjs.org/docs/latest/tutorial/updates)
- Bundled Chromium size and installer details: **unverified** (fetch failed; commonly ~100 MB+ but not confirmed here).

### pywebview
- Native webview wrapper for Windows (WinForms), macOS (Cocoa), Linux (GTK or Qt); two-way JS/Python bridge; built-in HTTP server; stays small when frozen. [pywebview](https://pywebview.flowrl.com/guide/)
- Installer/updater: none provided; relies on PyInstaller plus a hand-rolled updater (inference).

### Briefcase
- Supports Linux (AppImage, Flatpak, system packages), macOS app bundles, Windows app formats; support levels vary by host/arch and format. [platforms](https://briefcase.beeware.org/en/stable/reference/platforms/index.html)
- Auto-update: not documented there; **unverified**.

### PySide6
- Deployment docs and LGPL specifics could not be retrieved (pages 404 or empty). **Unverified:** pyside6-deploy behaviour, installer sizes, LGPL obligations. Follow up before deciding.

## Comparison (facts above plus labelled inference)

| Criterion | PySide6 + PyInstaller | Tauri + Python sidecar | Electron + Python | pywebview + PyInstaller |
|---|---|---|---|---|
| Python-first | Full | Core only; shell is Rust + JS | Core only; shell is JS | Full |
| Extra toolchains | none | Rust + Node | Node | Node (if SPA) |
| Installer size | Qt is large (unverified) | Small shell + frozen Python | Bundled Chromium (unverified) | Small shell + frozen Python |
| Built-in updater | No (roll own or Qt IFW, unverified) | Yes, signed, all 3 OS | Yes, mac/Win; Linux weaker | No |
| Data-table/filter UX | Adequate (QTableView), more code for rich filters (inference) | Full web ecosystem | Full web ecosystem | Full web ecosystem |
| Hosted-mode reuse | Core reusable; UI not | Web UI reusable as-is | Web UI reusable as-is | Web UI reusable as-is |
| Non-technical install | Installer per OS | Installer per OS | Installer per OS | Installer per OS |

Common to all: per-OS CI runners (PyInstaller has no cross-compile), macOS notarization costs $99/yr and needs a Mac, Windows signing needed to avoid SmartScreen warnings.

## Observations for the decision

- The "browser-based local app is ruled out" constraint (map #6) does not exclude embedded-webview shells, since these are installed apps; the map owner should confirm.
- Web-UI options make a future hosted mode cheapest (UI reused); the Python core would need an HTTP/IPC boundary, which pywebview gives for free.
- pywebview is the only web-UI option that stays entirely Python, but has no updater and least ecosystem support (inference from docs).
- PySide6 is the lowest-risk path if reusing `ddoloot_ui`, but data-table UX and hosted reuse are weaker.
- Catalog updates come from the public GitHub repo, so app-update needs are modest: catalog sync can be independent of app self-update.

## Gaps to close before deciding

PySide6 deploy/LGPL docs; Electron installer sizes; Briefcase updater; measured installer sizes of a spike per candidate.
