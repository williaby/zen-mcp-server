"""
Plugin System for Zen MCP Server Extensions

Automatically loads plugins without requiring server.py modifications.
Safe for upstream pulls - all customizations stay in plugins/ directory.
"""

import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)

def load_plugins() -> Dict[str, Any]:
    """
    Auto-load all plugins from plugins/ directory.
    
    Returns:
        Dict of plugin_name -> plugin_instance
    """
    plugins = {}

    try:
        # Import and initialize dynamic routing plugin
        from .dynamic_routing_plugin import DynamicRoutingPlugin

        routing_plugin = DynamicRoutingPlugin()
        if routing_plugin.initialize():
            plugins['dynamic_routing'] = routing_plugin
            logger.info("✅ Dynamic routing plugin loaded successfully")
        else:
            logger.warning("⚠️ Dynamic routing plugin failed to initialize")

    except ImportError as e:
        logger.debug(f"Dynamic routing plugin not available: {e}")
    except Exception as e:
        logger.error(f"Failed to load dynamic routing plugin: {e}")

    try:
        # Import and initialize PromptCraft system plugin
        from .promptcraft_system import plugin_instance as promptcraft_plugin

        if promptcraft_plugin.initialize():
            plugins['promptcraft_system'] = promptcraft_plugin
            logger.info("✅ PromptCraft system plugin loaded successfully")

            # Optionally start API server if enabled
            if os.getenv("ENABLE_PROMPTCRAFT_API", "false").lower() == "true":
                if promptcraft_plugin.start_api_server():
                    logger.info("🌐 PromptCraft API server started")
                else:
                    logger.warning("⚠️ PromptCraft API server failed to start")
        else:
            logger.warning("⚠️ PromptCraft system plugin failed to initialize")

    except ImportError as e:
        logger.debug(f"PromptCraft system plugin not available: {e}")
    except Exception as e:
        logger.error(f"Failed to load PromptCraft system plugin: {e}")

    return plugins

def get_plugin_tools() -> Dict[str, Any]:
    """
    Get tools provided by all loaded plugins.
    
    Returns:
        Dict of tool_name -> tool_instance
    """
    tools = {}
    plugins = load_plugins()

    for plugin_name, plugin in plugins.items():
        if hasattr(plugin, 'get_tools'):
            plugin_tools = plugin.get_tools()
            tools.update(plugin_tools)
            logger.debug(f"Loaded {len(plugin_tools)} tools from {plugin_name} plugin")

    return tools
