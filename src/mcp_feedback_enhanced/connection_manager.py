#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Connection Manager
=====================

Handles persistent connections, auto-reconnection, and session state preservation
for the MCP Feedback Enhanced server.
"""

import asyncio
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any
import uuid

from .debug import server_debug_log as debug_log


class ConnectionManager:
    """Manages persistent MCP connections and auto-reconnection"""

    def __init__(self):
        self.is_persistent_mode = False
        self.session_store_path = Path.home() / ".cache" / "mcp-feedback-enhanced" / "sessions"
        self.heartbeat_interval = 30  # seconds
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_attempts = 10
        self.current_session: Optional[Dict[str, Any]] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Ensure session store directory exists
        self.session_store_path.mkdir(parents=True, exist_ok=True)

        debug_log("ConnectionManager initialized")

    def enable_persistent_mode(self):
        """Enable persistent connection mode"""
        self.is_persistent_mode = True
        debug_log("Persistent connection mode enabled")

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        debug_log(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    async def start_heartbeat(self):
        """Start connection heartbeat monitoring"""
        if not self.is_persistent_mode:
            return

        debug_log("Starting connection heartbeat")
        self.is_running = True

        async def heartbeat_loop():
            while self.is_running:
                try:
                    await asyncio.sleep(self.heartbeat_interval)
                    if self.is_running:
                        await self._send_heartbeat()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    debug_log(f"Heartbeat error: {e}")

        self.heartbeat_task = asyncio.create_task(heartbeat_loop())

    async def _send_heartbeat(self):
        """Send heartbeat signal to maintain connection"""
        try:
            # Simple heartbeat - just log that we're alive
            debug_log("Heartbeat: Connection alive")

            # If we have an active session, update its timestamp
            if self.current_session:
                self.current_session["last_heartbeat"] = time.time()
                await self._save_session_state()

        except Exception as e:
            debug_log(f"Heartbeat failed: {e}")

    async def create_persistent_session(self, project_directory: str, summary: str) -> str:
        """Create a new persistent session"""
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "project_directory": project_directory,
            "summary": summary,
            "created_at": time.time(),
            "last_heartbeat": time.time(),
            "status": "active",
            "feedback_result": None,
            "images": [],
            "command_logs": []
        }

        self.current_session = session_data
        await self._save_session_state()

        debug_log(f"Created persistent session: {session_id}")
        return session_id

    async def restore_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Restore a previously saved session"""
        try:
            session_file = self.session_store_path / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                self.current_session = session_data
                debug_log(f"Restored session: {session_id}")
                return session_data
            else:
                debug_log(f"Session file not found: {session_id}")
                return None

        except Exception as e:
            debug_log(f"Failed to restore session {session_id}: {e}")
            return None

    async def _save_session_state(self):
        """Save current session state to disk"""
        if not self.current_session:
            return

        try:
            session_id = self.current_session["session_id"]
            session_file = self.session_store_path / f"{session_id}.json"

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, ensure_ascii=False, indent=2)

            debug_log(f"Session state saved: {session_id}")

        except Exception as e:
            debug_log(f"Failed to save session state: {e}")

    async def update_session_feedback(self, feedback: str, images: list):
        """Update session with feedback data"""
        if self.current_session:
            self.current_session["feedback_result"] = feedback
            self.current_session["images"] = images
            self.current_session["status"] = "completed"
            await self._save_session_state()
            debug_log("Session feedback updated")

    async def handle_connection_loss(self):
        """Handle connection loss and attempt reconnection"""
        if not self.is_persistent_mode:
            return False

        debug_log("Connection lost, attempting reconnection...")

        for attempt in range(self.max_reconnect_attempts):
            try:
                debug_log(f"Reconnection attempt {attempt + 1}/{self.max_reconnect_attempts}")

                # Wait before reconnecting
                await asyncio.sleep(self.reconnect_delay)

                # Try to restore connection (implementation depends on the specific client)
                if await self._test_connection():
                    debug_log("Reconnection successful")
                    return True

            except Exception as e:
                debug_log(f"Reconnection attempt {attempt + 1} failed: {e}")

        debug_log("All reconnection attempts failed")
        return False

    async def _test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            # Simple connection test - in real implementation this would
            # test the actual MCP connection
            return True
        except Exception:
            return False

    def get_active_sessions(self) -> list:
        """Get list of active sessions"""
        sessions = []

        try:
            for session_file in self.session_store_path.glob("*.json"):
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # Check if session is recent (last 24 hours)
                if time.time() - session_data.get("last_heartbeat", 0) < 86400:
                    sessions.append(session_data)

        except Exception as e:
            debug_log(f"Error reading sessions: {e}")

        return sessions

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old session files"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for session_file in self.session_store_path.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    last_activity = session_data.get("last_heartbeat", 0)
                    if current_time - last_activity > max_age_seconds:
                        session_file.unlink()
                        debug_log(f"Cleaned up old session: {session_file.name}")

                except Exception as e:
                    debug_log(f"Error cleaning session {session_file.name}: {e}")

        except Exception as e:
            debug_log(f"Error during session cleanup: {e}")

    def stop(self):
        """Stop the connection manager"""
        self.is_running = False

        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Save final session state
        if self.current_session:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._save_session_state())
            loop.close()

        debug_log("ConnectionManager stopped")


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def with_persistent_connection(func):
    """Decorator to wrap functions with persistent connection handling"""
    async def wrapper(*args, **kwargs):
        manager = get_connection_manager()

        try:
            # Start heartbeat if in persistent mode
            if manager.is_persistent_mode and not manager.heartbeat_task:
                await manager.start_heartbeat()

            return await func(*args, **kwargs)

        except Exception as e:
            # Handle connection loss
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                debug_log(f"Connection issue detected: {e}")

                if await manager.handle_connection_loss():
                    # Retry the function after reconnection
                    return await func(*args, **kwargs)
                else:
                    # Reconnection failed, propagate the error
                    raise
            else:
                # Not a connection issue, propagate the error
                raise

    return wrapper
