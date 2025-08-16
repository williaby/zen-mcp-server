"""
Hub-specific settings and configuration

Contains configuration for the hub functionality including
MCP server connections, filtering behavior, and performance settings.
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class MCPServerConfig:
    """Configuration for an individual MCP server connection"""
    name: str
    command: str
    server_type: str = "stdio"  # "stdio" or "sse"
    url: Optional[str] = None   # For SSE servers
    enabled: bool = True
    timeout: int = 30

@dataclass 
class HubSettings:
    """Configuration settings for the Zen MCP Hub"""
    
    # Enable/disable hub functionality
    hub_enabled: bool = True
    
    # Tool filtering settings
    enable_dynamic_filtering: bool = True
    fallback_to_core_tools: bool = True
    max_tools_per_context: int = 25
    
    # Performance settings
    tool_detection_timeout: int = 5  # seconds
    mcp_client_timeout: int = 30     # seconds
    cache_detection_results: bool = True
    cache_ttl: int = 300            # 5 minutes
    
    # Logging
    enable_hub_logging: bool = True
    log_tool_filtering: bool = False  # Can be verbose
    
    @classmethod
    def from_env(cls) -> "HubSettings":
        """Create settings from environment variables"""
        return cls(
            hub_enabled=os.getenv("ZEN_HUB_ENABLED", "true").lower() == "true",
            enable_dynamic_filtering=os.getenv("ZEN_HUB_FILTERING", "true").lower() == "true",
            fallback_to_core_tools=os.getenv("ZEN_HUB_FALLBACK", "true").lower() == "true",
            max_tools_per_context=int(os.getenv("ZEN_HUB_MAX_TOOLS", "25")),
            tool_detection_timeout=int(os.getenv("ZEN_HUB_DETECTION_TIMEOUT", "5")),
            mcp_client_timeout=int(os.getenv("ZEN_HUB_CLIENT_TIMEOUT", "30")),
            cache_detection_results=os.getenv("ZEN_HUB_CACHE", "true").lower() == "true",
            cache_ttl=int(os.getenv("ZEN_HUB_CACHE_TTL", "300")),
            enable_hub_logging=os.getenv("ZEN_HUB_LOGGING", "true").lower() == "true",
            log_tool_filtering=os.getenv("ZEN_HUB_FILTER_LOGGING", "false").lower() == "true"
        )

# Default MCP server configurations
DEFAULT_MCP_SERVERS: Dict[str, MCPServerConfig] = {
    "git": MCPServerConfig(
        name="git",
        command="uvx mcp-server-git",
        server_type="stdio"
    ),
    "time": MCPServerConfig(
        name="time", 
        command="uvx mcp-server-time",
        server_type="stdio"
    ),
    "sequential-thinking": MCPServerConfig(
        name="sequential-thinking",
        command="npx @modelcontextprotocol/server-sequential-thinking",
        server_type="stdio"
    ),
    "context7-sse": MCPServerConfig(
        name="context7-sse",
        command="",
        server_type="sse",
        url="https://mcp.context7.com/sse"
    ),
    "safety-mcp-sse": MCPServerConfig(
        name="safety-mcp-sse", 
        command="",
        server_type="sse",
        url="https://mcp.safetycli.com/sse"
    )
}