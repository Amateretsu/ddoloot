# PROTOTYPE: Tauri + PyInstaller FastAPI sidecar (throwaway, issue #15)

Question: can a Tauri 2 shell start a PyInstaller-frozen FastAPI sidecar on loopback
(random port + token), reach it from the UI, and build/bundle on Windows, macOS, Linux?
Validation runs in `.github/workflows/spike-tauri-sidecar.yml`. Wipe me after the ticket closes.

Local: `./build-sidecar.sh && cd . && npx tauri build --debug`
