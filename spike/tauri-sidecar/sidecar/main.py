"""PROTOTYPE sidecar: FastAPI on loopback, random port, bearer token from env."""
import os, socket, sys, threading
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

TOKEN = os.environ.get("DDOLOOT_TOKEN", "")
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["tauri://localhost", "http://tauri.localhost", "https://tauri.localhost"],
                   allow_headers=["Authorization"], allow_methods=["*"])

def _exit_when_parent_dies():
    sys.stdin.read()  # blocks; returns EOF when the Tauri parent (and its pipe) is gone
    os._exit(0)

def auth(authorization: str = Header(default="")):
    if not TOKEN or authorization != f"Bearer {TOKEN}":
        raise HTTPException(401)

@app.get("/api/v1/health", dependencies=[Depends(auth)])
def health():
    if os.environ.get("SPIKE_REPORT"):
        with open(os.environ["SPIKE_REPORT"], "a") as f:
            f.write("health-ok\n")
    return {"ok": True, "platform": sys.platform, "frozen": getattr(sys, "frozen", False)}

if __name__ == "__main__":
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    print(f"PORT={port}", flush=True)
    threading.Thread(target=_exit_when_parent_dies, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
