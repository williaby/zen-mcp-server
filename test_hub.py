#!/usr/bin/env python3
"""
Simple test script for Zen MCP Hub functionality

Tests basic hub initialization, tool filtering, and configuration
without requiring full MCP protocol setup.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from hub.config.hub_settings import HubSettings
from hub.config.tool_mappings import get_tools_for_categories, get_server_for_tool, CORE_TOOLS
from hub.mcp_client_manager import MCPClientManager
from hub.tool_filter import get_tool_categories_for_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_hub_settings():
    """Test hub settings loading"""
    logger.info("Testing hub settings...")
    
    settings = HubSettings.from_env()
    logger.info(f"Hub enabled: {settings.hub_enabled}")
    logger.info(f"Dynamic filtering: {settings.enable_dynamic_filtering}")
    logger.info(f"Max tools per context: {settings.max_tools_per_context}")
    
    return True

async def test_tool_mappings():
    """Test tool category mappings"""
    logger.info("Testing tool mappings...")
    
    # Test category to tools conversion
    test_categories = {"development", "git"}
    tools = get_tools_for_categories(test_categories)
    logger.info(f"Tools for {test_categories}: {len(tools)} tools")
    logger.info(f"Sample tools: {list(tools)[:5]}")
    
    # Test server detection
    test_tools = ["mcp__zen__debug", "mcp__git__git_status", "Read", "mcp__time__get_current_time"]
    for tool in test_tools:
        server = get_server_for_tool(tool)
        logger.info(f"Tool {tool} -> Server {server}")
    
    # Test core tools
    logger.info(f"Core tools count: {len(CORE_TOOLS)}")
    logger.info(f"Core tools: {list(CORE_TOOLS)[:5]}")
    
    return True

async def test_query_categorization():
    """Test query-based category detection"""
    logger.info("Testing query categorization...")
    
    test_queries = [
        "debug this error in my Python code",
        "commit my changes to git",
        "analyze the security of this function", 
        "help me plan this project",
        "what time is it in Tokyo?"
    ]
    
    for query in test_queries:
        categories = get_tool_categories_for_query(query)
        logger.info(f"Query: '{query}' -> Categories: {categories}")
    
    return True

async def test_mcp_client_manager():
    """Test MCP client manager initialization (mock mode)"""
    logger.info("Testing MCP client manager...")
    
    try:
        # Create manager
        manager = MCPClientManager()
        
        # Test initialization (will fail to connect but should handle gracefully)
        logger.info("Attempting to initialize MCP connections (expected to fail in test mode)...")
        success = await manager.initialize()
        logger.info(f"MCP initialization result: {success}")
        
        # Test tool discovery even if connections failed
        all_tools = await manager.get_all_tools()
        logger.info(f"Available tools from MCP manager: {len(all_tools)}")
        
        # Cleanup
        await manager.shutdown()
        
        return True
        
    except Exception as e:
        logger.error(f"MCP client manager test error: {e}")
        return False

async def test_hub_integration():
    """Test overall hub integration"""
    logger.info("Testing hub integration...")
    
    try:
        # Import hub server components
        from hub_server import ZenHubServer
        
        # Create hub server instance
        hub = ZenHubServer()
        logger.info(f"Hub server created - enabled: {hub.hub_enabled}")
        
        # Test initialization (will partially fail without real MCP servers)
        logger.info("Testing hub initialization...")
        success = await hub.initialize_hub()
        logger.info(f"Hub initialization: {success}")
        
        # Test status
        status = await hub.get_hub_status()
        logger.info(f"Hub status: {status}")
        
        # Cleanup
        await hub.shutdown_hub()
        
        return True
        
    except Exception as e:
        logger.error(f"Hub integration test error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    logger.info("Starting Zen MCP Hub tests...")
    
    tests = [
        ("Hub Settings", test_hub_settings),
        ("Tool Mappings", test_tool_mappings),
        ("Query Categorization", test_query_categorization),
        ("MCP Client Manager", test_mcp_client_manager),
        ("Hub Integration", test_hub_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            result = await test_func()
            results[test_name] = result
            status = "PASSED" if result else "FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"{test_name}: FAILED with error: {e}")
    
    # Summary
    logger.info(f"\n--- Test Summary ---")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Hub implementation looks good.")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test runner error: {e}")
        sys.exit(1)