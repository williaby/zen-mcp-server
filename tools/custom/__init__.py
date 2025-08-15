"""
Custom Tools for Zen MCP Server

This module provides a plugin-style system for adding custom tools without
modifying core zen files. Custom tools are automatically discovered and
registered, minimizing merge conflicts during git pulls.

Architecture:
- Custom tools are isolated in this directory
- Auto-discovery prevents core file modifications
- Each tool is self-contained with its own prompts and logic
- Registry system handles dynamic loading
"""

import logging
import os
from typing import Dict, Type

from tools.shared.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Registry of custom tools (populated by auto-discovery)
CUSTOM_TOOLS: Dict[str, Type[BaseTool]] = {}


def discover_custom_tools() -> Dict[str, BaseTool]:
    """
    Automatically discover and instantiate custom tools in this directory.

    This function scans the tools/custom directory for tool implementations
    and registers them without requiring modifications to core files.

    Returns:
        Dictionary mapping tool names to instantiated tool objects
    """

    custom_tool_instances = {}

    # Get the directory containing this __init__.py file
    custom_tools_dir = os.path.dirname(__file__)

    # Scan for Python files in the custom tools directory
    for filename in os.listdir(custom_tools_dir):
        if filename.endswith(".py") and filename not in ["__init__.py", "registry.py"]:
            module_name = filename[:-3]  # Remove .py extension

            try:
                # Dynamic import of the custom tool module
                module = __import__(f"tools.custom.{module_name}", fromlist=[""])

                # Look for classes that inherit from BaseTool
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's a tool class (inherits from BaseTool)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseTool)
                        and attr != BaseTool
                        and hasattr(attr, "get_name")
                    ):

                        try:
                            # Instantiate the tool
                            tool_instance = attr()
                            tool_name = tool_instance.get_name()

                            custom_tool_instances[tool_name] = tool_instance
                            logger.info(f"✅ Discovered custom tool: {tool_name}")

                        except Exception as e:
                            logger.error(f"❌ Failed to instantiate custom tool {attr_name}: {e}")

            except Exception as e:
                logger.error(f"❌ Failed to import custom tool module {module_name}: {e}")

    logger.info(f"Custom tool discovery complete: {len(custom_tool_instances)} tools loaded")
    return custom_tool_instances


def get_custom_tools() -> Dict[str, BaseTool]:
    """
    Get all discovered custom tools.

    This is the main entry point for the core server to load custom tools
    without needing to know about specific tool implementations.

    Returns:
        Dictionary mapping tool names to tool instances
    """
    return discover_custom_tools()


# Auto-discover tools when this module is imported
logger.info("Starting custom tool auto-discovery...")
CUSTOM_TOOLS_INSTANCES = discover_custom_tools()
