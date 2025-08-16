"""
Zen MCP Hub - Intelligent MCP server orchestration and tool filtering

This module provides centralized orchestration for multiple MCP servers with
intelligent tool filtering based on query context and task detection.

Key Components:
- MCPClientManager: Manages connections to external MCP servers
- ZenToolFilter: Implements dynamic tool loading and filtering
- ProxyHandler: Routes tool calls to appropriate servers

The hub acts as a smart proxy that reduces context usage by only exposing
relevant tools based on query analysis while maintaining full functionality.
"""

__version__ = "1.0.0"
__author__ = "Zen MCP Hub"

from .mcp_client_manager import MCPClientManager
from .tool_filter import ZenToolFilter

__all__ = ["MCPClientManager", "ZenToolFilter"]