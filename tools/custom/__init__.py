"""
Custom Tools for Zen MCP Server (fork-specific).

This module provides a plugin-style system for adding custom MCP tools
without modifying upstream zen files. Tools placed in this directory are
auto-discovered at import time and registered with the main server.

Architecture:
- Custom tools are isolated in this directory.
- Auto-discovery (see ``discover_custom_tools``) prevents core file edits.
- Each tool is self-contained with its own prompts and logic.
- Registry system handles dynamic loading.

Currently registered custom MCP tools (and when to pick each):

- ``dynamic_model_selector`` -- *Recommendation only*. Returns a ranked
  list of suggested models with reasoning. Use when you need to decide
  which model(s) to call but do NOT yet want to call them. Does not
  execute the underlying task.

- ``tiered_consensus`` -- *Execution*. Runs a full multi-model consensus
  analysis (selection + execution + synthesis) for a given prompt at a
  fixed tier (1=free/$0, 2=economy/~$0.50, 3=premium/~$5). Use when you
  want consensus *answers*, not just model recommendations. Distinct
  from the upstream ``consensus`` tool, which takes an explicit model
  list instead of a tier.

Companion fork-specific tool (registered separately in
``tools/routing_status.py``):

- ``routing_status`` -- *Introspection*. Read-only view of the dynamic
  routing subsystem (status, model lists, stats, config). Also exposes
  an ad-hoc 'recommend' action that returns a structured pick for a
  prompt. Use when you want to know what the routing layer is doing or
  to debug recommendations programmatically.

Environment variables consumed by custom tools (all optional unless
otherwise noted):

- ``OPENROUTER_API_KEY`` -- strongly recommended for ``tiered_consensus``
  Levels 1 and 2; provides access to the free tier and most economy
  models. Without it, free-tier failover skips straight to whichever
  paid providers are configured.
- ``GEMINI_API_KEY`` / ``OPENAI_API_KEY`` / ``XAI_API_KEY`` /
  ``ANTHROPIC_API_KEY`` -- enable the corresponding provider for premium
  Level 3 models in ``tiered_consensus`` and as targets for
  ``dynamic_model_selector`` recommendations.
- ``CUSTOM_API_URL`` -- points to a local provider (e.g. Ollama at
  ``http://localhost:11434``). Useful for offline development.
- ``ZEN_SMART_ROUTING`` -- set to ``true`` to enable the dynamic routing
  subsystem inspected by ``routing_status``. When unset/false, the
  ``routing_status`` tool returns a help message rather than data.
- ``ZEN_ROUTING_EXCLUDE_TOOLS`` -- comma-separated list of tool names to
  exempt from routing (applies only when ``ZEN_SMART_ROUTING=true``).

Startup behavior: if a required provider key is missing for a model that
``tiered_consensus`` tries to use, the tool *skips that model via
failover* rather than failing the whole call. Missing every provider key
will cause the consensus call to fall back to a simulated response and
log an error -- check ``logs/mcp_server.log`` if results look generic.
"""

import inspect
import logging
import os

from tools.shared.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Registry of custom tools (populated by auto-discovery)
CUSTOM_TOOLS: dict[str, type[BaseTool]] = {}


def discover_custom_tools() -> dict[str, BaseTool]:
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

                    # Check if it's a concrete tool class defined in this module
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseTool)
                        and attr != BaseTool
                        and not inspect.isabstract(attr)
                        and attr.__module__ == f"tools.custom.{module_name}"
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


def get_custom_tools() -> dict[str, BaseTool]:
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
