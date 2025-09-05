"""
PromptCraft Integration System for Zen MCP Server

This plugin provides comprehensive API endpoints and model management 
for PromptCraft applications, including:

- RESTful API endpoints for route analysis and smart execution
- Two-channel model management (stable/experimental)  
- Automated model detection and graduation pipeline
- Performance tracking and optimization

The system extends the core zen-mcp-server routing infrastructure
while maintaining complete isolation from upstream code changes.
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class PromptCraftSystemPlugin:
    """
    Main plugin class for PromptCraft integration system.
    
    Manages API server lifecycle, background workers, and data persistence
    while integrating seamlessly with existing zen-mcp-server infrastructure.
    """

    def __init__(self):
        self.name = "promptcraft_system"
        self.version = "1.0.0"
        self.api_server = None
        self.background_workers = []
        self.data_manager = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        Initialize the PromptCraft system plugin.
        
        Sets up data directories, initializes API server, and starts
        background workers for model detection and graduation.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing PromptCraft System Plugin...")

            # Initialize data management
            from .data_manager import PromptCraftDataManager
            self.data_manager = PromptCraftDataManager()

            # Initialize API server
            from .api_server import PromptCraftAPIServer
            self.api_server = PromptCraftAPIServer(self.data_manager)

            # Start background workers if enabled
            if self._should_start_workers():
                self._start_background_workers()

            self.initialized = True
            logger.info("✅ PromptCraft System Plugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize PromptCraft System Plugin: {e}")
            return False

    def get_tools(self) -> Dict[str, Any]:
        """
        Return tools provided by this plugin.
        
        For PromptCraft, the main integration is through HTTP API endpoints
        rather than MCP tools, so this returns an empty dict.
        
        Returns:
            Dict[str, Any]: Empty dict (API-based integration)
        """
        return {}

    def start_api_server(self) -> bool:
        """
        Start the FastAPI server for PromptCraft endpoints.
        
        Returns:
            bool: True if server started successfully
        """
        if not self.initialized or not self.api_server:
            logger.error("Plugin not initialized - cannot start API server")
            return False

        try:
            # Start API server in background thread
            server_thread = threading.Thread(
                target=self.api_server.start_server,
                daemon=True
            )
            server_thread.start()
            logger.info("🚀 PromptCraft API server started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start PromptCraft API server: {e}")
            return False

    def stop_api_server(self):
        """Stop the API server gracefully."""
        if self.api_server:
            self.api_server.stop_server()
            logger.info("🛑 PromptCraft API server stopped")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current plugin status and health information.
        
        Returns:
            Dict containing plugin status, API server health, and metrics
        """
        status = {
            "plugin_name": self.name,
            "plugin_version": self.version,
            "initialized": self.initialized,
            "api_server_running": self.api_server.is_running() if self.api_server else False,
            "background_workers": len(self.background_workers),
            "data_manager_healthy": self.data_manager.health_check() if self.data_manager else False
        }

        # Add API server metrics if available
        if self.api_server and self.api_server.is_running():
            status["api_metrics"] = self.api_server.get_metrics()

        return status

    def _should_start_workers(self) -> bool:
        """Check if background workers should be started based on environment config."""
        import os
        return os.getenv("ENABLE_PROMPTCRAFT_WORKERS", "true").lower() == "true"

    def _start_background_workers(self):
        """Start background worker processes for model detection and graduation."""
        try:
            from .background_workers import GraduationWorker, ModelDetectionWorker

            # Start model detection worker
            detection_worker = ModelDetectionWorker(self.data_manager)
            detection_thread = threading.Thread(
                target=detection_worker.start,
                daemon=True
            )
            detection_thread.start()
            self.background_workers.append(detection_worker)

            # Start graduation worker
            graduation_worker = GraduationWorker(self.data_manager)
            graduation_thread = threading.Thread(
                target=graduation_worker.start,
                daemon=True
            )
            graduation_thread.start()
            self.background_workers.append(graduation_worker)

            logger.info(f"🔄 Started {len(self.background_workers)} background workers")

        except Exception as e:
            logger.warning(f"⚠️ Could not start background workers: {e}")

# Global plugin instance for auto-discovery
plugin_instance = PromptCraftSystemPlugin()
