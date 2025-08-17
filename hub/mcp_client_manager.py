"""
MCP Client Manager for Zen Hub

Manages connections to external MCP servers and provides a unified interface
for tool discovery and execution across multiple MCP servers.
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from .config.hub_settings import DEFAULT_MCP_SERVERS, HubSettings, MCPServerConfig
from .config.tool_mappings import get_server_for_tool

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents a tool from an MCP server"""
    name: str
    description: str
    server: str
    input_schema: Dict[str, Any]

class MCPClient:
    """Client for connecting to a single MCP server"""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self.tools: Dict[str, MCPTool] = {}

    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            if self.config.server_type == "stdio":
                return await self._connect_stdio()
            elif self.config.server_type == "sse":
                return await self._connect_sse()
            else:
                logger.error(f"Unsupported server type: {self.config.server_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to {self.config.name}: {e}")
            return False

    async def _connect_stdio(self) -> bool:
        """Connect to stdio-based MCP server"""
        try:
            # Start the MCP server process
            self.process = subprocess.Popen(
                self.config.command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Initialize MCP protocol
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "zen-hub",
                        "version": "1.0.0"
                    }
                }
            }

            # Send initialization
            self.process.stdin.write(json.dumps(init_request) + "\n")
            self.process.stdin.flush()

            # Read response (simplified - real implementation would need proper JSON-RPC handling)
            response_line = self.process.stdout.readline()
            if response_line:
                self.connected = True
                await self._discover_tools()
                logger.info(f"Connected to {self.config.name} via stdio")
                return True

        except Exception as e:
            logger.error(f"Failed to connect to stdio server {self.config.name}: {e}")

        return False

    async def _connect_sse(self) -> bool:
        """Connect to SSE-based MCP server"""
        # For now, mark as connected - real implementation would use aiohttp
        # to connect to the SSE endpoint
        try:
            logger.info(f"SSE connection to {self.config.name} at {self.config.url} (mock)")
            self.connected = True
            # Mock some tools for SSE servers
            await self._mock_sse_tools()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SSE server {self.config.name}: {e}")
            return False

    async def _discover_tools(self):
        """Discover available tools from the connected server"""
        if not self.connected or not self.process:
            return

        try:
            # Request tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            self.process.stdin.write(json.dumps(tools_request) + "\n")
            self.process.stdin.flush()

            # Read response (simplified)
            response_line = self.process.stdout.readline()
            if response_line:
                # Mock parsing - real implementation would parse JSON-RPC response
                self._mock_tools_for_server()

        except Exception as e:
            logger.error(f"Failed to discover tools for {self.config.name}: {e}")

    def _mock_tools_for_server(self):
        """Mock tools based on server name (temporary implementation)"""
        server_name = self.config.name

        if server_name == "git":
            self.tools = {
                f"mcp__{server_name}__git_status": MCPTool(
                    name=f"mcp__{server_name}__git_status",
                    description="Shows the working tree status",
                    server=server_name,
                    input_schema={"type": "object", "properties": {"repo_path": {"type": "string"}}}
                ),
                f"mcp__{server_name}__git_commit": MCPTool(
                    name=f"mcp__{server_name}__git_commit",
                    description="Records changes to the repository",
                    server=server_name,
                    input_schema={"type": "object", "properties": {"repo_path": {"type": "string"}, "message": {"type": "string"}}}
                )
            }
        elif server_name == "time":
            self.tools = {
                f"mcp__{server_name}__get_current_time": MCPTool(
                    name=f"mcp__{server_name}__get_current_time",
                    description="Get current time in a specific timezone",
                    server=server_name,
                    input_schema={"type": "object", "properties": {"timezone": {"type": "string"}}}
                )
            }
        # Add more server-specific tool mocks as needed

    async def _mock_sse_tools(self):
        """Mock tools for SSE servers"""
        server_name = self.config.name

        if server_name == "context7-sse":
            self.tools = {
                f"mcp__{server_name.replace('-', '_')}__resolve_library_id": MCPTool(
                    name=f"mcp__{server_name.replace('-', '_')}__resolve_library_id",
                    description="Resolve library identifier",
                    server=server_name,
                    input_schema={"type": "object", "properties": {"library": {"type": "string"}}}
                )
            }
        elif server_name == "safety-mcp-sse":
            self.tools = {
                f"mcp__{server_name.replace('-', '_')}__check_package_security": MCPTool(
                    name=f"mcp__{server_name.replace('-', '_')}__check_package_security",
                    description="Check if Python package contains vulnerabilities",
                    server=server_name,
                    input_schema={"type": "object", "properties": {"packages": {"type": "array"}}}
                )
            }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on this MCP server"""
        if not self.connected:
            raise RuntimeError(f"Not connected to {self.config.name}")

        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found on server {self.config.name}")

        # For now, return a mock response
        # Real implementation would send JSON-RPC request to the server
        return {
            "status": "success",
            "result": f"Mock result from {tool_name} on {self.config.name}",
            "arguments": arguments
        }

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.process:
            self.process.terminate()
            self.process = None
        self.connected = False
        logger.info(f"Disconnected from {self.config.name}")

class MCPClientManager:
    """Manages connections to multiple MCP servers"""

    def __init__(self, settings: Optional[HubSettings] = None):
        self.settings = settings or HubSettings.from_env()
        self.clients: Dict[str, MCPClient] = {}
        self.connected_servers: Set[str] = set()

    async def initialize(self) -> bool:
        """Initialize connections to all configured MCP servers"""
        logger.info("Initializing MCP client connections...")

        success_count = 0
        for server_name, config in DEFAULT_MCP_SERVERS.items():
            if not config.enabled:
                logger.info(f"Skipping disabled server: {server_name}")
                continue

            try:
                client = MCPClient(config)
                if await client.connect():
                    self.clients[server_name] = client
                    self.connected_servers.add(server_name)
                    success_count += 1
                    logger.info(f"Successfully connected to {server_name}")
                else:
                    logger.warning(f"Failed to connect to {server_name}")

            except Exception as e:
                logger.error(f"Error connecting to {server_name}: {e}")

        logger.info(f"Connected to {success_count}/{len(DEFAULT_MCP_SERVERS)} MCP servers")
        return success_count > 0

    async def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all tools from all connected servers"""
        all_tools = {}

        for server_name, client in self.clients.items():
            for tool_name, tool in client.tools.items():
                all_tools[tool_name] = tool

        return all_tools

    async def get_tools_for_servers(self, server_names: Set[str]) -> Dict[str, MCPTool]:
        """Get tools from specific servers only"""
        filtered_tools = {}

        for server_name in server_names:
            if server_name in self.clients:
                client = self.clients[server_name]
                for tool_name, tool in client.tools.items():
                    filtered_tools[tool_name] = tool

        return filtered_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route a tool call to the appropriate server"""
        server_name = get_server_for_tool(tool_name)

        if server_name == "claude_code":
            # These are built-in Claude Code tools, not MCP tools
            raise ValueError(f"Tool {tool_name} is a built-in Claude Code tool, not an MCP tool")

        if server_name not in self.clients:
            raise RuntimeError(f"Server {server_name} not connected")

        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)

    async def shutdown(self):
        """Shutdown all MCP client connections"""
        logger.info("Shutting down MCP client connections...")

        for client in self.clients.values():
            await client.disconnect()

        self.clients.clear()
        self.connected_servers.clear()
        logger.info("All MCP client connections closed")
