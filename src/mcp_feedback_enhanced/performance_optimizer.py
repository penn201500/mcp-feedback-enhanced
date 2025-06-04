#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer
====================

Optimizes startup performance and reduces latency for interactive GUI/Web UI.
"""

import asyncio
import os
import sys
import threading
import time
from typing import Optional, Dict, Any
import json
from pathlib import Path

from .debug import server_debug_log as debug_log


class PerformanceOptimizer:
    """Optimizes MCP Feedback Enhanced performance"""

    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "mcp-feedback-enhanced"
        self.cache_file = self.cache_dir / "performance_cache.json"
        self.cache_data: Dict[str, Any] = {}
        self.gui_preloaded = False
        self.web_manager_ready = False
        self._load_cache()

    def _load_cache(self):
        """Load performance cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                debug_log("Performance cache loaded")
        except Exception as e:
            debug_log(f"Failed to load performance cache: {e}")
            self.cache_data = {}

    def _save_cache(self):
        """Save performance cache to disk"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f)
            debug_log("Performance cache saved")
        except Exception as e:
            debug_log(f"Failed to save performance cache: {e}")

    def get_cached_environment_detection(self) -> Optional[Dict[str, bool]]:
        """Get cached environment detection results"""
        cache_key = "environment_detection"
        cached = self.cache_data.get(cache_key)

        if cached and time.time() - cached.get("timestamp", 0) < 300:  # 5 minutes cache
            debug_log("Using cached environment detection")
            return {
                "is_remote": cached["is_remote"],
                "can_gui": cached["can_gui"]
            }
        return None

    def cache_environment_detection(self, is_remote: bool, can_gui: bool):
        """Cache environment detection results"""
        self.cache_data["environment_detection"] = {
            "is_remote": is_remote,
            "can_gui": can_gui,
            "timestamp": time.time()
        }
        self._save_cache()
        debug_log("Environment detection cached")

    def preload_gui_components(self):
        """Preload GUI components in background thread"""
        if self.gui_preloaded:
            return

        def preload():
            try:
                start_time = time.time()
                debug_log("Preloading GUI components...")

                # Import PySide6 in background
                from PySide6.QtWidgets import QApplication
                from PySide6.QtCore import QTimer

                # Create minimal QApplication to test functionality
                app = QApplication.instance()
                if app is None:
                    app = QApplication([])

                load_time = time.time() - start_time
                debug_log(f"GUI components preloaded in {load_time:.2f}s")
                self.gui_preloaded = True

                # Cache the result
                self.cache_data["gui_preload"] = {
                    "success": True,
                    "load_time": load_time,
                    "timestamp": time.time()
                }
                self._save_cache()

            except Exception as e:
                debug_log(f"GUI preload failed: {e}")
                self.cache_data["gui_preload"] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }
                self._save_cache()

        # Run preload in background thread
        threading.Thread(target=preload, daemon=True).start()

    def preload_web_manager(self):
        """Preload and warm up web manager"""
        if self.web_manager_ready:
            return

        def preload():
            try:
                start_time = time.time()
                debug_log("Preloading web manager...")

                from .web.main import get_web_ui_manager
                manager = get_web_ui_manager()

                # Pre-initialize but don't start server yet
                manager.port = manager.port or 8765  # Set default port

                load_time = time.time() - start_time
                debug_log(f"Web manager preloaded in {load_time:.2f}s")
                self.web_manager_ready = True

            except Exception as e:
                debug_log(f"Web manager preload failed: {e}")

        # Run preload in background thread
        threading.Thread(target=preload, daemon=True).start()

    def get_optimal_interface_choice(self, force_web: bool = False) -> str:
        """Get optimal interface choice with caching"""
        # Check cache first
        cached_env = self.get_cached_environment_detection()

        if cached_env:
            is_remote = cached_env["is_remote"]
            can_gui = cached_env["can_gui"]
        else:
            # Do detection and cache result
            from .server import is_remote_environment, can_use_gui
            is_remote = is_remote_environment()
            can_gui = can_use_gui()
            self.cache_environment_detection(is_remote, can_gui)

        # Determine interface
        if force_web or is_remote or not can_gui:
            return "web"
        else:
            return "gui"

    async def fast_launch_interface(self, interface_type: str, project_dir: str, summary: str, timeout: int):
        """Launch interface with performance optimizations"""
        start_time = time.time()

        if interface_type == "web":
            return await self._fast_launch_web(project_dir, summary, timeout)
        else:
            return await self._fast_launch_gui(project_dir, summary, timeout)

    async def _fast_launch_web(self, project_dir: str, summary: str, timeout: int):
        """Fast web UI launch with optimizations"""
        debug_log("Fast launching Web UI...")

        # Use preloaded manager if available
        from .web.main import get_web_ui_manager
        manager = get_web_ui_manager()

        # Quick port check and reuse
        if not hasattr(manager, '_server_started') or not manager._server_started:
            # Start server only if not already running
            manager.start_server()
            manager._server_started = True

        # Create session and launch
        session_id = manager.create_session(project_dir, summary)
        session = manager.get_session(session_id)

        feedback_url = f"{manager.get_server_url()}/session/{session_id}"
        manager.open_browser(feedback_url)

        try:
            result = await session.wait_for_feedback(timeout)
            return result
        finally:
            manager.remove_session(session_id)

    async def _fast_launch_gui(self, project_dir: str, summary: str, timeout: int):
        """Fast GUI launch with optimizations"""
        debug_log("Fast launching GUI...")

        # Check if GUI was preloaded
        if not self.gui_preloaded:
            debug_log("GUI not preloaded, falling back to standard launch")

        # Use optimized GUI launch
        from .gui import feedback_ui_with_timeout
        return feedback_ui_with_timeout(project_dir, summary, timeout)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "gui_preloaded": self.gui_preloaded,
            "web_manager_ready": self.web_manager_ready,
            "cache_data": self.cache_data,
            "cache_file": str(self.cache_file)
        }


# Global optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def enable_performance_optimizations():
    """Enable all performance optimizations"""
    optimizer = get_performance_optimizer()

    # Start preloading in background
    optimizer.preload_gui_components()
    optimizer.preload_web_manager()

    debug_log("Performance optimizations enabled")
