"""
Dynamic Routing Plugin

Self-contained plugin that adds intelligent model routing to the Zen MCP Server
without requiring modifications to server.py. Safe for upstream pulls.
"""

import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)

class DynamicRoutingPlugin:
    """Plugin that adds dynamic model routing capabilities."""

    def __init__(self):
        self.enabled = False
        self.routing_tool = None
        self._integration_initialized = False

    def initialize(self) -> bool:
        """
        Initialize the dynamic routing plugin.
        
        Returns:
            bool: True if successfully initialized
        """
        try:
            # Check if routing should be enabled
            self.enabled = os.getenv("ZEN_SMART_ROUTING", "").lower() == "true"

            if not self.enabled:
                logger.info("Dynamic routing disabled (ZEN_SMART_ROUTING not set to true)")
                return False

            # Initialize routing system
            self._initialize_routing_integration()
            self._initialize_routing_tool()

            logger.info("🚀 Dynamic routing plugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize dynamic routing plugin: {e}")
            return False

    def _initialize_routing_integration(self):
        """Initialize the core routing integration with BaseTool."""
        try:
            from routing.integration import integrate_with_server
            integrate_with_server()
            self._integration_initialized = True
            logger.debug("Routing integration with BaseTool completed")
        except ImportError as e:
            logger.warning(f"Routing integration not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize routing integration: {e}")
            raise

    def _initialize_routing_tool(self):
        """Initialize the routing status tool."""
        try:
            from tools.routing_status import RoutingStatusTool
            self.routing_tool = RoutingStatusTool()
            logger.debug("Routing status tool initialized")
        except ImportError as e:
            logger.warning(f"Routing status tool not available: {e}")
            # Not critical - continue without the status tool
        except Exception as e:
            logger.error(f"Failed to initialize routing status tool: {e}")
            # Not critical - continue without the status tool

    def get_tools(self) -> Dict[str, Any]:
        """
        Get tools provided by this plugin.
        
        Returns:
            Dict of tool_name -> tool_instance
        """
        tools = {}

        if self.enabled and self.routing_tool:
            tools["routing_status"] = self.routing_tool

        return tools

    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status information.
        
        Returns:
            Dict with plugin status details
        """
        return {
            "enabled": self.enabled,
            "integration_initialized": self._integration_initialized,
            "routing_tool_available": self.routing_tool is not None,
            "environment_variable": os.getenv("ZEN_SMART_ROUTING", "not set")
        }
