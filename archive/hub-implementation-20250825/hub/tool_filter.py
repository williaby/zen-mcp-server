"""
Zen Tool Filter - Intelligent tool filtering using dynamic loading logic

Integrates the dynamic function loading system to provide context-aware
tool filtering for the Zen MCP Hub.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Set

from .config.hub_settings import HubSettings
from .config.tool_mappings import CORE_TOOLS, TOOL_CATEGORY_MAPPINGS, get_tools_for_categories
from .dynamic_function_loader import DynamicFunctionLoader
from .mcp_client_manager import MCPClientManager, MCPTool
from .task_detection import DetectionResult, TaskDetectionSystem

logger = logging.getLogger(__name__)

class ZenToolFilter:
    """
    Intelligent tool filtering system that uses task detection to determine
    which tools should be available for a given query context.
    """

    def __init__(self,
                 mcp_manager: MCPClientManager,
                 settings: Optional[HubSettings] = None):
        self.mcp_manager = mcp_manager
        self.settings = settings or HubSettings.from_env()

        # Initialize dynamic loading components
        self.task_detector = TaskDetectionSystem()
        self.function_loader = DynamicFunctionLoader()

        # Cache for performance
        self._detection_cache: Dict[str, DetectionResult] = {}
        self._cache_timestamps: Dict[str, float] = {}

    async def filter_tools_for_query(self,
                                   query: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, MCPTool]:
        """
        Filter available tools based on query analysis.
        
        Args:
            query: User query to analyze
            context: Additional context (file types, git state, etc.)
            
        Returns:
            Dictionary of tool_name -> MCPTool for filtered tools
        """
        if not self.settings.enable_dynamic_filtering:
            # If filtering disabled, return all tools
            return await self.mcp_manager.get_all_tools()

        try:
            # Get task detection result
            detection_result = await self._get_detection_result(query, context)

            # Convert categories to tool names
            tool_names = self._categories_to_tools(detection_result.categories)

            # Get actual tool objects from MCP manager
            filtered_tools = await self._get_tools_by_names(tool_names)

            # Log filtering if enabled
            if self.settings.log_tool_filtering:
                self._log_filtering_result(query, detection_result, filtered_tools)

            return filtered_tools

        except Exception as e:
            logger.error(f"Error in tool filtering: {e}")

            if self.settings.fallback_to_core_tools:
                logger.info("Falling back to core tools due to filtering error")
                return await self._get_core_tools()
            else:
                # Return all tools as fallback
                return await self.mcp_manager.get_all_tools()

    async def _get_detection_result(self,
                                  query: str,
                                  context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        """Get task detection result with caching"""

        # Create cache key
        cache_key = f"{hash(query)}_{hash(str(context))}"

        # Check cache if enabled
        if self.settings.cache_detection_results:
            if cache_key in self._detection_cache:
                cache_time = self._cache_timestamps.get(cache_key, 0)
                if time.time() - cache_time < self.settings.cache_ttl:
                    return self._detection_cache[cache_key]

        # Perform detection with timeout
        try:
            detection_result = await asyncio.wait_for(
                self.task_detector.detect_categories(query, context),
                timeout=self.settings.tool_detection_timeout
            )

            # Cache result if enabled
            if self.settings.cache_detection_results:
                self._detection_cache[cache_key] = detection_result
                self._cache_timestamps[cache_key] = time.time()

            return detection_result

        except asyncio.TimeoutError:
            logger.warning(f"Task detection timed out for query: {query[:50]}...")
            # Return fallback detection result
            return DetectionResult(
                categories={"core": True},
                confidence_scores={"core": 1.0},
                detection_time_ms=self.settings.tool_detection_timeout * 1000,
                signals_used={},
                fallback_applied="timeout"
            )

    def _categories_to_tools(self, categories: Dict[str, bool]) -> Set[str]:
        """Convert detection categories to specific tool names"""
        active_categories = {cat for cat, active in categories.items() if active}

        # Get tools for active categories
        tool_names = set(get_tools_for_categories(active_categories))

        # Ensure we don't exceed max tools limit
        if len(tool_names) > self.settings.max_tools_per_context:
            # Keep core tools + highest priority others
            core_tools = set(CORE_TOOLS)
            other_tools = tool_names - core_tools

            # Sort other tools by priority (implementation would need priority scoring)
            limited_other_tools = list(other_tools)[:self.settings.max_tools_per_context - len(core_tools)]
            tool_names = core_tools | set(limited_other_tools)

        return tool_names

    async def _get_tools_by_names(self, tool_names: Set[str]) -> Dict[str, MCPTool]:
        """Get actual MCPTool objects for the given tool names"""
        # Get all available tools from MCP manager
        all_tools = await self.mcp_manager.get_all_tools()

        # Filter to requested tools
        filtered_tools = {}

        for tool_name in tool_names:
            if tool_name in all_tools:
                filtered_tools[tool_name] = all_tools[tool_name]
            elif tool_name in CORE_TOOLS:
                # Handle built-in Claude Code tools that aren't in MCP servers
                # These would be handled differently - for now just note they're needed
                logger.debug(f"Core tool {tool_name} requested but not available via MCP")

        return filtered_tools

    async def _get_core_tools(self) -> Dict[str, MCPTool]:
        """Get just the core tools as fallback"""
        return await self._get_tools_by_names(CORE_TOOLS)

    def _log_filtering_result(self,
                            query: str,
                            detection_result: DetectionResult,
                            filtered_tools: Dict[str, MCPTool]):
        """Log the filtering result for debugging"""
        active_categories = {cat for cat, active in detection_result.categories.items() if active}
        tool_names = list(filtered_tools.keys())

        logger.info(f"Tool filtering for query: '{query[:50]}...'")
        logger.info(f"  Detected categories: {active_categories}")
        logger.info(f"  Detection time: {detection_result.detection_time_ms:.1f}ms")
        logger.info(f"  Filtered to {len(tool_names)} tools: {tool_names[:5]}...")
        if detection_result.fallback_applied:
            logger.info(f"  Fallback applied: {detection_result.fallback_applied}")

    async def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get statistics about tool filtering usage"""
        return {
            "cache_size": len(self._detection_cache),
            "settings": {
                "filtering_enabled": self.settings.enable_dynamic_filtering,
                "max_tools_per_context": self.settings.max_tools_per_context,
                "detection_timeout": self.settings.tool_detection_timeout
            },
            "available_categories": list(TOOL_CATEGORY_MAPPINGS.keys())
        }

    def clear_cache(self):
        """Clear the detection result cache"""
        self._detection_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Tool filter cache cleared")

# Utility functions for integration with existing Zen server

async def create_tool_filter(mcp_manager: MCPClientManager,
                           settings: Optional[HubSettings] = None) -> ZenToolFilter:
    """Factory function to create and initialize a tool filter"""
    tool_filter = ZenToolFilter(mcp_manager, settings)
    logger.info("Zen tool filter initialized")
    return tool_filter

def get_tool_categories_for_query(query: str) -> Set[str]:
    """
    Quick synchronous function to get likely categories for a query.
    Useful for preliminary filtering before full async detection.
    """
    query_lower = query.lower()

    categories = set()

    # Simple keyword-based category detection
    if any(word in query_lower for word in ["debug", "error", "bug", "fix"]):
        categories.add("development")
    if any(word in query_lower for word in ["git", "commit", "branch", "merge"]):
        categories.add("workflow")
    if any(word in query_lower for word in ["security", "vulnerability", "audit"]):
        categories.add("specialized")
    if any(word in query_lower for word in ["plan", "analyze", "consensus"]):
        categories.add("workflow")
    if any(word in query_lower for word in ["test", "coverage", "pytest"]):
        categories.add("development")

    # Always include core for basic functionality
    if not categories:
        categories.add("core")

    return categories
