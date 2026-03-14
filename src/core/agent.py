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
    await emit_event(task_id, "Thinking", {"message": f"Analyzing: {user_input}"})

    # ── Try OpenClaw Gateway ──────────────────────────────────────────────
    from src.core.openclaw_client import send_to_openclaw

    await emit_event(task_id, "AgentStep", {"desc": f"🦞 Routing task to OpenClaw ({channel})..."})

    result_text = await asyncio.to_thread(send_to_openclaw, user_input, channel=channel, sender=sender)

    # If OpenClaw returned any error
    if result_text.startswith("❌"):
        logger.warning(f"OpenClaw error: {result_text}")
        await emit_event(task_id, "AgentStep", {"desc": result_text})
    else:
        await emit_event(task_id, "AgentDone", {"result": result_text})

    timestamp = datetime.now().strftime("%I:%M:%S %p")

    return {
        "success": "❌" not in result_text,
        "steps": [{
            "type": "Action",
            "content": result_text,
            "timestamp": timestamp,
            "tool": "OpenClaw",
            "success": "❌" not in result_text,
        }],
        "intermediate_steps": [{
            "type": "Action",
            "content": result_text,
            "timestamp": timestamp,
            "tool": "OpenClaw",
            "success": "❌" not in result_text,
        }],
    }
