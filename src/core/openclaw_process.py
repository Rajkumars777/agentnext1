"""
openclaw_process.py
===================
Manages the OpenClaw gateway as a child process.
Starts `openclaw gateway --port 18789` in the background,
monitors its output, and captures QR codes for channel pairing.
"""

import subprocess
import threading
import os
import json
import logging
import time
import re

logger = logging.getLogger(__name__)

# ─── State ────────────────────────────────────────────────────────────────────

_process: subprocess.Popen | None = None
_gateway_port: int = 18789
_gateway_log: list[str] = []
_qr_data: str | None = None          # latest QR code string from openclaw output
_status: str = "stopped"              # stopped | starting | running | error
_openclaw_home: str = ""

MAX_LOG_LINES = 200


def _get_openclaw_home() -> str:
    """Return path to .openclaw directory — check user home first, then project."""
    global _openclaw_home
    if _openclaw_home:
        return _openclaw_home

    # Priority 1: project-level .openclaw
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_path = os.path.join(project_root, ".openclaw")
    if os.path.isfile(os.path.join(project_path, "openclaw.json")):
        _openclaw_home = project_path
        return _openclaw_home

    # Priority 2: ~/.openclaw
    home_path = os.path.join(os.path.expanduser("~"), ".openclaw")
    if os.path.isfile(os.path.join(home_path, "openclaw.json")):
        _openclaw_home = home_path
        return _openclaw_home

    _openclaw_home = project_path  # default even if not found
    return _openclaw_home


def _get_config() -> dict:
    """Read openclaw.json config."""
    config_path = os.path.join(_get_openclaw_home(), "openclaw.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _reader_thread(pipe, label: str):
    """Read process stdout/stderr line by line, look for QR codes."""
    global _qr_data, _status
    try:
        for raw_line in iter(pipe.readline, ""):
            line = raw_line.strip()
            if not line:
                continue

            _gateway_log.append(f"[{label}] {line}")
            if len(_gateway_log) > MAX_LOG_LINES:
                _gateway_log.pop(0)

            # Detect QR code data — OpenClaw prints QR codes for WhatsApp pairing
            # Look for base64 QR data or "Scan this QR code" markers
            if "qr" in line.lower() or "scan" in line.lower():
                logger.info(f"[OpenClaw] QR marker: {line}")

            # Capture raw QR data (OpenClaw outputs it as a data URI or base64)
            if line.startswith("data:image/") or "base64," in line:
                _qr_data = line
                logger.info("[OpenClaw] Captured QR code data")

            # Detect gateway ready
            if "gateway" in line.lower() and ("ready" in line.lower() or "listening" in line.lower()):
                _status = "running"
                logger.info(f"[OpenClaw] Gateway is running on port {_gateway_port}")

            if "error" in line.lower():
                logger.warning(f"[OpenClaw] {line}")

    except Exception as e:
        logger.error(f"[OpenClaw reader] {e}")


def _is_gateway_alive(port: int | None = None) -> bool:
    """Check if the OpenClaw gateway is responding on the given port via HTTP."""
    import requests as _req
    p = port or _gateway_port
    try:
        r = _req.get(f"http://127.0.0.1:{p}/__openclaw__/canvas/", timeout=2)
        return r.status_code < 500
    except Exception:
        return False


def start_gateway(port: int | None = None) -> dict:
    """Start the OpenClaw gateway process (skips if already running on port)."""
    global _process, _gateway_port, _status, _gateway_log, _qr_data

    config = _get_config()
    _gateway_port = port or config.get("gateway", {}).get("port", 18789)

    # If gateway is already alive on the port (user started it externally), just mark running
    if _is_gateway_alive(_gateway_port):
        _status = "running"
        _gateway_log.append(f"[NEXUS] Gateway already running on port {_gateway_port}")
        return {"success": True, "message": f"Gateway already running on port {_gateway_port}", "status": "running", "port": _gateway_port}

    # If our own process is still alive, skip
    if _process and _process.poll() is None:
        return {"success": True, "message": "Gateway already running", "status": _status, "port": _gateway_port}

    _status = "starting"
    _gateway_log.clear()
    _qr_data = None

    cmd = f"openclaw gateway run --port {_gateway_port} --allow-unconfigured"

    logger.info(f"[OpenClaw] Starting gateway: {cmd}")
    _gateway_log.append(f"[NEXUS] Starting: {cmd}")

    try:
        # On Windows, use CREATE_NEW_PROCESS_GROUP so the child survives independently
        creation_flags = 0
        if os.name == "nt":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        _process = subprocess.Popen(
            cmd,
            shell=True,
            creationflags=creation_flags,
        )

        try:
            # Wait for gateway to become responsive (up to 15 seconds)
            for i in range(15):
                time.sleep(1)
                if _is_gateway_alive(_gateway_port):
                    _status = "running"
                    _gateway_log.append(f"[NEXUS] ✅ Gateway is live on port {_gateway_port}")
                    logger.info(f"[OpenClaw] Gateway is live on port {_gateway_port}")
                    return {"success": True, "message": f"Gateway started on port {_gateway_port}", "status": "running", "port": _gateway_port}
                if _process.poll() is not None:
                    stderr_log.flush()
                    stderr_log.close()
                    try:
                        with open(os.path.join(log_dir, "gateway-stderr.log"), "r") as f:
                            err = f.read().strip()[-300:]
                    except Exception:
                        err = "unknown error"
                    _status = "error"
                    _gateway_log.append(f"[NEXUS] ❌ Gateway failed: {err}")
                    return {"success": False, "message": f"Gateway exited: {err}", "status": _status}

            # 15s passed, process alive but port not responding yet
            _status = "starting"
            _gateway_log.append("[NEXUS] Gateway process running, waiting for port...")
            return {"success": True, "message": f"Gateway process started (PID {_process.pid}), waiting for port...", "status": "starting", "port": _gateway_port}
        finally:
            # Always close the file handles so OS file descriptors are not leaked
            try:
                stdout_log.close()
            except Exception:
                pass
            try:
                stderr_log.close()
            except Exception:
                pass

    except FileNotFoundError:
        _status = "error"
        return {"success": False, "message": "OpenClaw not found. Run: npm install -g openclaw", "status": _status}
    except Exception as e:
        _status = "error"
        return {"success": False, "message": str(e), "status": _status}


def stop_gateway() -> dict:
    """Stop the OpenClaw gateway process."""
    global _process, _status

    if _process and _process.poll() is None:
        _process.terminate()
        _process.wait(timeout=10)
        _status = "stopped"
        _gateway_log.append("[NEXUS] Gateway stopped")
        return {"success": True, "message": "Gateway stopped"}

    _status = "stopped"
    return {"success": True, "message": "Gateway was not running"}


def get_status() -> dict:
    """Return current gateway status — probes the port to detect external gateways too."""
    global _status

    # Always probe the actual port — covers both our process and external ones
    if _is_gateway_alive():
        _status = "running"
    elif _process and _process.poll() is None:
        _status = "running"  # process alive but port not yet ready
    else:
        _status = "stopped"

    config = _get_config()
    gateway_config = config.get("gateway", {})
    channels_config = config.get("channels", {})
    
    # Enrich channel info
    channels_status = {}
    for name, cfg in channels_config.items():
        channels_status[name] = {
            **cfg,
            "has_token": bool(cfg.get("token")),
        }
        
    # Check if WhatsApp is paired (has folder in credentials)
    whatsapp_creds = os.path.join(_get_openclaw_home(), "credentials", "whatsapp")
    if os.path.isdir(whatsapp_creds) and any(os.listdir(whatsapp_creds)):
        if "whatsapp" in channels_status:
            channels_status["whatsapp"]["paired"] = True

    # Get model info (can be string or object with 'primary' key)
    raw_model = config.get("agents", {}).get("defaults", {}).get("model", "unknown")
    if isinstance(raw_model, dict):
        model_name = raw_model.get("primary", "unknown")
    else:
        model_name = str(raw_model)

    return {
        "status": _status,
        "port": _gateway_port,
        "pid": _process.pid if _process and _process.poll() is None else None,
        "qr_data": _qr_data,
        "log_tail": _gateway_log[-20:],
        "gateway_auth_token": gateway_config.get("auth", {}).get("token", ""),
        "channels": channels_status,
        "model": model_name,
    }


def start_channel_pairing(channel: str = "whatsapp") -> dict:
    """
    Trigger channel pairing by running `openclaw channel add <channel>`.
    This produces a QR code that the user scans.
    """
    global _qr_data
    _qr_data = None

    openclaw_home = _get_openclaw_home()
    if channel == "whatsapp":
        cmd = f"openclaw channels login --channel {channel}"
    else:
        # For Telegram/Slack, use 'add' with tokens if available in config
        config = _get_config()
        token = config.get("channels", {}).get(channel, {}).get("token")
        if token:
            cmd = f"openclaw channels add --channel {channel} --token {token}"
        else:
            cmd = f"openclaw channels add --channel {channel}"

    logger.info(f"[OpenClaw] Starting channel pairing: {cmd}")

    def _pair_reader():
        global _qr_data
        try:
            # Use same creation flags, etc. as gateway for consistency
            creation_flags = 0
            if os.name == "nt":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=os.environ.copy(), # Should already have OPENCLAW_HOME if set globally
                cwd=os.path.dirname(openclaw_home),
                creationflags=creation_flags
            )
            
            # Read output specifically looking for QR
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                if not line: continue
                
                _gateway_log.append(f"[Pairing] {line}")
                if len(_gateway_log) > MAX_LOG_LINES:
                    _gateway_log.pop(0)

                # Capture raw QR data 
                if line.startswith("data:image/") or "base64," in line:
                    _qr_data = line
                    logger.info("[OpenClaw] Captured QR code data from pairing process")
                
                if "Linked!" in line or "Ready" in line:
                    logger.info("[OpenClaw] Channel linked successfully")
            
            proc.wait(timeout=10)
        except Exception as e:
            logger.error(f"[OpenClaw pairing reader] {e}")

    # Start pairing in background
    threading.Thread(target=_pair_reader, daemon=True).start()

    return {
        "success": True,
        "message": f"Pairing started for {channel}. Check status/QR code in a few seconds.",
        "qr_data": _qr_data,
    }


def logout_channel(channel: str = "whatsapp") -> dict:
    """
    Log out of a channel by running `openclaw channels logout --channel <channel>`.
    """
    openclaw_home = _get_openclaw_home()
    cmd = f"openclaw channels logout --channel {channel}"

    logger.info(f"[OpenClaw] Logging out channel: {cmd}")

    try:
        env = os.environ.copy()
        env["OPENCLAW_HOME"] = openclaw_home

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            cwd=os.path.dirname(openclaw_home),
            timeout=30,
        )

        output = result.stdout + "\n" + result.stderr
        _gateway_log.append(f"[NEXUS] Logout output: {output[:500]}")

        # If pairing was active, clear it
        global _qr_data
        _qr_data = None

        return {
            "success": result.returncode == 0,
            "message": "Logged out successfully" if result.returncode == 0 else f"Logout failed: {output[:200]}",
            "output": output
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
