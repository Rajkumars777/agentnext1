"""
openclaw_client.py
==================
Forwards user messages to the local OpenClaw Gateway via WebSocket RPC.
OpenClaw uses a JSON-RPC protocol over WebSocket (not REST).

Protocol:
  1. Connect to ws://127.0.0.1:<port>
  2. Receive connect.challenge event with nonce
  3. Send connect request with auth token
  4. Send chat.send request with message
  5. Receive chat events (delta/final) for streaming response
"""

import json
import os
import logging
import uuid
import threading
import time

logger = logging.getLogger(__name__)

# Path to the config file
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def _get_openclaw_home() -> str:
    """Always use the standard OpenClaw home directory."""
    return os.path.join(os.path.expanduser("~"), ".openclaw")

def _get_openclaw_config_path() -> str:
    return os.path.join(_get_openclaw_home(), "openclaw.json")


def load_config() -> dict:
    """Load the current config from config.json."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "ai_provider": "gemini",
            "api_key": "",
            "ai_model": "gemini-2.5-flash",
            "openclaw_gateway_port": 18789,
            "openclaw_channel": "",
            "openclaw_token": "",
        }


def load_openclaw_config() -> dict:
    """Load OpenClaw's own config."""
    config_path = _get_openclaw_config_path()
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_gateway_port() -> int:
    """Get the OpenClaw gateway port from openclaw.json or fallback."""
    oc_config = load_openclaw_config()
    return oc_config.get("gateway", {}).get("port", 18789)


def get_auth_token() -> str | None:
    """Get the auth token from openclaw.json, respecting mode."""
    # We no longer check environment for tokens to match user's manual behavior
    oc_config = load_openclaw_config()
    auth_cfg = oc_config.get("gateway", {}).get("auth", {})
    if auth_cfg.get("mode") == "none":
        return None
    return auth_cfg.get("token", "")


def send_to_openclaw(user_text: str, channel: str = "nexus", sender: str = "main") -> str:
    """
    Forwards the user's UI input to the local OpenClaw Gateway via WebSocket RPC.
    Returns the agent's reply text.
    
    Args:
        user_text: The message to send.
        channel: The source channel (e.g., whatsapp, telegram, nexus).
        sender: The user identity or conversation ID from the source.
    """
    try:
        import websocket  # websocket-client library
    except ImportError:
        return "❌ websocket-client not installed. Run: pip install websocket-client"

    port = get_gateway_port()
    token = get_auth_token()
    ws_url = f"ws://127.0.0.1:{port}"

    masked_token = (token[:4] + "..." + token[-4:]) if token and len(token) >= 8 else (token or "None")
    logger.info(f"🦞 Routing to OpenClaw via WebSocket: port={port}, token={masked_token}, msg={user_text[:50]}...")

    result_text = ""
    error_text = ""
    connect_nonce = ""
    connected = False
    chat_done = threading.Event()
    connect_done = threading.Event()

    def generate_id():
        return str(uuid.uuid4())

    def on_message(ws, raw_msg):
        nonlocal result_text, error_text, connect_nonce, connected

        try:
            msg = json.loads(raw_msg)
        except json.JSONDecodeError:
            return

        msg_type = msg.get("type", "")

        # Handle events
        if msg_type == "event":
            event_name = msg.get("event", "")
            payload = msg.get("payload", {})

            # Step 1: Receive connect challenge with nonce
            if event_name == "connect.challenge":
                connect_nonce = payload.get("nonce", "") if payload else ""
                # Now send the connect request
                connect_req = {
                    "type": "req",
                    "id": generate_id(),
                    "method": "connect",
                    "params": {
                        "minProtocol": 3,
                        "maxProtocol": 3,
                        "client": {
                            "id": "gateway-client",
                            "version": "1.0.0",
                            "platform": "windows",
                            "mode": "backend",
                            "instanceId": generate_id(),
                        },
                        "role": "operator",
                        "scopes": ["operator.admin"],
                        "caps": [],
                    },
                }
                if token is not None:
                    connect_req["params"]["auth"] = {"token": token}
                
                ws.send(json.dumps(connect_req))
                return

            if event_name == "connect.ready":
                connected = True
                connect_done.set()
                return

            # Step 3: Handle chat response events
            if event_name == "chat":
                state = payload.get("state", "")
                message = payload.get("message", {})

                if state == "delta":
                    # Streaming delta — extract text
                    if isinstance(message, dict):
                        content = message.get("content", [])
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    result_text += block.get("text", "")
                        elif isinstance(message.get("text"), str):
                            result_text += message["text"]

                elif state == "final":
                    # Final response
                    if isinstance(message, dict):
                        content = message.get("content", [])
                        if isinstance(content, list):
                            texts = []
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    texts.append(block.get("text", ""))
                            if texts:
                                result_text = "\n".join(texts)
                        elif isinstance(message.get("text"), str):
                            result_text = message["text"]
                    chat_done.set()

                elif state == "error":
                    error_text = payload.get("errorMessage", "Chat error")
                    chat_done.set()

                elif state == "aborted":
                    if not result_text:
                        error_text = "Chat aborted"
                    chat_done.set()

                return

        # Handle RPC responses
        if msg_type == "res":
            req_id = msg.get("id", "")
            ok = msg.get("ok", False)

            if ok:
                # Connect successful — now send the chat message
                if not connected:
                    connected = True
                    connect_done.set()
            else:
                err = msg.get("error", {})
                err_msg = err.get("message", "Unknown error")
                error_text = f"Gateway error: {err_msg}"
                connect_done.set()
                chat_done.set()

    def on_error(ws, error):
        nonlocal error_text
        error_text = f"WebSocket error: {str(error)}"
        connect_done.set()
        chat_done.set()

    def on_close(ws, close_status_code, close_msg):
        connect_done.set()
        chat_done.set()

    def on_open(ws):
        # Step 1: Send connect request immediately if we want to skip waiting for challenge
        # Or wait for on_message to handle challenge. 
        # For Protocol 3, it's safer to wait for challenge, but let's send a probe if needed.
        pass

    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        # Run WebSocket in a thread
        ws_thread = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 30})
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for connection + auth
        if not connect_done.wait(timeout=10):
            ws.close()
            return "❌ OpenClaw Gateway connection timed out."

        if error_text:
            ws.close()
            return f"❌ {error_text}"

        if not connected:
            ws.close()
            return "❌ Failed to authenticate with OpenClaw Gateway."

        # Step 2: Send chat.send request
        # Session key format: agent:{channel}:{sender}
        session_key = f"agent:{channel}:{sender}"
        
        execution_id = generate_id()
        chat_req = {
            "type": "req",
            "id": generate_id(),
            "method": "chat.send",
            "params": {
                "sessionKey": session_key,
                "message": user_text,
                "deliver": False,
                "idempotencyKey": execution_id,
            },
        }
        ws.send(json.dumps(chat_req))
        logger.info("🦞 chat.send request sent, waiting for response...")

        # Wait for chat response (up to 5 minutes for complex tasks)
        if not chat_done.wait(timeout=300):
            ws.close()
            return "❌ OpenClaw request timed out after 5 minutes."

        ws.close()

        if error_text:
            return f"❌ {error_text}"

        return result_text if result_text else "Task completed (no text response)."

    except ConnectionRefusedError:
        return (
            "❌ Cannot reach OpenClaw Gateway. "
            f"Make sure OpenClaw is running locally on port {port}. "
            "You can start it with: `openclaw gateway` or check the logs."
        )
    except Exception as e:
        return f"❌ Error communicating with OpenClaw: {str(e)}"
