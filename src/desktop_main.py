import os
import sys
import threading
import uvicorn
import webbrowser
from fastapi.staticfiles import StaticFiles
from src.main import app

def start_backend():
    # Run uvicorn server in a separate thread
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def main():
    # Get the directory where the bundle is located (for PyInstaller)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    static_path = os.path.join(base_path, "src", "static")
    
    if os.path.exists(static_path):
        # Mount the static files from the frontend export
        app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
        print(f"Serving static files from: {static_path}")
    else:
        print(f"Warning: Static files not found at {static_path}")

    # Start backend thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    print("NEXUS Desktop App started at http://127.0.0.1:8000")
    
    # Automatically open the browser
    webbrowser.open("http://127.0.0.1:8000")

    # Keep the main thread alive (or use a real windowing library like pywebview later)
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
