# PromptCraft MCP Integration Guide

Complete guide for integrating PromptCraft applications with zen-mcp-server via native MCP stdio protocol.

## Overview

The PromptCraft MCP integration provides native MCP stdio support **alongside** the existing HTTP API, enabling:

- **20-30ms latency reduction** per request vs HTTP
- **Native MCP protocol** communication for better ecosystem alignment
- **Automatic HTTP fallback** on MCP failures for reliability
- **Gradual migration** from HTTP to MCP over time
- **Zero disruption** to existing HTTP integrations

## Architecture

```
PromptCraft Application
         |
         v
ZenMCPStdioClient (Python Library)
         |
         v
zen-mcp-server subprocess (stdio)
         |
         v
promptcraft_mcp_bridge (Custom Tool)
         |
         v
Internal Tools (chat, dynamic_model_selector, listmodels)
```

## Quick Start

### 1. Installation Requirements

The MCP client library is included with zen-mcp-server as a custom tool. No additional installation required.

**Dependencies:**
- Python 3.9+
- httpx (for HTTP fallback)
- pydantic (for data validation)

### 2. Basic Usage

```python
from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
from tools.custom.promptcraft_mcp_client.models import RouteAnalysisRequest

async def basic_example():
    # Create and connect client
    async with ZenMCPStdioClient("/path/to/zen-mcp-server/server.py") as client:
        
        # Analyze route
        request = RouteAnalysisRequest(
            prompt="Write Python code to sort a list",
            user_tier="full"
        )
        result = await client.analyze_route(request)
        
        print(f"Recommended model: {result.recommendations['primary_model']}")
        print(f"Processing time: {result.processing_time:.3f}s")
```

### 3. Convenience Function

```python
from tools.custom.promptcraft_mcp_client import create_client

async def convenient_example():
    # Create client with defaults
    client = await create_client(
        server_path="/path/to/zen-mcp-server/server.py",
        env_vars={"LOG_LEVEL": "INFO"},
        http_fallback_url="http://localhost:8000"
    )
    
    try:
        # Use client...
        pass
    finally:
        await client.disconnect()
```

## Core Operations

### Route Analysis

Analyze prompt complexity and get model recommendations:

```python
from tools.custom.promptcraft_mcp_client.models import RouteAnalysisRequest

request = RouteAnalysisRequest(
    prompt="Build a REST API with authentication",
    user_tier="premium",
    task_type="coding"  # Optional hint
)

result = await client.analyze_route(request)

if result.success:
    analysis = result.analysis
    recommendations = result.recommendations
    
    print(f"Task type: {analysis['task_type']}")
    print(f"Complexity: {analysis['complexity_level']}")
    print(f"Primary model: {recommendations['primary_model']}")
    print(f"Estimated cost: ${recommendations['estimated_cost']}")
else:
    print(f"Analysis failed: {result.error}")
```

### Smart Execution

Execute prompts with optimal model routing:

```python
from tools.custom.promptcraft_mcp_client.models import SmartExecutionRequest

request = SmartExecutionRequest(
    prompt="Enhanced prompt from Journey 1",
    user_tier="full",
    channel="stable",  # or "experimental"
    cost_optimization=True,
    include_reasoning=True
)

result = await client.smart_execute(request)

if result.success:
    response = result.response
    metadata = result.execution_metadata
    
    print(f"Response: {response['content']}")
    print(f"Model used: {response['model_used']}")
    print(f"Processing time: {metadata['processing_time']:.3f}s")
else:
    print(f"Execution failed: {result.error}")
```

### Model Listing

Get available models for user tiers:

```python
from tools.custom.promptcraft_mcp_client.models import ModelListRequest

request = ModelListRequest(
    user_tier="limited",
    channel="stable",
    include_metadata=True,
    format="ui"  # or "api"
)

result = await client.list_models(request)

if result.success:
    models = result.models
    metadata = result.metadata
    
    print(f"Available models for {metadata['user_tier']} tier:")
    for model in models:
        print(f"  - {model['name']} ({model['provider']})")
else:
    print(f"Model listing failed: {result.error}")
```

## Configuration

### Connection Configuration

```python
from tools.custom.promptcraft_mcp_client.models import MCPConnectionConfig

config = MCPConnectionConfig(
    server_path="/path/to/zen-mcp-server/server.py",
    env_vars={
        "LOG_LEVEL": "INFO",
        "OPENROUTER_API_KEY": "your-api-key",
    },
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
)

client = ZenMCPStdioClient(config.server_path, config.env_vars)
```

### Fallback Configuration

```python
from tools.custom.promptcraft_mcp_client.models import FallbackConfig

fallback_config = FallbackConfig(
    enabled=True,
    http_base_url="http://localhost:8000",
    fallback_timeout=10.0,
    circuit_breaker_threshold=5,
    circuit_breaker_reset_time=60.0,
)

client = ZenMCPStdioClient(
    server_path="./server.py",
    fallback_config=fallback_config
)
```

## Error Handling

### Automatic Fallback

The client automatically falls back to HTTP API on MCP failures:

```python
async def robust_operation():
    try:
        result = await client.analyze_route(request)
        # Result could come from MCP or HTTP fallback
        print(f"Success via {'MCP' if result.used_mcp else 'HTTP'}")
    except Exception as e:
        print(f"Both MCP and HTTP failed: {e}")
```

### Circuit Breaker Pattern

Monitor circuit breaker status:

```python
# Get circuit breaker status
status = client.connection_manager.get_circuit_breaker_status()
print(f"Circuit state: {status['state']}")
print(f"Failure count: {status['failure_count']}")

# Manually reset circuit breaker
if status['state'] == 'open':
    await client.connection_manager.reset_circuit_breaker()
```

### Health Monitoring

```python
# Perform health check
health = await client.health_check()
print(f"Healthy: {health.healthy}")
print(f"Latency: {health.latency_ms:.1f}ms")

if not health.healthy:
    print(f"Health issue: {health.error}")

# Get performance metrics
metrics = client.get_metrics()
print(f"Total requests: {metrics.total_requests}")
print(f"MCP success rate: {metrics.mcp_requests / metrics.total_requests * 100:.1f}%")
print(f"Average latency: {metrics.average_latency_ms:.1f}ms")
```

## Environment Variables

Configure zen-mcp-server behavior via environment variables:

```python
env_vars = {
    # API Keys
    "OPENROUTER_API_KEY": "your-openrouter-key",
    "ANTHROPIC_API_KEY": "your-anthropic-key",
    
    # Logging
    "LOG_LEVEL": "INFO",  # DEBUG, INFO, WARNING, ERROR
    
    # Model Selection
    "DEFAULT_MODEL": "claude-3-5-sonnet-20241022",
    
    # Performance
    "MCP_TIMEOUT": "30.0",
    "MAX_CONCURRENT_REQUESTS": "10",
}

client = ZenMCPStdioClient("./server.py", env_vars=env_vars)
```

## Migration from HTTP API

### Gradual Migration Pattern

```python
import os

# Use feature flag to control MCP vs HTTP usage
USE_MCP_STDIO = os.getenv("USE_MCP_STDIO", "false").lower() == "true"

if USE_MCP_STDIO:
    # Use MCP client
    from tools.custom.promptcraft_mcp_client import create_client
    client = await create_client()
    result = await client.analyze_route(request)
else:
    # Use existing HTTP client
    import httpx
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post("/api/promptcraft/route/analyze", json=request.dict())
        result = response.json()
```

### Traffic Splitting

```python
import random

# Route percentage of traffic to MCP
MCP_TRAFFIC_PERCENTAGE = int(os.getenv("MCP_TRAFFIC_PERCENTAGE", "10"))

async def smart_routing():
    if random.randint(1, 100) <= MCP_TRAFFIC_PERCENTAGE:
        # Route to MCP
        async with ZenMCPStdioClient("./server.py") as client:
            return await client.analyze_route(request)
    else:
        # Route to HTTP
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post("/api/promptcraft/route/analyze", json=request.dict())
            return response.json()
```

## Best Practices

### 1. Connection Reuse

```python
# Good: Reuse connection across requests
async def efficient_usage():
    async with ZenMCPStdioClient("./server.py") as client:
        # Multiple operations with same client
        result1 = await client.analyze_route(request1)
        result2 = await client.smart_execute(request2)
        result3 = await client.list_models(request3)

# Bad: Create new connection per request
async def inefficient_usage():
    async with ZenMCPStdioClient("./server.py") as client1:
        result1 = await client1.analyze_route(request1)
    async with ZenMCPStdioClient("./server.py") as client2:
        result2 = await client2.smart_execute(request2)
```

### 2. Error Handling

```python
from tools.custom.promptcraft_mcp_client.models import AnalysisResult

async def robust_error_handling():
    try:
        result = await client.analyze_route(request)
        
        if result.success:
            # Process successful result
            return result.analysis
        else:
            # Handle business logic errors
            logger.warning(f"Analysis failed: {result.error}")
            return None
            
    except Exception as e:
        # Handle connection/system errors
        logger.error(f"System error: {e}")
        raise
```

### 3. Resource Cleanup

```python
# Always use context managers or explicit cleanup
async def proper_cleanup():
    client = ZenMCPStdioClient("./server.py")
    try:
        await client.connect()
        # Use client...
    finally:
        await client.disconnect()

# Or use context manager (preferred)
async def context_manager_cleanup():
    async with ZenMCPStdioClient("./server.py") as client:
        # Use client...
        pass  # Automatic cleanup on exit
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```python
   # Increase timeout for slow environments
   client = ZenMCPStdioClient("./server.py", connection_timeout=60.0)
   ```

2. **Server Path Not Found**
   ```python
   # Use absolute paths
   import os
   server_path = os.path.abspath("./server.py")
   client = ZenMCPStdioClient(server_path)
   ```

3. **Environment Variable Issues**
   ```python
   # Verify environment variables are passed
   env_vars = {
       "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
       "LOG_LEVEL": "DEBUG",  # Enable debug logging
   }
   # Check that API key is not None
   if not env_vars["OPENROUTER_API_KEY"]:
       raise ValueError("OPENROUTER_API_KEY environment variable not set")
   ```

### Debug Logging

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging for MCP client
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tools.custom.promptcraft_mcp_client")
logger.setLevel(logging.DEBUG)

# Create client with debug environment
client = ZenMCPStdioClient(
    "./server.py",
    env_vars={"LOG_LEVEL": "DEBUG"}
)
```

## Performance Considerations

### Latency Comparison

| Operation | HTTP API | MCP stdio | Improvement |
|-----------|----------|-----------|-------------|
| Route Analysis | ~50ms | ~20ms | 60% faster |
| Smart Execution | ~200ms | ~170ms | 15% faster |
| Model Listing | ~30ms | ~10ms | 67% faster |

### Memory Usage

- **MCP Client**: ~10-20MB additional memory for subprocess
- **HTTP Client**: ~2-5MB for HTTP connection pool
- **Trade-off**: Slightly higher memory for significantly better latency

### Concurrent Requests

```python
import asyncio

async def concurrent_requests():
    async with ZenMCPStdioClient("./server.py") as client:
        # Execute multiple requests concurrently
        tasks = [
            client.analyze_route(request1),
            client.smart_execute(request2), 
            client.list_models(request3),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Request {i} failed: {result}")
            else:
                print(f"Request {i} succeeded")
```

## Next Steps

1. **Integration Testing**: See [mcp-client-api.md](./mcp-client-api.md) for detailed API reference
2. **Migration Planning**: See [migration-guide.md](./migration-guide.md) for step-by-step migration
3. **Performance Benchmarking**: See [performance-benchmarks.md](./performance-benchmarks.md) for detailed metrics
4. **Production Deployment**: See [troubleshooting.md](./troubleshooting.md) for production considerations

## Support

For questions or issues:
1. Check the [troubleshooting guide](./troubleshooting.md)
2. Review integration test examples in `/tests/test_promptcraft_mcp_integration.py`
3. Enable debug logging for detailed diagnostics
4. Contact the zen-mcp-server development team