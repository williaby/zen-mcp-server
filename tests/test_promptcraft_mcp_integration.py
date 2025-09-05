"""
Integration tests for PromptCraft MCP Client Library

Tests the complete MCP stdio integration including client library,
bridge tool, subprocess management, and fallback mechanisms.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import bridge tool
from tools.custom.promptcraft_mcp_bridge import PromptCraftMCPBridgeTool

# Import PromptCraft MCP client components
from tools.custom.promptcraft_mcp_client import (
    FallbackConfig,
    MCPConnectionConfig,
    MCPConnectionManager,
    MCPProtocolBridge,
    RouteAnalysisRequest,
    ZenMCPProcess,
    ZenMCPStdioClient,
    create_client,
)


class TestMCPProtocolBridge:
    """Test the protocol bridge for HTTP to MCP translation."""

    def setup_method(self):
        """Setup protocol bridge for testing."""
        self.bridge = MCPProtocolBridge()

    def test_route_analysis_http_to_mcp(self):
        """Test converting route analysis HTTP request to MCP call."""
        http_request = {
            "prompt": "Write Python code to sort a list",
            "user_tier": "full",
            "task_type": "coding"
        }

        mcp_call = self.bridge.http_to_mcp_request("/api/promptcraft/route/analyze", http_request)

        assert mcp_call.name == "promptcraft_mcp_bridge"
        assert mcp_call.arguments["action"] == "analyze_route"
        assert mcp_call.arguments["prompt"] == "Write Python code to sort a list"
        assert mcp_call.arguments["user_tier"] == "full"
        assert mcp_call.arguments["task_type"] == "coding"

    def test_smart_execution_http_to_mcp(self):
        """Test converting smart execution HTTP request to MCP call."""
        http_request = {
            "prompt": "Enhanced prompt from Journey 1",
            "user_tier": "premium",
            "channel": "experimental",
            "cost_optimization": False,
            "include_reasoning": True,
        }

        mcp_call = self.bridge.http_to_mcp_request("/api/promptcraft/execute/smart", http_request)

        assert mcp_call.name == "promptcraft_mcp_bridge"
        assert mcp_call.arguments["action"] == "smart_execute"
        assert mcp_call.arguments["prompt"] == "Enhanced prompt from Journey 1"
        assert mcp_call.arguments["user_tier"] == "premium"
        assert mcp_call.arguments["channel"] == "experimental"
        assert mcp_call.arguments["cost_optimization"] is False

    def test_model_listing_http_to_mcp(self):
        """Test converting model listing HTTP request to MCP call."""
        http_request = {
            "user_tier": "limited",
            "channel": "stable",
            "include_metadata": True,
            "format": "api"
        }

        mcp_call = self.bridge.http_to_mcp_request("/api/promptcraft/models/available", http_request)

        assert mcp_call.name == "promptcraft_mcp_bridge"
        assert mcp_call.arguments["action"] == "list_models"
        assert mcp_call.arguments["user_tier"] == "limited"
        assert mcp_call.arguments["channel"] == "stable"
        assert mcp_call.arguments["format"] == "api"

    def test_mcp_to_http_response_route_analysis(self):
        """Test converting MCP result to HTTP response for route analysis."""
        mcp_result = {
            "content": [{
                "text": """PromptCraft MCP Bridge Result:

{
  "success": true,
  "analysis": {
    "task_type": "coding",
    "complexity_score": 0.7,
    "complexity_level": "medium",
    "indicators": ["code_generation", "algorithm"],
    "reasoning": "Code generation task with moderate complexity"
  },
  "recommendations": {
    "primary_model": "claude-3-5-sonnet-20241022",
    "alternative_models": ["gpt-4o", "claude-3-opus-20240229"],
    "estimated_cost": 0.02,
    "confidence": 0.88
  },
  "processing_time": 0.15,
  "bridge_version": "1.0.0"
}"""
            }]
        }

        http_response = self.bridge.mcp_to_http_response("/api/promptcraft/route/analyze", mcp_result)

        assert http_response["success"] is True
        assert http_response["analysis"]["task_type"] == "coding"
        assert http_response["analysis"]["complexity_score"] == 0.7
        assert http_response["recommendations"]["primary_model"] == "claude-3-5-sonnet-20241022"
        assert http_response["processing_time"] == 0.15

    def test_unsupported_endpoint_error(self):
        """Test error handling for unsupported endpoints."""
        with pytest.raises(ValueError, match="Unsupported endpoint"):
            self.bridge.http_to_mcp_request("/api/unknown/endpoint", {})

    def test_get_supported_endpoints(self):
        """Test getting list of supported endpoints."""
        endpoints = self.bridge.get_supported_endpoints()

        assert "/api/promptcraft/route/analyze" in endpoints
        assert "/api/promptcraft/execute/smart" in endpoints
        assert "/api/promptcraft/models/available" in endpoints
        assert len(endpoints) == 3


class TestPromptCraftMCPBridge:
    """Test the MCP bridge tool functionality."""

    def setup_method(self):
        """Setup MCP bridge tool for testing."""
        self.bridge_tool = PromptCraftMCPBridgeTool()

    def test_tool_initialization(self):
        """Test that bridge tool initializes correctly."""
        assert self.bridge_tool.get_name() == "promptcraft_mcp_bridge"
        assert "PromptCraft MCP Bridge" in self.bridge_tool.get_description()
        assert self.bridge_tool.chat_tool is not None
        assert self.bridge_tool.listmodels_tool is not None
        assert self.bridge_tool.dynamic_model_selector_tool is not None

    def test_get_tool_fields(self):
        """Test tool field definitions for MCP interface."""
        fields = self.bridge_tool.get_tool_fields()

        assert "action" in fields
        assert fields["action"]["enum"] == ["analyze_route", "smart_execute", "list_models"]
        assert "prompt" in fields
        assert "user_tier" in fields
        assert fields["user_tier"]["enum"] == ["free", "limited", "full", "premium", "admin"]

    def test_get_required_fields(self):
        """Test required field specification."""
        required = self.bridge_tool.get_required_fields()
        assert "action" in required
        assert len(required) == 1

    @pytest.mark.asyncio
    async def test_analyze_route_action(self):
        """Test route analysis action execution."""
        request = {
            "action": "analyze_route",
            "prompt": "Write Python code to sort a list",
            "user_tier": "full",
            "task_type": "coding",
            "model": "flash",
        }

        # Mock the dynamic model selector tool
        with patch.object(self.bridge_tool, '_call_internal_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"content": "Analysis completed successfully"}

            result = await self.bridge_tool._analyze_route_action(
                self.bridge_tool.get_request_model()(**request)
            )

            assert result["success"] is True
            assert "analysis" in result
            assert "recommendations" in result
            assert result["analysis"]["task_type"] == "coding"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_smart_execute_action(self):
        """Test smart execution action."""
        request = {
            "action": "smart_execute",
            "prompt": "Enhanced prompt from Journey 1",
            "user_tier": "premium",
            "channel": "experimental",
            "model": "auto",
        }

        with patch.object(self.bridge_tool, '_call_internal_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "content": "Execution completed successfully",
                "metadata": {"model": "claude-3-5-sonnet-20241022"}
            }

            result = await self.bridge_tool._smart_execute_action(
                self.bridge_tool.get_request_model()(**request)
            )

            assert result["success"] is True
            assert "response" in result
            assert "execution_metadata" in result
            assert result["execution_metadata"]["channel"] == "experimental"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_models_action(self):
        """Test model listing action."""
        request = {
            "action": "list_models",
            "user_tier": "limited",
            "channel": "stable",
            "include_metadata": True,
            "format": "api",
            "model": "flash",
        }

        with patch.object(self.bridge_tool, '_call_internal_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"content": "Models listed successfully"}

            result = await self.bridge_tool._list_models_action(
                self.bridge_tool.get_request_model()(**request)
            )

            assert result["success"] is True
            assert "models" in result
            assert "metadata" in result
            assert len(result["models"]) > 0  # Should have models for limited tier
            mock_call.assert_called_once()


class TestZenMCPProcess:
    """Test subprocess management functionality."""

    def setup_method(self):
        """Setup MCP process for testing."""
        self.config = MCPConnectionConfig(
            server_path="./server.py",
            env_vars={"LOG_LEVEL": "DEBUG"},
            timeout=10.0,
        )
        self.process = ZenMCPProcess(self.config)

    def test_process_initialization(self):
        """Test process initialization."""
        assert self.process.config == self.config
        assert self.process.process is None
        assert self.process.start_time is None
        assert self.process.error_count == 0

    def test_process_status_not_running(self):
        """Test getting status when process is not running."""
        status = self.process.get_status()
        assert status.connected is False
        assert status.process_id is None
        assert status.uptime is None
        assert status.error_count == 0

    @pytest.mark.asyncio
    async def test_health_check_not_running(self):
        """Test health check when process is not running."""
        is_healthy, error_msg = await self.process.health_check()
        assert is_healthy is False
        assert "not running" in error_msg

    def test_is_running_false(self):
        """Test is_running when process is not started."""
        assert self.process.is_running() is False

    def test_get_process_id_none(self):
        """Test getting process ID when not running."""
        assert self.process.get_process_id() is None

    def test_get_uptime_none(self):
        """Test getting uptime when not running."""
        assert self.process.get_uptime() is None


class TestMCPConnectionManager:
    """Test connection manager with fallback functionality."""

    def setup_method(self):
        """Setup connection manager for testing."""
        self.fallback_config = FallbackConfig(
            enabled=True,
            http_base_url="http://localhost:8000",
            circuit_breaker_threshold=3,
        )
        self.manager = MCPConnectionManager(self.fallback_config)

    def test_manager_initialization(self):
        """Test connection manager initialization."""
        assert self.manager.fallback_config == self.fallback_config
        assert self.manager.circuit_state.value == "closed"
        assert self.manager.failure_count == 0
        assert self.manager.metrics.total_requests == 0

    def test_circuit_breaker_closed_initially(self):
        """Test that circuit breaker starts in closed state."""
        assert self.manager._should_use_fallback() is False

    def test_record_failure_increments_count(self):
        """Test that recording failures increments counter."""
        initial_count = self.manager.failure_count
        self.manager._record_failure()
        assert self.manager.failure_count == initial_count + 1

    def test_record_success_resets_failure_count_in_half_open(self):
        """Test success in half-open state closes circuit."""
        # Simulate half-open state
        from tools.custom.promptcraft_mcp_client.error_handler import CircuitBreakerState
        self.manager.circuit_state = CircuitBreakerState.HALF_OPEN
        self.manager.failure_count = 2

        self.manager._record_success()

        assert self.manager.circuit_state == CircuitBreakerState.CLOSED
        assert self.manager.failure_count == 0

    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        # Record failures up to threshold
        for _ in range(self.fallback_config.circuit_breaker_threshold):
            self.manager._record_failure()

        from tools.custom.promptcraft_mcp_client.error_handler import CircuitBreakerState
        assert self.manager.circuit_state == CircuitBreakerState.OPEN

    def test_get_circuit_breaker_status(self):
        """Test getting circuit breaker status information."""
        status = self.manager.get_circuit_breaker_status()

        assert "state" in status
        assert "failure_count" in status
        assert "threshold" in status
        assert status["state"] == "closed"
        assert status["failure_count"] == 0
        assert status["threshold"] == 3

    @pytest.mark.asyncio
    async def test_reset_circuit_breaker(self):
        """Test manual circuit breaker reset."""
        # Force circuit breaker open
        self.manager.failure_count = 5
        from tools.custom.promptcraft_mcp_client.error_handler import CircuitBreakerState
        self.manager.circuit_state = CircuitBreakerState.OPEN

        await self.manager.reset_circuit_breaker()

        assert self.manager.circuit_state == CircuitBreakerState.CLOSED
        assert self.manager.failure_count == 0

    def test_get_metrics(self):
        """Test getting performance metrics."""
        metrics = self.manager.get_metrics()

        assert hasattr(metrics, 'total_requests')
        assert hasattr(metrics, 'successful_requests')
        assert hasattr(metrics, 'failed_requests')
        assert hasattr(metrics, 'mcp_requests')
        assert hasattr(metrics, 'http_fallback_requests')
        assert hasattr(metrics, 'average_latency_ms')


class TestZenMCPStdioClientIntegration:
    """Integration tests for the complete MCP client."""

    def setup_method(self):
        """Setup client for integration testing."""
        self.server_path = "./server.py"
        self.env_vars = {"LOG_LEVEL": "DEBUG"}
        self.fallback_config = FallbackConfig(
            enabled=True,
            http_base_url="http://localhost:8000",
        )

    @pytest.mark.asyncio
    async def test_client_creation_with_defaults(self):
        """Test creating client with default configuration."""
        client = ZenMCPStdioClient(self.server_path)

        assert client.connection_config.server_path == self.server_path
        assert client.protocol_bridge is not None
        assert client.connection_manager is not None
        assert client.connected is False

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as async context manager."""
        # Mock the connection process since we don't want to start actual server
        with patch('tools.custom.promptcraft_mcp_client.subprocess_manager.ProcessPool.get_process') as mock_get_process:
            mock_process = Mock()
            mock_process.is_running.return_value = True
            mock_get_process.return_value = mock_process

            with patch.object(ZenMCPStdioClient, '_test_connection', return_value=True):
                async with ZenMCPStdioClient(self.server_path) as client:
                    assert client.connected is True

                # Context manager should disconnect on exit
                # (But we can't easily test this with mocks)

    @pytest.mark.asyncio
    async def test_convenience_create_client_function(self):
        """Test convenience function for creating clients."""
        with patch('tools.custom.promptcraft_mcp_client.client.ZenMCPStdioClient.connect') as mock_connect:
            mock_connect.return_value = True

            client = await create_client(
                server_path=self.server_path,
                env_vars=self.env_vars,
                http_fallback_url="http://localhost:8000",
            )

            assert client is not None
            assert client.connection_config.server_path == self.server_path
            mock_connect.assert_called_once()

    def test_request_model_validation(self):
        """Test request model validation."""
        # Valid route analysis request
        valid_request = RouteAnalysisRequest(
            prompt="Test prompt",
            user_tier="full",
        )
        assert valid_request.prompt == "Test prompt"
        assert valid_request.user_tier == "full"

        # Invalid user tier should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            RouteAnalysisRequest(
                prompt="Test prompt",
                user_tier="invalid_tier",
            )

    @pytest.mark.asyncio
    async def test_analyze_route_with_mocked_backend(self):
        """Test route analysis with mocked backend."""
        client = ZenMCPStdioClient(self.server_path, fallback_config=self.fallback_config)

        # Mock the connection manager to return success
        mock_result = {
            "success": True,
            "analysis": {
                "task_type": "coding",
                "complexity_score": 0.7,
                "complexity_level": "medium",
                "indicators": ["code_generation"],
                "reasoning": "Code generation task"
            },
            "recommendations": {
                "primary_model": "claude-3-5-sonnet-20241022",
                "alternative_models": [],
                "estimated_cost": 0.02,
                "confidence": 0.85
            },
            "processing_time": 0.1
        }

        with patch.object(client.connection_manager, 'with_fallback_to_http') as mock_fallback:
            mock_fallback.return_value = (mock_result, True)

            request = RouteAnalysisRequest(
                prompt="Write Python code to sort a list",
                user_tier="full",
            )

            result = await client.analyze_route(request)

            assert result.success is True
            assert result.analysis is not None
            assert result.analysis["task_type"] == "coding"
            assert result.recommendations is not None
            assert result.processing_time == 0.1


class TestEndToEndMCPIntegration:
    """End-to-end integration tests (requires actual server)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_integration_with_bridge_tool(self):
        """Test full integration with actual bridge tool (requires server)."""
        # This test would require an actual zen-mcp-server instance
        # Skip by default, run only when specifically requested
        pytest.skip("Integration test requires running zen-mcp-server")

        # Example of what this test would do:
        # 1. Start zen-mcp-server with bridge tool loaded
        # 2. Create MCP client
        # 3. Test all three operations (analyze, execute, list_models)
        # 4. Verify responses match expected format
        # 5. Test fallback behavior by stopping server
        # 6. Cleanup


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
