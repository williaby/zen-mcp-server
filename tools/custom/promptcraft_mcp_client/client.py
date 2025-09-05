"""
PromptCraft MCP Stdio Client

Main client implementation for communicating with zen-mcp-server via MCP stdio protocol.
Provides a high-level interface for PromptCraft integration with automatic fallback,
error handling, and connection management.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from .models import (
    MCPConnectionConfig,
    MCPConnectionStatus, 
    MCPHealthCheck,
    MCPToolCall,
    MCPToolResult,
    RouteAnalysisRequest,
    SmartExecutionRequest,
    ModelListRequest,
    AnalysisResult,
    ExecutionResult,
    ModelListResult,
    FallbackConfig,
    BridgeMetrics,
)
from .subprocess_manager import ProcessPool, ZenMCPProcess
from .protocol_bridge import MCPProtocolBridge
from .error_handler import MCPConnectionManager, RetryHandler

logger = logging.getLogger(__name__)


class ZenMCPStdioClient:
    """
    High-level MCP stdio client for PromptCraft integration with zen-mcp-server.
    
    Features:
    - Async MCP stdio communication
    - Automatic subprocess management
    - HTTP fallback on MCP failures
    - Connection pooling and reuse
    - Comprehensive error handling
    - Performance metrics tracking
    """
    
    def __init__(
        self,
        server_path: str,
        env_vars: Optional[Dict[str, str]] = None,
        fallback_config: Optional[FallbackConfig] = None,
        connection_timeout: float = 30.0,
    ):
        """
        Initialize PromptCraft MCP client.
        
        Args:
            server_path: Path to zen-mcp-server executable  
            env_vars: Environment variables for server process
            fallback_config: HTTP fallback configuration
            connection_timeout: Connection timeout in seconds
        """
        # Configuration
        self.connection_config = MCPConnectionConfig(
            server_path=server_path,
            env_vars=env_vars or {},
            timeout=connection_timeout,
        )
        
        # Components
        self.process_pool = ProcessPool(self.connection_config)
        self.protocol_bridge = MCPProtocolBridge()
        self.connection_manager = MCPConnectionManager(
            fallback_config or FallbackConfig()
        )
        self.retry_handler = RetryHandler()
        
        # Connection state
        self.connected = False
        self.current_process: Optional[ZenMCPProcess] = None
        self._lock = asyncio.Lock()
        
        logger.info("✅ ZenMCPStdioClient initialized")

    async def connect(self) -> bool:
        """
        Establish connection to zen-mcp-server.
        
        Returns:
            bool: True if connection established successfully
        """
        async with self._lock:
            if self.connected and self.current_process and self.current_process.is_running():
                logger.debug("Already connected to zen-mcp-server")
                return True
            
            try:
                logger.info("Connecting to zen-mcp-server...")
                
                # Get process from pool
                self.current_process = await self.process_pool.get_process()
                if not self.current_process:
                    logger.error("Failed to start zen-mcp-server process")
                    return False
                
                # Test connection with a simple tool call
                test_successful = await self._test_connection()
                if test_successful:
                    self.connected = True
                    logger.info("✅ Successfully connected to zen-mcp-server")
                    return True
                else:
                    logger.error("Connection test failed")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to connect to zen-mcp-server: {e}")
                return False

    async def disconnect(self):
        """Disconnect from zen-mcp-server and cleanup resources."""
        async with self._lock:
            try:
                logger.info("Disconnecting from zen-mcp-server...")
                
                # Shutdown process pool
                await self.process_pool.shutdown_all()
                
                # Close connection manager
                await self.connection_manager.close()
                
                self.connected = False
                self.current_process = None
                
                logger.info("✅ Disconnected from zen-mcp-server")
                
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

    async def analyze_route(self, request: RouteAnalysisRequest) -> AnalysisResult:
        """
        Analyze prompt complexity and get model recommendations.
        
        Args:
            request: Route analysis request parameters
            
        Returns:
            AnalysisResult: Analysis results with recommendations
        """
        endpoint = "/api/promptcraft/route/analyze"
        request_data = request.dict()
        
        async def mcp_operation():
            mcp_call = self.protocol_bridge.http_to_mcp_request(endpoint, request_data)
            mcp_result = await self.call_tool(mcp_call.name, mcp_call.arguments)
            return self.protocol_bridge.mcp_to_http_response(endpoint, mcp_result)
        
        try:
            result, used_mcp = await self.connection_manager.with_fallback_to_http(
                mcp_operation, endpoint, request_data
            )
            
            return AnalysisResult(
                success=result.get("success", True),
                analysis=result.get("analysis"),
                recommendations=result.get("recommendations"),
                processing_time=result.get("processing_time", 0.0),
                error=result.get("error"),
            )
            
        except Exception as e:
            logger.error(f"Route analysis failed: {e}")
            return AnalysisResult(
                success=False,
                processing_time=0.0,
                error=str(e),
            )

    async def smart_execute(self, request: SmartExecutionRequest) -> ExecutionResult:
        """
        Execute prompt with smart model routing.
        
        Args:
            request: Smart execution request parameters
            
        Returns:
            ExecutionResult: Execution results with response
        """
        endpoint = "/api/promptcraft/execute/smart"
        request_data = request.dict()
        
        async def mcp_operation():
            mcp_call = self.protocol_bridge.http_to_mcp_request(endpoint, request_data)
            mcp_result = await self.call_tool(mcp_call.name, mcp_call.arguments)
            return self.protocol_bridge.mcp_to_http_response(endpoint, mcp_result)
        
        try:
            result, used_mcp = await self.connection_manager.with_fallback_to_http(
                mcp_operation, endpoint, request_data
            )
            
            return ExecutionResult(
                success=result.get("success", True),
                response=result.get("result"),  # Note: HTTP uses "result" key
                execution_metadata=result.get("execution_metadata"),
                processing_time=result.get("processing_time", 0.0),
                error=result.get("error"),
            )
            
        except Exception as e:
            logger.error(f"Smart execution failed: {e}")
            return ExecutionResult(
                success=False,
                processing_time=0.0,
                error=str(e),
            )

    async def list_models(self, request: ModelListRequest) -> ModelListResult:
        """
        Get available models for user tier.
        
        Args:
            request: Model list request parameters
            
        Returns:
            ModelListResult: Available models and metadata
        """
        endpoint = "/api/promptcraft/models/available"
        request_data = request.dict()
        
        async def mcp_operation():
            mcp_call = self.protocol_bridge.http_to_mcp_request(endpoint, request_data)
            mcp_result = await self.call_tool(mcp_call.name, mcp_call.arguments)
            return self.protocol_bridge.mcp_to_http_response(endpoint, mcp_result)
        
        try:
            result, used_mcp = await self.connection_manager.with_fallback_to_http(
                mcp_operation, endpoint, request_data
            )
            
            return ModelListResult(
                success=result.get("success", True),
                models=result.get("models"),
                metadata=result.get("metadata"),
                processing_time=result.get("processing_time", 0.0),
                error=result.get("error"),
            )
            
        except Exception as e:
            logger.error(f"Model listing failed: {e}")
            return ModelListResult(
                success=False,
                processing_time=0.0,
                error=str(e),
            )

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool directly.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Dict[str, Any]: Tool result
        """
        if not self.connected or not self.current_process:
            raise Exception("Not connected to zen-mcp-server")
        
        async def operation():
            return await self._send_mcp_request(tool_name, arguments)
        
        return await self.retry_handler.with_retry(operation, f"call_tool({tool_name})")

    async def _send_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send MCP tool call request via stdio.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Dict[str, Any]: Tool result
        """
        if not self.current_process or not self.current_process.process:
            raise Exception("No active server process")
        
        process = self.current_process.process
        
        # Create MCP request
        request_id = str(uuid.uuid4())
        mcp_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }
        
        try:
            # Send request
            request_json = json.dumps(mcp_request) + "\n"
            logger.debug(f"Sending MCP request: {request_json.strip()}")
            
            if process.stdin:
                process.stdin.write(request_json)
                process.stdin.flush()
            else:
                raise Exception("Process stdin not available")
            
            # Read response with timeout
            response_json = await asyncio.wait_for(
                self._read_response(process, request_id),
                timeout=self.connection_config.timeout,
            )
            
            logger.debug(f"Received MCP response: {response_json}")
            
            response = json.loads(response_json)
            
            # Check for errors
            if "error" in response:
                error_info = response["error"]
                raise Exception(f"MCP error {error_info.get('code', 'unknown')}: {error_info.get('message', 'Unknown error')}")
            
            # Extract result
            if "result" in response:
                return response["result"]
            else:
                raise Exception("No result in MCP response")
                
        except asyncio.TimeoutError:
            raise Exception(f"MCP request timeout after {self.connection_config.timeout}s")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in MCP response: {e}")
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            raise

    async def _read_response(self, process: Any, request_id: str) -> str:
        """
        Read MCP response from process stdout.
        
        Args:
            process: Subprocess instance
            request_id: Expected request ID
            
        Returns:
            str: Response JSON string
        """
        if not process.stdout:
            raise Exception("Process stdout not available")
        
        # Read response lines until we find our response
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, process.stdout.readline
                )
                
                if not line:
                    raise Exception("Process stdout closed unexpectedly")
                
                line = line.strip()
                if not line:
                    continue
                
                # Try to parse as JSON
                try:
                    response_data = json.loads(line)
                    if response_data.get("id") == request_id:
                        return line
                    # else: different request, keep reading
                except json.JSONDecodeError:
                    # Not JSON, might be log output, ignore
                    continue
                    
            except Exception as e:
                raise Exception(f"Error reading MCP response: {e}")

    async def _test_connection(self) -> bool:
        """Test MCP connection with a simple request."""
        try:
            # Test with listmodels tool
            result = await self.call_tool("listmodels", {"model": "flash"})
            logger.debug(f"Connection test result: {result}")
            return True
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False

    async def health_check(self) -> MCPHealthCheck:
        """
        Perform comprehensive health check.
        
        Returns:
            MCPHealthCheck: Health check results
        """
        return await self.connection_manager.health_check(self)

    def get_connection_status(self) -> MCPConnectionStatus:
        """Get current connection status."""
        if self.current_process:
            status = self.current_process.get_status()
            status.connected = self.connected
            return status
        else:
            return MCPConnectionStatus(connected=False)

    def get_metrics(self) -> BridgeMetrics:
        """Get performance metrics."""
        return self.connection_manager.get_metrics()

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.connected and self.current_process and self.current_process.is_running()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions for easy integration
async def create_client(
    server_path: str = "./server.py",
    env_vars: Optional[Dict[str, str]] = None,
    http_fallback_url: str = "http://localhost:8000",
) -> ZenMCPStdioClient:
    """
    Create and connect PromptCraft MCP client with sensible defaults.
    
    Args:
        server_path: Path to zen-mcp-server executable
        env_vars: Environment variables for server
        http_fallback_url: HTTP API base URL for fallback
        
    Returns:
        ZenMCPStdioClient: Connected client instance
    """
    fallback_config = FallbackConfig(
        enabled=True,
        http_base_url=http_fallback_url,
    )
    
    client = ZenMCPStdioClient(
        server_path=server_path,
        env_vars=env_vars,
        fallback_config=fallback_config,
    )
    
    await client.connect()
    return client