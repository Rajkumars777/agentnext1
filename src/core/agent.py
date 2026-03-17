"""
src/core/agent.py
==================
Main agent — routes all tasks through OpenClaw Gateway.

The agent forwards user input to the OpenClaw local Gateway via WebSocket RPC.
Settings (API key, model, provider) are loaded from openclaw.json dynamically.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "ai_provider": "gemini",
            "api_key": "",
            "ai_model": "gemini-2.5-flash",
        }

def reload_agent():
    """Called when settings change."""
    logger.info("🔄 Agent config reloaded")


# ─── Main Entry Point ────────────────────────────────────────────────────────

async def run_agent(user_input: str, task_id: str = "default", channel: str = "nexus", sender: str = "main"):
    """
    Routes user input through OpenClaw Local Gateway via WebSocket RPC.
    """
    from src.api.routers.events import emit_event
    
    # ── Workspace Remapping ──────────────────────────────────────────────────
    # ── System Folders ───────────────────────────────────────────────────────
    # Use actual system folders from the user profile
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_home = os.path.expanduser("~")
    workspace_instruction = (
        f"IMPORTANT: The user workspace logic remains in '{project_root}', but "
        "always use these ACTUAL system folders for user files:\n"
        f"- Desktop: {os.path.join(user_home, 'Desktop')}\n"
        f"- Downloads: {os.path.join(user_home, 'Downloads')}\n"
        f"- Documents: {os.path.join(user_home, 'Documents')}\n"
        f"- Music: {os.path.join(user_home, 'Music')}\n"
        f"- Videos: {os.path.join(user_home, 'Videos')}\n"
        f"- Pictures: {os.path.join(user_home, 'Pictures')}\n"
        "ALWAYS use these system paths when the user refers to these folders. "
        "Do NOT use project-local 'src/Downloads' etc.\n\n"
    )
    
    contextualized_input = workspace_instruction + user_input
    
    await emit_event(task_id, "Thinking", {"message": f"Analyzing: {user_input}"})

    # ── Local Desktop Intention Detection (Basic) ─────────────────────────
    processed_input = user_input.lower().strip()
    
    # 1. Close application
    if any(kw in processed_input for kw in ["close ", "exit ", "stop ", "terminate "]):
        app_name = processed_input.replace("close ", "").replace("exit ", "").replace("stop ", "").replace("terminate ", "").replace("the ", "").strip()
        if app_name:
            from src.capabilities.desktop import close_app
            await emit_event(task_id, "AgentStep", {"desc": f"🖥️ Detected 'close' intent for: {app_name}"})
            result = await asyncio.to_thread(close_app, app_name)
            await emit_event(task_id, "AgentDone", {"result": result["message"]})
            return _format_response(result["message"], "DesktopTool")

    # 2. Open application
    if any(kw in processed_input for kw in ["open ", "start ", "launch ", "run "]):
        app_name = processed_input.replace("open ", "").replace("start ", "").replace("launch ", "").replace("run ", "").replace("the ", "").strip()
        if app_name:
            from src.capabilities.desktop import open_app
            await emit_event(task_id, "AgentStep", {"desc": f"🖥️ Detected 'open' intent for: {app_name}"})
            result = await asyncio.to_thread(open_app, app_name)
            await emit_event(task_id, "AgentDone", {"result": result["message"]})
            return _format_response(result["message"], "DesktopTool")

    # 3. Check if running
    if any(kw in processed_input for kw in ["is ", "check if "]) and "running" in processed_input:
        app_name = processed_input.replace("is ", "").replace("check if ", "").replace(" running", "").replace("the ", "").strip()
        if app_name:
            from src.capabilities.desktop import is_running
            await emit_event(task_id, "AgentStep", {"desc": f"🖥️ Detected 'status' intent for: {app_name}"})
            running = await asyncio.to_thread(is_running, app_name)
            msg = f"Yes, {app_name} is currently running." if running else f"No, {app_name} is not running."
            await emit_event(task_id, "AgentDone", {"result": msg})
            return _format_response(msg, "DesktopTool")

    # ── Try OpenClaw Gateway ──────────────────────────────────────────────
    from src.core.openclaw_client import send_to_openclaw

    await emit_event(task_id, "AgentStep", {"desc": f"Wait for a moment({channel})..."})

    result_text = await asyncio.to_thread(send_to_openclaw, contextualized_input, channel=channel, sender=sender)

    # If OpenClaw returned any error
    if result_text.startswith("❌"):
        logger.warning(f"model error: {result_text}")
        await emit_event(task_id, "AgentStep", {"desc": result_text})
    else:
        await emit_event(task_id, "AgentDone", {"result": result_text})

    return _format_response(result_text, "model")

def _format_response(result_text: str, tool_name: str):
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    return {
        "success": "❌" not in result_text,
        "steps": [{
            "type": "Action",
            "content": result_text,
            "timestamp": timestamp,
            "tool": tool_name,
            "success": "❌" not in result_text,
        }],
        "intermediate_steps": [{
            "type": "Action",
            "content": result_text,
            "timestamp": timestamp,
            "tool": tool_name,
            "success": "❌" not in result_text,
        }],
    }
