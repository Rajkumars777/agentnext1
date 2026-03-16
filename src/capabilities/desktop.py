"""
src/capabilities/desktop.py
===========================
NEXUS Desktop Management Capability.
Handles process detection, termination, and application launching.
"""

import psutil
import logging
from AppOpener import open as open_app_opener, close as close_app_opener
import os
import subprocess

logger = logging.getLogger(__name__)

def list_processes() -> list[dict]:
    """Returns a list of important running processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def is_running(app_name: str) -> bool:
    """Check if an application is running by name (fuzzy)."""
    app_low = app_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if app_low in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def close_app(app_name: str) -> dict:
    """Close an application by name."""
    logger.info(f"Attempting to close: {app_name}")
    closed_count = 0
    app_low = app_name.lower()
    
    # 1. Try via psutil (Graceful then Forceful)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if app_low in proc.info['name'].lower():
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 2. Try via AppOpener fallback
    try:
        close_app_opener(app_name, match_closest=True, output=False)
    except Exception as e:
        logger.warning(f"AppOpener close failed for {app_name}: {e}")

    # 3. Final fallback: taskkill
    if closed_count == 0:
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"*{app_name}*"], capture_output=True)
        except Exception:
            pass

    return {
        "success": True, 
        "message": f"Closed instances matching '{app_name}'",
        "count": closed_count
    }

def open_app(app_name: str) -> dict:
    """Open an application by name."""
    logger.info(f"Attempting to open: {app_name}")
    try:
        # AppOpener is quite good for Windows apps
        open_app_opener(app_name, match_closest=True, output=False)
        return {"success": True, "message": f"Launched '{app_name}'"}
    except Exception as e:
        logger.error(f"Failed to open {app_name}: {e}")
        return {"success": False, "message": f"Failed to launch '{app_name}': {str(e)}"}
