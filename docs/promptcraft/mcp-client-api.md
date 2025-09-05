# PromptCraft MCP Client API Reference

Complete API reference for the PromptCraft MCP client library.

## Table of Contents

- [Client Classes](#client-classes)
- [Request/Response Models](#requestresponse-models)
- [Configuration Models](#configuration-models)
- [Error Handling](#error-handling)
- [Utility Functions](#utility-functions)

## Client Classes

### ZenMCPStdioClient

Main client class for MCP stdio communication with zen-mcp-server.

#### Constructor

```python
ZenMCPStdioClient(
    server_path: str,
    env_vars: Optional[Dict[str, str]] = None,
    fallback_config: Optional[FallbackConfig] = None,
    connection_timeout: float = 30.0,
)
```

**Parameters:**
- `server_path`: Path to zen-mcp-server executable
- `env_vars`: Environment variables for server process
- `fallback_config`: HTTP fallback configuration
- `connection_timeout`: Connection timeout in seconds

#### Methods

##### `async connect() -> bool`

Establish connection to zen-mcp-server.

**Returns:** `bool` - True if connection established successfully

**Example:**
```python
client = ZenMCPStdioClient("./server.py")
success = await client.connect()
if success:
    print("Connected successfully")
```

##### `async disconnect() -> None`

Disconnect from zen-mcp-server and cleanup resources.

**Example:**
```python
await client.disconnect()
```

##### `async analyze_route(request: RouteAnalysisRequest) -> AnalysisResult`

Analyze prompt complexity and get model recommendations.

**Parameters:**
- `request`: Route analysis parameters

**Returns:** `AnalysisResult` - Analysis results with recommendations

**Example:**
```python
request = RouteAnalysisRequest(
    prompt="Build a web scraper",
    user_tier="premium",
    task_type="coding"
)
result = await client.analyze_route(request)
```

##### `async smart_execute(request: SmartExecutionRequest) -> ExecutionResult`

Execute prompt with smart model routing.

**Parameters:**
- `request`: Smart execution parameters

**Returns:** `ExecutionResult` - Execution results with response

**Example:**
```python
request = SmartExecutionRequest(
    prompt="Enhanced prompt from Journey 1",
    user_tier="full",
    channel="stable"
)
result = await client.smart_execute(request)
```

##### `async list_models(request: ModelListRequest) -> ModelListResult`

Get available models for user tier.

**Parameters:**
- `request`: Model list parameters

**Returns:** `ModelListResult` - Available models and metadata

**Example:**
```python
request = ModelListRequest(
    user_tier="limited",
    channel="stable"
)
result = await client.list_models(request)
```

##### `async call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

Call an MCP tool directly.

**Parameters:**
- `tool_name`: Name of the tool to call
- `arguments`: Tool arguments

**Returns:** `Dict[str, Any]` - Tool result

**Example:**
```python
result = await client.call_tool("promptcraft_mcp_bridge", {
    "action": "analyze_route",
    "prompt": "Test prompt",
    "user_tier": "full"
})
```

##### `async health_check() -> MCPHealthCheck`

Perform comprehensive health check.

**Returns:** `MCPHealthCheck` - Health check results

##### `get_connection_status() -> MCPConnectionStatus`

Get current connection status.

**Returns:** `MCPConnectionStatus` - Connection status information

##### `get_metrics() -> BridgeMetrics`

Get performance metrics.

**Returns:** `BridgeMetrics` - Performance metrics

##### `is_connected() -> bool`

Check if client is connected.

**Returns:** `bool` - True if connected

#### Context Manager Support

```python
async with ZenMCPStdioClient("./server.py") as client:
    # Client is automatically connected
    result = await client.analyze_route(request)
    # Client is automatically disconnected on exit
```

## Request/Response Models

### RouteAnalysisRequest

Request model for route analysis operations.

```python
RouteAnalysisRequest(
    prompt: str,
    user_tier: str,
    task_type: Optional[str] = None
)
```

**Fields:**
- `prompt`: The prompt to analyze (required)
- `user_tier`: User tier: "free", "limited", "full", "premium", "admin" (required)
- `task_type`: Optional task type hint

### SmartExecutionRequest

Request model for smart execution operations.

```python
SmartExecutionRequest(
    prompt: str,
    user_tier: str,
    channel: str = "stable",
    cost_optimization: bool = True,
    include_reasoning: bool = True
)
```

**Fields:**
- `prompt`: The enhanced prompt from Journey 1 (required)
- `user_tier`: User tier (required)
- `channel`: Model channel: "stable" or "experimental" (default: "stable")
- `cost_optimization`: Enable cost optimization (default: True)
- `include_reasoning`: Include reasoning in response (default: True)

### ModelListRequest

Request model for model listing operations.

```python
ModelListRequest(
    user_tier: Optional[str] = None,
    channel: str = "stable",
    include_metadata: bool = True,
    format: str = "ui"
)
```

**Fields:**
- `user_tier`: Filter by user tier (optional)
- `channel`: Model channel (default: "stable")
- `include_metadata`: Include detailed metadata (default: True)
- `format`: Response format: "ui" or "api" (default: "ui")

### AnalysisResult

Response model for route analysis results.

```python
class AnalysisResult(BaseModel):
    success: bool
    analysis: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    processing_time: float
    error: Optional[str]
```

**Fields:**
- `success`: Whether analysis was successful
- `analysis`: Analysis details (if successful)
  - `task_type`: Detected task type
  - `complexity_score`: Complexity score (0.0-1.0)
  - `complexity_level`: "low", "medium", "high", "critical"
  - `indicators`: List of complexity indicators
  - `reasoning`: Analysis reasoning
- `recommendations`: Model recommendations (if successful)
  - `primary_model`: Recommended primary model
  - `alternative_models`: List of alternative models
  - `estimated_cost`: Estimated cost in USD
  - `confidence`: Confidence score (0.0-1.0)
- `processing_time`: Processing time in seconds
- `error`: Error message (if failed)

### ExecutionResult

Response model for smart execution results.

```python
class ExecutionResult(BaseModel):
    success: bool
    response: Optional[Dict[str, Any]]
    execution_metadata: Optional[Dict[str, Any]]
    processing_time: float
    error: Optional[str]
```

**Fields:**
- `success`: Whether execution was successful
- `response`: Execution response (if successful)
  - `content`: Generated content
  - `model_used`: Model that was used
  - `reasoning`: Reasoning (if requested)
- `execution_metadata`: Execution metadata (if successful)
  - `channel`: Channel used
  - `cost_optimization`: Whether cost optimization was enabled
  - `processing_time`: Processing time
- `processing_time`: Total processing time in seconds
- `error`: Error message (if failed)

### ModelListResult

Response model for model listing results.

```python
class ModelListResult(BaseModel):
    success: bool
    models: Optional[List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]]
    processing_time: float
    error: Optional[str]
```

**Fields:**
- `success`: Whether listing was successful
- `models`: List of available models (if successful)
  - Each model has: `id`, `name`, `provider`, `tier`, `channel`, `available`
- `metadata`: Response metadata (if successful)
  - `user_tier`: User tier filter applied
  - `channel`: Channel filter applied
  - `total_models`: Total number of models
- `processing_time`: Processing time in seconds
- `error`: Error message (if failed)

## Configuration Models

### MCPConnectionConfig

Configuration for MCP stdio connection.

```python
MCPConnectionConfig(
    server_path: str,
    env_vars: Dict[str, str] = {},
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0
)
```

### FallbackConfig

Configuration for HTTP fallback behavior.

```python
FallbackConfig(
    enabled: bool = True,
    http_base_url: str = "http://localhost:8000",
    fallback_timeout: float = 10.0,
    circuit_breaker_threshold: int = 5,
    circuit_breaker_reset_time: float = 60.0
)
```

### MCPConnectionStatus

Status information for MCP connection.

```python
class MCPConnectionStatus(BaseModel):
    connected: bool
    process_id: Optional[int]
    uptime: Optional[float]
    last_activity: Optional[datetime]
    error_count: int
```

### MCPHealthCheck

Health check result for MCP connection.

```python
class MCPHealthCheck(BaseModel):
    healthy: bool
    latency_ms: Optional[float]
    server_version: Optional[str]
    available_tools: Optional[List[str]]
    error: Optional[str]
```

### BridgeMetrics

Performance metrics for MCP bridge.

```python
class BridgeMetrics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    mcp_requests: int
    http_fallback_requests: int
    average_latency_ms: float
    last_request_time: Optional[datetime]
    uptime: float
```

## Error Handling

### Exception Types

The client raises standard Python exceptions:

- `Exception`: Generic errors (connection failures, validation errors)
- `asyncio.TimeoutError`: Timeout errors
- `json.JSONDecodeError`: JSON parsing errors
- `ValidationError`: Pydantic validation errors

### Circuit Breaker States

```python
from tools.custom.promptcraft_mcp_client.error_handler import CircuitBreakerState

# States:
# CircuitBreakerState.CLOSED - Normal operation
# CircuitBreakerState.OPEN - Failing, using fallback
# CircuitBreakerState.HALF_OPEN - Testing recovery
```

### Error Recovery

```python
# Check circuit breaker status
status = client.connection_manager.get_circuit_breaker_status()
if status['state'] == 'open':
    # Manually reset if needed
    await client.connection_manager.reset_circuit_breaker()

# Health check with recovery
health = await client.health_check()
if not health.healthy:
    # Attempt reconnection
    await client.disconnect()
    await client.connect()
```

## Utility Functions

### create_client()

Convenience function for creating and connecting MCP clients.

```python
async def create_client(
    server_path: str = "./server.py",
    env_vars: Optional[Dict[str, str]] = None,
    http_fallback_url: str = "http://localhost:8000",
) -> ZenMCPStdioClient
```

**Parameters:**
- `server_path`: Path to zen-mcp-server executable
- `env_vars`: Environment variables for server
- `http_fallback_url`: HTTP API base URL for fallback

**Returns:** Connected `ZenMCPStdioClient` instance

**Example:**
```python
client = await create_client(
    server_path="/path/to/server.py",
    env_vars={"LOG_LEVEL": "INFO"},
    http_fallback_url="http://localhost:8000"
)

try:
    # Use client...
    result = await client.analyze_route(request)
finally:
    await client.disconnect()
```

## Advanced Usage

### Direct Tool Calls

For advanced use cases, call MCP tools directly:

```python
# Direct bridge tool call
result = await client.call_tool("promptcraft_mcp_bridge", {
    "action": "analyze_route",
    "prompt": "Test prompt",
    "user_tier": "full",
    "task_type": "coding",
    "model": "flash"
})

# Direct internal tool call
result = await client.call_tool("chat", {
    "prompt": "Hello, world!",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.7
})
```

### Custom Error Handling

```python
from tools.custom.promptcraft_mcp_client.error_handler import MCPConnectionManager

# Create custom connection manager
custom_fallback = FallbackConfig(
    circuit_breaker_threshold=10,  # Higher threshold
    circuit_breaker_reset_time=30.0,  # Faster reset
)

client = ZenMCPStdioClient(
    "./server.py",
    fallback_config=custom_fallback
)

# Monitor circuit breaker
async def monitor_circuit_breaker():
    while True:
        status = client.connection_manager.get_circuit_breaker_status()
        print(f"Circuit state: {status['state']}, failures: {status['failure_count']}")
        await asyncio.sleep(10)
```

### Performance Monitoring

```python
# Collect detailed metrics
async def performance_monitoring():
    start_time = time.time()
    
    # Perform operations
    result1 = await client.analyze_route(request1)
    result2 = await client.smart_execute(request2)
    
    # Get metrics
    metrics = client.get_metrics()
    total_time = time.time() - start_time
    
    print(f"Operations completed in {total_time:.3f}s")
    print(f"Average latency: {metrics.average_latency_ms:.1f}ms")
    print(f"Success rate: {metrics.successful_requests/metrics.total_requests*100:.1f}%")
    print(f"MCP vs HTTP: {metrics.mcp_requests}:{metrics.http_fallback_requests}")
```

## Type Annotations

The library is fully typed with Pydantic models and type hints:

```python
from typing import Dict, List, Optional, Any
from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
from tools.custom.promptcraft_mcp_client.models import (
    RouteAnalysisRequest,
    AnalysisResult,
)

async def typed_function(client: ZenMCPStdioClient) -> Optional[Dict[str, Any]]:
    request: RouteAnalysisRequest = RouteAnalysisRequest(
        prompt="Test",
        user_tier="full"
    )
    
    result: AnalysisResult = await client.analyze_route(request)
    
    if result.success:
        return result.analysis
    else:
        return None
```