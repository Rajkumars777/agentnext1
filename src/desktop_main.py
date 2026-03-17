import os
import sys
import threading
import uvicorn
import webbrowser
import logging
import traceback
import datetime
import time

# ── Fatal logger ───────────────────────────────────────────────────────────────
# Always writes to the user's home directory so it's accessible even if the
# bundle crashes before it can create its own log folder.
def log_fatal(msg: str):
    log_path = os.path.join(os.path.expanduser("~"), "nexus_desktop_fatal.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] FATAL: {msg}\n")

# ── Path resolution ────────────────────────────────────────────────────────────
#
#   FROZEN (PyInstaller --onefile):
#     sys._MEIPASS  → temp dir where Python modules are extracted  (e.g. C:\Users\...\AppData\Local\Temp\_MEIxxxxx)
#     EXE_DIR       → folder that contains ai-engine.exe           (e.g. C:\Users\rajak\Music\AI-agent---LTID-main\dist)
#
#   DEV (plain Python):
#     MEIPASS_DIR   → src/   (where desktop_main.py lives)
#     EXE_DIR       → project root  (C:\Users\rajak\Music\AI-agent---LTID-main)
#
if getattr(sys, 'frozen', False):
    MEIPASS_DIR = sys._MEIPASS                                       # extracted python packages
    EXE_DIR     = os.path.dirname(os.path.abspath(sys.executable))  # where .exe lives
else:
    # Running as: python src/desktop_main.py  (from project root)
    MEIPASS_DIR = os.path.dirname(os.path.abspath(__file__))         # src/
    EXE_DIR     = os.path.dirname(MEIPASS_DIR)                       # project root

# Make sure Python can find our packages (api/, core/, capabilities/, main.py)
for p in [MEIPASS_DIR, os.path.join(MEIPASS_DIR, 'src')]:
    if p not in sys.path:
        sys.path.insert(0, p)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nexus.desktop")

# ── Import FastAPI app ─────────────────────────────────────────────────────────
try:
    # In bundle:  main.py is copied to _MEIPASS root  → "from main import app"
    # In dev:     main.py is at src/main.py, MEIPASS_DIR == src/ → same import works
    from main import app
    logger.info("FastAPI app imported successfully")
except ImportError as e:
    log_fatal(f"Failed to import main: {e}\nsys.path: {sys.path}")
    raise

# ── Static file mounting ───────────────────────────────────────────────────────
def _mount_static():
    """
    Mount the compiled Next.js frontend.
    Checks several candidate paths so it works in both dev and frozen modes.
    """
    from fastapi.staticfiles import StaticFiles

    candidates = [
        # Frozen: static/ copied to _MEIPASS root by the spec file
        os.path.join(MEIPASS_DIR, "static"),
        # Frozen: static/ placed next to the .exe
        os.path.join(EXE_DIR, "static"),
        # Dev: Next.js exports to frontend/out
        os.path.join(EXE_DIR, "frontend", "out"),
        # Dev: legacy path
        os.path.join(EXE_DIR, "src", "static"),
    ]

    for path in candidates:
        if os.path.exists(path):
            app.mount("/", StaticFiles(directory=path, html=True), name="static")
            logger.info(f"Serving static files from: {path}")
            return

    logger.warning("No static folder found — UI will not load. Checked:")
    for c in candidates:
        logger.warning(f"  {c}")

# ── OpenClaw gateway ───────────────────────────────────────────────────────────
def _start_gateway():
    """Start the OpenClaw gateway in a background thread (non-blocking)."""
    try:
        from core.openclaw_process import start_gateway
        result = start_gateway()
        logger.info(f"Gateway result: {result}")
    except Exception as e:
        log_fatal(f"Gateway start failed: {e}\n{traceback.format_exc()}")
        logger.error(f"Gateway failed: {e}")

# ── FastAPI / uvicorn ──────────────────────────────────────────────────────────
def _start_backend():
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            use_colors=False,
        )
    except Exception as e:
        log_fatal(f"Backend thread crashed: {e}\n{traceback.format_exc()}")
        logger.error(f"Backend crashed: {e}")

# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    try:
        logger.info(f"EXE_DIR    : {EXE_DIR}")
        logger.info(f"MEIPASS_DIR: {MEIPASS_DIR}")

        _mount_static()

        # Start gateway first (OpenClaw can take a few seconds)
        # We start this thread WITHOUT setting FAST_START yet, so it uses the full timeout
        gateway_thread = threading.Thread(target=_start_gateway, daemon=True, name="openclaw-gateway")
        gateway_thread.start()

        # NOW set FAST_START so that the backend thread (Lifespan) will skip its own 
        # redundant gateway start attempt.
        os.environ["OPENCLAW_FAST_START"] = "1"
        backend_thread = threading.Thread(target=_start_backend, daemon=True, name="uvicorn-backend")
        backend_thread.start()

        logger.info("NEXUS Desktop started → http://127.0.0.1:8000")

        # Give uvicorn a moment then open browser
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000")

        # Keep main thread alive — daemon threads die when this exits
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down NEXUS Desktop...")
    except Exception as e:
        log_fatal(f"main() crashed: {e}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
