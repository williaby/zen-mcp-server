# PromptCraft Migration Guide: HTTP to MCP

Step-by-step guide for migrating from HTTP API to native MCP stdio integration.

## Migration Overview

This guide covers the **phased migration approach** recommended by PromptCraft's executive team:

- **Phase 1**: Add MCP alongside HTTP (Weeks 1-2)  
- **Phase 2**: Validate and test MCP integration (Weeks 3-4)
- **Phase 3**: Gradual traffic migration (Weeks 5-6)
- **Phase 4**: Optimization and monitoring (Week 7+)

## Phase 1: Foundation Setup (Weeks 1-2)

### Step 1: Install MCP Client Library

The MCP client library is included with zen-mcp-server. No additional installation required.

```python
# Verify installation
from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
print("✅ MCP client library available")
```

### Step 2: Environment Configuration

Add MCP-specific environment variables:

```bash
# .env file additions
USE_MCP_STDIO=false                    # Feature flag (start disabled)
MCP_TRAFFIC_PERCENTAGE=0               # Traffic splitting (start at 0%)
ZEN_MCP_SERVER_PATH=./server.py        # Path to zen-mcp-server
MCP_TIMEOUT=30                         # MCP connection timeout
HTTP_FALLBACK_URL=http://localhost:8000 # Existing HTTP API URL
```

### Step 3: Create Migration Wrapper

Create a wrapper class that supports both HTTP and MCP:

```python
# promptcraft/integration/zen_client.py
import os
import asyncio
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

# Existing HTTP client imports
import httpx

# New MCP client imports  
from tools.custom.promptcraft_mcp_client import ZenMCPStdioClient
from tools.custom.promptcraft_mcp_client.models import (
    RouteAnalysisRequest,
    SmartExecutionRequest,
    ModelListRequest,
)


@dataclass
class ZenClientConfig:
    """Configuration for Zen integration client."""
    use_mcp: bool = False
    mcp_traffic_percentage: int = 0
    server_path: str = "./server.py"
    http_base_url: str = "http://localhost:8000"
    mcp_timeout: float = 30.0


class ZenIntegrationClient:
    """
    Wrapper client supporting both HTTP and MCP protocols.
    Enables gradual migration from HTTP to MCP.
    """
    
    def __init__(self, config: Optional[ZenClientConfig] = None):
        self.config = config or self._load_config_from_env()
        self.mcp_client: Optional[ZenMCPStdioClient] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        
    def _load_config_from_env(self) -> ZenClientConfig:
        """Load configuration from environment variables."""
        return ZenClientConfig(
            use_mcp=os.getenv("USE_MCP_STDIO", "false").lower() == "true",
            mcp_traffic_percentage=int(os.getenv("MCP_TRAFFIC_PERCENTAGE", "0")),
            server_path=os.getenv("ZEN_MCP_SERVER_PATH", "./server.py"),
            http_base_url=os.getenv("HTTP_FALLBACK_URL", "http://localhost:8000"),
            mcp_timeout=float(os.getenv("MCP_TIMEOUT", "30.0")),
        )
    
    async def __aenter__(self):
        """Initialize clients based on configuration."""
        if self.config.use_mcp or self.config.mcp_traffic_percentage > 0:
            # Initialize MCP client if needed
            self.mcp_client = ZenMCPStdioClient(
                server_path=self.config.server_path,
                connection_timeout=self.config.mcp_timeout
            )
            await self.mcp_client.connect()
        
        # Always initialize HTTP client for fallback
        self.http_client = httpx.AsyncClient(
            base_url=self.config.http_base_url,
            timeout=10.0
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup clients."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
        if self.http_client:
            await self.http_client.aclose()
    
    def _should_use_mcp(self) -> bool:
        """Determine if this request should use MCP."""
        if not self.config.use_mcp:
            return False
            
        if self.config.mcp_traffic_percentage == 0:
            return False
            
        if self.config.mcp_traffic_percentage == 100:
            return True
            
        # Traffic splitting based on percentage
        import random
        return random.randint(1, 100) <= self.config.mcp_traffic_percentage
    
    async def analyze_route(
        self, 
        prompt: str, 
        user_tier: str, 
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze route with automatic HTTP/MCP selection."""
        
        if self._should_use_mcp() and self.mcp_client:
            # Try MCP first
            try:
                request = RouteAnalysisRequest(
                    prompt=prompt,
                    user_tier=user_tier,
                    task_type=task_type
                )
                result = await self.mcp_client.analyze_route(request)
                
                # Convert to consistent format
                return {
                    "success": result.success,
                    "analysis": result.analysis,
                    "recommendations": result.recommendations,
                    "processing_time": result.processing_time,
                    "error": result.error,
                    "_used_protocol": "mcp"
                }
                
            except Exception as e:
                print(f"MCP failed, falling back to HTTP: {e}")
                # Fall through to HTTP
        
        # Use HTTP (either as primary or fallback)
        response = await self.http_client.post(
            "/api/promptcraft/route/analyze",
            json={
                "prompt": prompt,
                "user_tier": user_tier,
                "task_type": task_type
            }
        )
        result = response.json()
        result["_used_protocol"] = "http"
        return result
    
    async def smart_execute(
        self,
        prompt: str,
        user_tier: str,
        channel: str = "stable",
        cost_optimization: bool = True,
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """Execute prompt with automatic HTTP/MCP selection."""
        
        if self._should_use_mcp() and self.mcp_client:
            try:
                request = SmartExecutionRequest(
                    prompt=prompt,
                    user_tier=user_tier,
                    channel=channel,
                    cost_optimization=cost_optimization,
                    include_reasoning=include_reasoning
                )
                result = await self.mcp_client.smart_execute(request)
                
                return {
                    "success": result.success,
                    "result": result.response,  # Note: different key name
                    "execution_metadata": result.execution_metadata,
                    "processing_time": result.processing_time,
                    "error": result.error,
                    "_used_protocol": "mcp"
                }
                
            except Exception as e:
                print(f"MCP failed, falling back to HTTP: {e}")
        
        # HTTP fallback
        response = await self.http_client.post(
            "/api/promptcraft/execute/smart",
            json={
                "prompt": prompt,
                "user_tier": user_tier,
                "channel": channel,
                "cost_optimization": cost_optimization,
                "include_reasoning": include_reasoning
            }
        )
        result = response.json()
        result["_used_protocol"] = "http"
        return result
    
    async def list_models(
        self,
        user_tier: Optional[str] = None,
        channel: str = "stable",
        include_metadata: bool = True,
        format: str = "ui"
    ) -> Dict[str, Any]:
        """List models with automatic HTTP/MCP selection."""
        
        if self._should_use_mcp() and self.mcp_client:
            try:
                request = ModelListRequest(
                    user_tier=user_tier,
                    channel=channel,
                    include_metadata=include_metadata,
                    format=format
                )
                result = await self.mcp_client.list_models(request)
                
                return {
                    "success": result.success,
                    "models": result.models,
                    "metadata": result.metadata,
                    "processing_time": result.processing_time,
                    "error": result.error,
                    "_used_protocol": "mcp"
                }
                
            except Exception as e:
                print(f"MCP failed, falling back to HTTP: {e}")
        
        # HTTP fallback
        response = await self.http_client.get(
            "/api/promptcraft/models/available",
            params={
                "user_tier": user_tier,
                "channel": channel,
                "include_metadata": include_metadata,
                "format": format
            }
        )
        result = response.json()
        result["_used_protocol"] = "http"
        return result
```

### Step 4: Update Application Code

Replace existing HTTP client usage:

```python
# BEFORE: Direct HTTP usage
async def old_approach():
    async with httpx.AsyncClient() as client:
        response = await client.post("/api/promptcraft/route/analyze", json={
            "prompt": "Test prompt",
            "user_tier": "full"
        })
        return response.json()

# AFTER: Migration wrapper
async def new_approach():
    async with ZenIntegrationClient() as client:
        return await client.analyze_route("Test prompt", "full")
```

### Step 5: Testing Setup

Create test scenarios for both protocols:

```python
# tests/test_migration.py
import pytest
from promptcraft.integration.zen_client import ZenIntegrationClient, ZenClientConfig


@pytest.mark.asyncio
async def test_http_only():
    """Test HTTP-only mode."""
    config = ZenClientConfig(use_mcp=False)
    async with ZenIntegrationClient(config) as client:
        result = await client.analyze_route("Test", "full")
        assert result["_used_protocol"] == "http"


@pytest.mark.asyncio 
async def test_mcp_with_fallback():
    """Test MCP with HTTP fallback."""
    config = ZenClientConfig(use_mcp=True, mcp_traffic_percentage=100)
    async with ZenIntegrationClient(config) as client:
        result = await client.analyze_route("Test", "full")
        # Should use MCP or HTTP (depending on server availability)
        assert result["_used_protocol"] in ["mcp", "http"]


@pytest.mark.asyncio
async def test_traffic_splitting():
    """Test traffic splitting functionality."""
    config = ZenClientConfig(use_mcp=True, mcp_traffic_percentage=50)
    
    protocols_used = []
    async with ZenIntegrationClient(config) as client:
        # Run multiple requests to test splitting
        for _ in range(20):
            result = await client.analyze_route("Test", "full")
            protocols_used.append(result["_used_protocol"])
    
    # Should have mix of both protocols (allowing for randomness)
    unique_protocols = set(protocols_used)
    assert len(unique_protocols) >= 1  # At least one protocol used
```

## Phase 2: Validation & Testing (Weeks 3-4)

### Step 1: Performance Benchmarking

Create benchmarking script:

```python
# scripts/benchmark_migration.py
import asyncio
import time
import statistics
from promptcraft.integration.zen_client import ZenIntegrationClient, ZenClientConfig


async def benchmark_protocol(config: ZenClientConfig, num_requests: int = 50):
    """Benchmark a specific configuration."""
    latencies = []
    success_count = 0
    
    async with ZenIntegrationClient(config) as client:
        for i in range(num_requests):
            start_time = time.time()
            try:
                result = await client.analyze_route(
                    f"Benchmark request {i}",
                    "full"
                )
                latency = time.time() - start_time
                latencies.append(latency * 1000)  # Convert to ms
                
                if result.get("success", True):
                    success_count += 1
                    
            except Exception as e:
                print(f"Request {i} failed: {e}")
                latencies.append(float('inf'))
    
    # Filter out failed requests for latency calculation
    valid_latencies = [lat for lat in latencies if lat != float('inf')]
    
    return {
        "protocol": "mcp" if config.use_mcp else "http", 
        "total_requests": num_requests,
        "successful_requests": success_count,
        "success_rate": success_count / num_requests * 100,
        "avg_latency_ms": statistics.mean(valid_latencies) if valid_latencies else 0,
        "p95_latency_ms": statistics.quantiles(valid_latencies, n=20)[18] if valid_latencies else 0,
        "min_latency_ms": min(valid_latencies) if valid_latencies else 0,
        "max_latency_ms": max(valid_latencies) if valid_latencies else 0,
    }


async def run_benchmarks():
    """Run comparative benchmarks."""
    print("🚀 Starting migration benchmarks...")
    
    # HTTP baseline
    http_config = ZenClientConfig(use_mcp=False)
    http_results = await benchmark_protocol(http_config)
    
    # MCP comparison
    mcp_config = ZenClientConfig(use_mcp=True, mcp_traffic_percentage=100)
    mcp_results = await benchmark_protocol(mcp_config)
    
    # Print comparison
    print("\n📊 Benchmark Results:")
    print(f"{'Metric':<20} {'HTTP':<15} {'MCP':<15} {'Improvement':<15}")
    print("-" * 65)
    
    metrics = ['avg_latency_ms', 'p95_latency_ms', 'success_rate']
    for metric in metrics:
        http_val = http_results[metric]
        mcp_val = mcp_results[metric]
        
        if metric == 'success_rate':
            improvement = f"{mcp_val - http_val:+.1f}%"
        else:
            improvement = f"{(http_val - mcp_val) / http_val * 100:+.1f}%"
            
        print(f"{metric:<20} {http_val:<15.1f} {mcp_val:<15.1f} {improvement:<15}")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
```

### Step 2: Load Testing

```python
# scripts/load_test.py
import asyncio
import aiohttp
from promptcraft.integration.zen_client import ZenIntegrationClient, ZenClientConfig


async def load_test(concurrent_requests: int = 10, duration_seconds: int = 60):
    """Load test both protocols under concurrent load."""
    
    async def worker(client, worker_id: int, results: list):
        """Worker function for concurrent requests."""
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                result = await client.analyze_route(f"Load test {worker_id}", "full")
                request_count += 1
                results.append({
                    "success": result.get("success", True),
                    "protocol": result.get("_used_protocol", "unknown"),
                    "latency": result.get("processing_time", 0)
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "protocol": "error"
                })
            
            await asyncio.sleep(0.1)  # Brief pause between requests
    
    print(f"🔥 Load testing with {concurrent_requests} concurrent workers for {duration_seconds}s")
    
    # Test with 50/50 traffic split
    config = ZenClientConfig(use_mcp=True, mcp_traffic_percentage=50)
    results = []
    
    async with ZenIntegrationClient(config) as client:
        # Start concurrent workers
        tasks = [
            worker(client, i, results) 
            for i in range(concurrent_requests)
        ]
        
        await asyncio.gather(*tasks)
    
    # Analyze results
    total_requests = len(results)
    successful_requests = sum(1 for r in results if r["success"])
    mcp_requests = sum(1 for r in results if r["protocol"] == "mcp")
    http_requests = sum(1 for r in results if r["protocol"] == "http")
    
    print(f"\n📈 Load Test Results:")
    print(f"Total requests: {total_requests}")
    print(f"Success rate: {successful_requests/total_requests*100:.1f}%")
    print(f"MCP requests: {mcp_requests} ({mcp_requests/total_requests*100:.1f}%)")
    print(f"HTTP requests: {http_requests} ({http_requests/total_requests*100:.1f}%)")


if __name__ == "__main__":
    asyncio.run(load_test())
```

## Phase 3: Gradual Migration (Weeks 5-6)

### Step 1: Enable MCP (Week 5, Day 1)

Start with minimal MCP traffic:

```bash
# Environment configuration
USE_MCP_STDIO=true
MCP_TRAFFIC_PERCENTAGE=10  # Start with 10%
```

### Step 2: Monitor and Increase (Week 5)

Gradually increase MCP traffic based on performance:

```bash
# Day 2: 10% → 20%
MCP_TRAFFIC_PERCENTAGE=20

# Day 3: 20% → 30% 
MCP_TRAFFIC_PERCENTAGE=30

# Day 5: 30% → 50%
MCP_TRAFFIC_PERCENTAGE=50
```

### Step 3: Monitoring Dashboard

Create monitoring for the migration:

```python
# monitoring/migration_metrics.py
import asyncio
import json
from datetime import datetime
from collections import defaultdict, deque


class MigrationMonitor:
    """Monitor migration progress and performance."""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.start_time = datetime.now()
    
    def record_request(self, protocol: str, success: bool, latency_ms: float):
        """Record a request for monitoring."""
        timestamp = datetime.now()
        self.metrics[f"{protocol}_requests"].append({
            "timestamp": timestamp.isoformat(),
            "success": success,
            "latency_ms": latency_ms
        })
    
    def get_summary(self, last_n_minutes: int = 60) -> dict:
        """Get summary of metrics for last N minutes."""
        cutoff = datetime.now().timestamp() - (last_n_minutes * 60)
        
        summary = {
            "period_minutes": last_n_minutes,
            "protocols": {}
        }
        
        for protocol in ["mcp", "http"]:
            requests = list(self.metrics[f"{protocol}_requests"])
            
            # Filter to time window
            recent_requests = [
                r for r in requests 
                if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff
            ]
            
            if recent_requests:
                latencies = [r["latency_ms"] for r in recent_requests]
                successes = sum(1 for r in recent_requests if r["success"])
                
                summary["protocols"][protocol] = {
                    "total_requests": len(recent_requests),
                    "successful_requests": successes,
                    "success_rate": successes / len(recent_requests) * 100,
                    "avg_latency_ms": sum(latencies) / len(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies),
                }
            else:
                summary["protocols"][protocol] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "success_rate": 0,
                    "avg_latency_ms": 0,
                    "min_latency_ms": 0,
                    "max_latency_ms": 0,
                }
        
        return summary
    
    def print_summary(self):
        """Print current migration status."""
        summary = self.get_summary(60)
        
        print(f"\n🔄 Migration Status (Last 60 minutes)")
        print(f"{'Protocol':<10} {'Requests':<10} {'Success':<10} {'Avg Latency':<12}")
        print("-" * 50)
        
        for protocol, metrics in summary["protocols"].items():
            print(f"{protocol.upper():<10} {metrics['total_requests']:<10} "
                  f"{metrics['success_rate']:<10.1f}% {metrics['avg_latency_ms']:<12.1f}ms")


# Integration with existing client
class MonitoredZenClient(ZenIntegrationClient):
    """Zen client with monitoring capabilities."""
    
    def __init__(self, config=None, monitor=None):
        super().__init__(config)
        self.monitor = monitor or MigrationMonitor()
    
    async def analyze_route(self, prompt: str, user_tier: str, task_type=None):
        start_time = time.time()
        
        try:
            result = await super().analyze_route(prompt, user_tier, task_type)
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            self.monitor.record_request(
                protocol=result.get("_used_protocol", "unknown"),
                success=result.get("success", True),
                latency_ms=latency_ms
            )
            
            return result
            
        except Exception as e:
            # Record failure
            latency_ms = (time.time() - start_time) * 1000
            self.monitor.record_request(
                protocol="error",
                success=False, 
                latency_ms=latency_ms
            )
            raise
```

### Step 4: Automated Traffic Control

```python
# scripts/traffic_controller.py
import asyncio
import os
from monitoring.migration_metrics import MigrationMonitor, MonitoredZenClient


async def automatic_traffic_control():
    """Automatically adjust MCP traffic based on performance."""
    
    current_percentage = int(os.getenv("MCP_TRAFFIC_PERCENTAGE", "10"))
    monitor = MigrationMonitor()
    
    while True:
        # Monitor for 10 minutes
        await asyncio.sleep(600)
        
        summary = monitor.get_summary(10)  # Last 10 minutes
        mcp_metrics = summary["protocols"]["mcp"]
        http_metrics = summary["protocols"]["http"]
        
        print(f"Current MCP traffic: {current_percentage}%")
        monitor.print_summary()
        
        # Decision logic
        if (mcp_metrics["success_rate"] >= 98.0 and 
            mcp_metrics["avg_latency_ms"] <= http_metrics["avg_latency_ms"] * 1.2):
            
            # MCP is performing well, increase traffic
            if current_percentage < 100:
                new_percentage = min(current_percentage + 10, 100)
                print(f"✅ Increasing MCP traffic: {current_percentage}% → {new_percentage}%")
                current_percentage = new_percentage
                
                # Update environment variable (application needs restart)
                # In production, this would update a configuration service
                os.environ["MCP_TRAFFIC_PERCENTAGE"] = str(new_percentage)
                
        elif mcp_metrics["success_rate"] < 95.0:
            # MCP performance degraded, decrease traffic
            if current_percentage > 0:
                new_percentage = max(current_percentage - 10, 0)
                print(f"⚠️ Decreasing MCP traffic: {current_percentage}% → {new_percentage}%")
                current_percentage = new_percentage
                os.environ["MCP_TRAFFIC_PERCENTAGE"] = str(new_percentage)
        
        else:
            print(f"📊 Maintaining current MCP traffic: {current_percentage}%")


if __name__ == "__main__":
    asyncio.run(automatic_traffic_control())
```

## Phase 4: Optimization (Week 7+)

### Step 1: Full MCP Migration

Once MCP performance is validated:

```bash
# Final configuration
USE_MCP_STDIO=true
MCP_TRAFFIC_PERCENTAGE=100  # Full MCP
```

### Step 2: Performance Optimizations

```python
# Optimize for production
from tools.custom.promptcraft_mcp_client.models import FallbackConfig

# Production configuration
production_fallback = FallbackConfig(
    enabled=True,  # Keep HTTP fallback available
    circuit_breaker_threshold=3,  # Quick failure detection
    circuit_breaker_reset_time=30.0,  # Fast recovery attempts
    fallback_timeout=5.0,  # Fast fallback timeout
)

client = ZenMCPStdioClient(
    server_path="/prod/zen-mcp-server/server.py",
    env_vars={
        "LOG_LEVEL": "WARNING",  # Reduce logging overhead
        "MCP_TIMEOUT": "20.0",   # Stricter timeout
    },
    fallback_config=production_fallback
)
```

### Step 3: Cleanup Legacy Code

Remove HTTP-only code paths once MCP is stable:

```python
# Remove old HTTP client code
# Keep only the MCP client with HTTP fallback

async def production_analyze_route(prompt: str, user_tier: str) -> dict:
    """Production route analysis using MCP with HTTP fallback."""
    async with ZenMCPStdioClient("/prod/server.py") as client:
        request = RouteAnalysisRequest(prompt=prompt, user_tier=user_tier)
        result = await client.analyze_route(request)
        
        return {
            "success": result.success,
            "analysis": result.analysis,
            "recommendations": result.recommendations,
            "processing_time": result.processing_time,
        }
```

## Rollback Plan

If issues occur, rollback is simple:

```bash
# Emergency rollback to HTTP-only
USE_MCP_STDIO=false
MCP_TRAFFIC_PERCENTAGE=0

# Restart application
# MCP client will not be initialized, all traffic goes to HTTP
```

## Success Metrics

Track these metrics throughout migration:

1. **Performance**: 20-30ms latency improvement target
2. **Reliability**: 99.9% success rate maintained
3. **Fallback**: HTTP fallback usage < 5% in normal conditions
4. **Errors**: Error rate < 0.1%

## Validation Checklist

Before completing each phase:

### Phase 1 Checklist
- [ ] MCP client library accessible
- [ ] Environment variables configured
- [ ] Migration wrapper implemented
- [ ] Unit tests passing
- [ ] HTTP fallback working

### Phase 2 Checklist  
- [ ] Performance benchmarks show improvement
- [ ] Load testing passes
- [ ] Error handling robust
- [ ] Monitoring in place
- [ ] Rollback plan tested

### Phase 3 Checklist
- [ ] Traffic splitting working
- [ ] Gradual increase successful
- [ ] No performance degradation
- [ ] Circuit breaker functioning
- [ ] Metrics collection accurate

### Phase 4 Checklist
- [ ] Full MCP traffic stable
- [ ] HTTP fallback rarely used
- [ ] Legacy code removed
- [ ] Documentation updated
- [ ] Team knowledge transfer complete

## Support

For migration assistance:
1. Review [mcp-integration-guide.md](./mcp-integration-guide.md)
2. Check [troubleshooting.md](./troubleshooting.md)  
3. Run integration tests: `pytest tests/test_promptcraft_mcp_integration.py -v`
4. Contact zen-mcp-server development team