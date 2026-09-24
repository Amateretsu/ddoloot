#!/usr/bin/env bash
# Freeze the sidecar and name it with the Rust target triple, as Tauri externalBin requires.
set -euo pipefail
cd "$(dirname "$0")"
TRIPLE=$(rustc -vV | sed -n 's/host: //p')
EXT=""; case "$TRIPLE" in *windows*) EXT=".exe";; esac
python -m pip install -q fastapi uvicorn pyinstaller
python -m PyInstaller --onefile --name ddoloot-sidecar --distpath sidecar/dist --workpath sidecar/build --specpath sidecar/build sidecar/main.py
mkdir -p src-tauri/binaries
cp "sidecar/dist/ddoloot-sidecar$EXT" "src-tauri/binaries/ddoloot-sidecar-$TRIPLE$EXT"
ls -l src-tauri/binaries
