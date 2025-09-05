# PromptCraft MCP Integration Troubleshooting

Common issues and solutions for PromptCraft MCP stdio integration.

## Quick Diagnostics

### 1. Verify Installation

```python
# Test 1: Check MCP client library availability
try:
    from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
    print("✅ MCP client library available")
except ImportError as e:
    print(f"❌ MCP client library not found: {e}")

# Test 2: Check bridge tool availability  
try:
    from tools.custom.promptcraft_mcp_bridge import PromptCraftMCPBridgeTool
    bridge = PromptCraftMCPBridgeTool()
    print("✅ MCP bridge tool available")
    print(f"Bridge tool name: {bridge.get_name()}")
except Exception as e:
    print(f"❌ MCP bridge tool error: {e}")

# Test 3: Check zen-mcp-server availability
import os
from pathlib import Path

server_path = Path("./server.py")
if server_path.exists():
    print(f"✅ zen-mcp-server found at {server_path.absolute()}")
else:
    print(f"❌ zen-mcp-server not found at {server_path.absolute()}")
```

### 2. Connection Test

```python
# Basic connection test
import asyncio
from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient

async def test_connection():
    try:
        client = ZenMCPStdioClient("./server.py", connection_timeout=10.0)
        success = await client.connect()
        
        if success:
            print("✅ MCP connection successful")
            
            # Test health check
            health = await client.health_check()
            print(f"Health status: {'✅ Healthy' if health.healthy else '❌ Unhealthy'}")
            if health.error:
                print(f"Health error: {health.error}")
                
        else:
            print("❌ MCP connection failed")
            
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

# Run test
asyncio.run(test_connection())
```

## Common Issues

### 1. Server Process Won't Start

**Symptoms:**
- Connection timeout errors
- "Process terminated immediately" messages
- "Server executable not found" errors

**Causes & Solutions:**

#### Issue: Server Path Not Found
```python
# Problem: Relative path not resolving
client = ZenMCPStdioClient("./server.py")  # May not work

# Solution: Use absolute path
import os
server_path = os.path.abspath("./server.py")
client = ZenMCPStdioClient(server_path)

# Or: Verify current working directory
print(f"Current directory: {os.getcwd()}")
print(f"Server exists: {os.path.exists('./server.py')}")
```

#### Issue: Python Environment Problems
```python
# Problem: Wrong Python interpreter
# Solution: Check virtual environment

# Check if in virtual environment
import sys
if hasattr(sys, 'prefix') and hasattr(sys, 'base_prefix'):
    if sys.prefix != sys.base_prefix:
        print("✅ In virtual environment")
    else:
        print("❌ Not in virtual environment")

# Check Python path
print(f"Python executable: {sys.executable}")

# Solution: Activate correct environment
# In shell: source .zen_venv/bin/activate
# Or: Use specific Python path in configuration
```

#### Issue: Missing Dependencies
```bash
# Check for required packages
pip list | grep -E "(mcp|pydantic|httpx)"

# Install missing dependencies  
pip install pydantic httpx

# Or check requirements.txt
pip install -r requirements.txt
```

#### Issue: Permission Problems
```bash
# Check file permissions
ls -la server.py
# Should be readable and executable

# Fix permissions if needed
chmod +x server.py
```

### 2. Environment Variable Issues

**Symptoms:**
- API authentication failures
- "API key not found" errors
- Server starts but tool calls fail

**Solutions:**

```python
# Debug environment variables
import os

required_vars = [
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY", 
    "LOG_LEVEL",
]

print("Environment Variables Check:")
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask API keys for security
        if "API_KEY" in var:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: Not set")

# Solution: Pass environment variables to client
env_vars = {
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "LOG_LEVEL": "DEBUG",  # Enable debug logging
}

# Filter out None values
env_vars = {k: v for k, v in env_vars.items() if v is not None}

client = ZenMCPStdioClient("./server.py", env_vars=env_vars)
```

### 3. Timeout and Performance Issues

**Symptoms:**
- "Request timeout" errors
- Slow response times
- Circuit breaker opening frequently

**Solutions:**

#### Increase Timeouts
```python
from tools.custom.promptcraft_mcp_client.models import MCPConnectionConfig, FallbackConfig

# Increase connection timeout
client = ZenMCPStdioClient(
    "./server.py",
    connection_timeout=60.0  # Increase from default 30s
)

# Configure fallback with longer timeouts
fallback_config = FallbackConfig(
    fallback_timeout=20.0,  # Increase HTTP fallback timeout
    circuit_breaker_threshold=10,  # Higher failure threshold
    circuit_breaker_reset_time=120.0,  # Longer recovery time
)

client = ZenMCPStdioClient(
    "./server.py",
    fallback_config=fallback_config
)
```

#### Optimize for Performance
```python
# Reduce logging overhead
env_vars = {
    "LOG_LEVEL": "WARNING",  # Less verbose logging
}

# Use connection pooling (reuse client)
async def efficient_usage():
    async with ZenMCPStdioClient("./server.py", env_vars=env_vars) as client:
        # Multiple operations with same client
        results = []
        for prompt in prompts:
            result = await client.analyze_route(prompt, "full")
            results.append(result)
        return results
```

#### Monitor Performance
```python
# Performance monitoring
import time

async def monitored_request():
    client = ZenMCPStdioClient("./server.py")
    
    try:
        await client.connect()
        
        start_time = time.time()
        result = await client.analyze_route("Test prompt", "full")
        end_time = time.time()
        
        print(f"Request completed in {(end_time - start_time)*1000:.1f}ms")
        
        # Check metrics
        metrics = client.get_metrics()
        print(f"Average latency: {metrics.average_latency_ms:.1f}ms")
        print(f"Success rate: {metrics.successful_requests/metrics.total_requests*100:.1f}%")
        
    finally:
        await client.disconnect()
```

### 4. Circuit Breaker and Fallback Issues

**Symptoms:**
- "Circuit breaker open" messages
- Unexpected HTTP fallback usage
- Inconsistent response formats

**Solutions:**

#### Check Circuit Breaker Status
```python
async def debug_circuit_breaker():
    client = ZenMCPStdioClient("./server.py")
    await client.connect()
    
    # Get circuit breaker status
    status = client.connection_manager.get_circuit_breaker_status()
    print(f"Circuit breaker state: {status['state']}")
    print(f"Failure count: {status['failure_count']}/{status['threshold']}")
    
    if status['state'] == 'open':
        print(f"Next attempt at: {status['next_attempt_time']}")
        
        # Manual reset if needed
        await client.connection_manager.reset_circuit_breaker()
        print("Circuit breaker manually reset")
    
    await client.disconnect()
```

#### Verify Fallback Configuration
```python
# Test HTTP fallback directly
import httpx

async def test_http_fallback():
    try:
        async with httpx.AsyncClient(base_url="http://localhost:8000") as http_client:
            response = await http_client.get("/health")
            print(f"HTTP API health: {response.status_code}")
            
            # Test actual endpoint
            response = await http_client.post("/api/promptcraft/route/analyze", json={
                "prompt": "Test",
                "user_tier": "full"
            })
            print(f"HTTP API response: {response.status_code}")
            
    except Exception as e:
        print(f"HTTP API not available: {e}")

asyncio.run(test_http_fallback())
```

### 5. JSON and Protocol Issues

**Symptoms:**
- "Invalid JSON in MCP response" errors
- "No result in MCP response" errors
- Response parsing failures

**Solutions:**

#### Enable Debug Logging
```python
import logging

# Enable debug logging for MCP communication
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tools.custom.promptcraft_mcp_client")
logger.setLevel(logging.DEBUG)

# Create client with debug mode
client = ZenMCPStdioClient(
    "./server.py",
    env_vars={"LOG_LEVEL": "DEBUG"}
)
```

#### Test Raw Tool Calls
```python
# Test direct tool calls to isolate issues
async def debug_tool_calls():
    async with ZenMCPStdioClient("./server.py") as client:
        try:
            # Test basic tool call
            result = await client.call_tool("listmodels", {"model": "flash"})
            print(f"listmodels result: {result}")
            
            # Test bridge tool directly
            result = await client.call_tool("promptcraft_mcp_bridge", {
                "action": "list_models",
                "user_tier": "full",
                "model": "flash"
            })
            print(f"Bridge tool result: {result}")
            
        except Exception as e:
            print(f"Tool call failed: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(debug_tool_calls())
```

### 6. Import and Module Issues

**Symptoms:**
- "Module not found" errors
- "Import error" messages
- Tool discovery failures

**Solutions:**

#### Check Python Path
```python
import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

# Check if zen-mcp-server directory is in path
project_root = "/path/to/zen-mcp-server"
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

#### Verify Tool Discovery
```python
# Test tool discovery
try:
    from tools.custom import get_custom_tools
    custom_tools = get_custom_tools()
    print(f"Discovered custom tools: {list(custom_tools.keys())}")
    
    if "promptcraft_mcp_bridge" in custom_tools:
        print("✅ Bridge tool discovered")
    else:
        print("❌ Bridge tool not found")
        
except Exception as e:
    print(f"Tool discovery failed: {e}")
```

## Debug Scripts

### Complete Diagnostic Script

```python
#!/usr/bin/env python3
"""
PromptCraft MCP Integration Diagnostic Script

Run this script to diagnose common integration issues.
"""

import asyncio
import os
import sys
import time
import traceback
from pathlib import Path


async def run_diagnostics():
    """Run comprehensive diagnostics."""
    
    print("🔍 PromptCraft MCP Integration Diagnostics")
    print("=" * 50)
    
    # 1. Environment Check
    print("\n1. Environment Check")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    # 2. File System Check  
    print("\n2. File System Check")
    server_path = Path("./server.py")
    print(f"Server path exists: {server_path.exists()}")
    if server_path.exists():
        print(f"Server path: {server_path.absolute()}")
        print(f"Server permissions: {oct(server_path.stat().st_mode)[-3:]}")
    
    # 3. Module Import Check
    print("\n3. Module Import Check")
    try:
        from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
        print("✅ MCP client import successful")
    except ImportError as e:
        print(f"❌ MCP client import failed: {e}")
        return
    
    try:
        from tools.custom.promptcraft_mcp_bridge import PromptCraftMCPBridgeTool
        print("✅ Bridge tool import successful")
    except ImportError as e:
        print(f"❌ Bridge tool import failed: {e}")
        return
    
    # 4. Environment Variables Check
    print("\n4. Environment Variables Check")
    required_vars = ["OPENROUTER_API_KEY", "ANTHROPIC_API_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set (length: {len(value)})")
        else:
            print(f"⚠️ {var}: Not set")
    
    # 5. Connection Test
    print("\n5. Connection Test")
    try:
        client = ZenMCPStdioClient("./server.py", connection_timeout=20.0)
        
        print("Attempting to connect...")
        start_time = time.time()
        success = await client.connect()
        connect_time = time.time() - start_time
        
        if success:
            print(f"✅ Connection successful ({connect_time:.2f}s)")
            
            # Health check
            health = await client.health_check()
            print(f"Health: {'✅' if health.healthy else '❌'} {health.latency_ms:.1f}ms")
            
            # Tool call test
            try:
                result = await client.call_tool("listmodels", {"model": "flash"})
                print("✅ Basic tool call successful")
            except Exception as e:
                print(f"❌ Tool call failed: {e}")
            
            # Bridge tool test
            try:
                result = await client.call_tool("promptcraft_mcp_bridge", {
                    "action": "list_models",
                    "user_tier": "full",
                    "model": "flash"
                })
                print("✅ Bridge tool call successful")
            except Exception as e:
                print(f"❌ Bridge tool call failed: {e}")
        
        else:
            print("❌ Connection failed")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        traceback.print_exc()
    
    # 6. Performance Test
    print("\n6. Performance Test")
    try:
        async with ZenMCPStdioClient("./server.py") as client:
            # Test route analysis
            from tools.custom.promptcraft_mcp_client.models import RouteAnalysisRequest
            
            request = RouteAnalysisRequest(
                prompt="Test diagnostic prompt",
                user_tier="full"
            )
            
            start_time = time.time()
            result = await client.analyze_route(request)
            end_time = time.time()
            
            if result.success:
                print(f"✅ Route analysis: {(end_time-start_time)*1000:.1f}ms")
            else:
                print(f"❌ Route analysis failed: {result.error}")
                
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnostics complete!")


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
```

Save as `scripts/diagnose_mcp.py` and run:
```bash
python scripts/diagnose_mcp.py
```

## Getting Help

### 1. Enable Debug Logging

Always start troubleshooting with debug logging:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Collect Debug Information

```python
# Collect comprehensive debug info
async def collect_debug_info():
    info = {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": dict(os.environ),
        "server_path_exists": Path("./server.py").exists(),
    }
    
    try:
        async with ZenMCPStdioClient("./server.py") as client:
            info["connection_status"] = client.get_connection_status().dict()
            info["metrics"] = client.get_metrics().dict()
            info["circuit_breaker"] = client.connection_manager.get_circuit_breaker_status()
    except Exception as e:
        info["connection_error"] = str(e)
    
    return info
```

### 3. Contact Support

When contacting support, include:
1. Output from diagnostic script
2. Debug logs from failed operations
3. Environment details (Python version, OS, etc.)
4. Configuration being used
5. Expected vs actual behavior

### 4. Community Resources

- **Integration Tests**: `tests/test_promptcraft_mcp_integration.py`
- **Example Usage**: `docs/promptcraft/mcp-integration-guide.md`
- **API Reference**: `docs/promptcraft/mcp-client-api.md`
- **Migration Guide**: `docs/promptcraft/migration-guide.md`

## Common Error Messages

### "Process terminated immediately"
- **Cause**: Server script syntax error or missing dependencies
- **Solution**: Run `python server.py` directly to see error details

### "Connection timeout"
- **Cause**: Server taking too long to start or unresponsive
- **Solution**: Increase timeout, check server logs, verify dependencies

### "Circuit breaker open"
- **Cause**: Multiple consecutive failures triggered circuit breaker
- **Solution**: Check server health, manually reset circuit breaker

### "Invalid JSON in MCP response"
- **Cause**: Server returning malformed JSON or mixing stdout with logs
- **Solution**: Enable debug logging, check server log output

### "No result in MCP response"
- **Cause**: MCP protocol error or tool execution failure
- **Solution**: Test tool calls directly, check tool implementation

### "HTTP fallback unreachable"
- **Cause**: HTTP API not running or incorrect URL
- **Solution**: Verify HTTP API is running, check base URL configuration