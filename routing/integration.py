"""
Integration layer for model routing with existing Zen MCP tools.

This module provides seamless integration of dynamic model routing with the existing
MCP server and tool architecture. It wraps the model provider selection logic to
provide intelligent routing while maintaining full backwards compatibility.
"""

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional

from .hooks import ToolHooks
from .model_level_router import ModelLevelRouter, RoutingResult

logger = logging.getLogger(__name__)

class ModelRoutingIntegration:
    """
    Main integration class for dynamic model routing.
    
    Provides seamless integration with existing Zen MCP server and tool architecture
    by intercepting model provider selection and injecting intelligent routing decisions.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.enabled = self._is_routing_enabled()
        self.router = None
        self.hooks = None
        self.metrics = {
            "routing_decisions": 0,
            "routing_successes": 0,
            "routing_failures": 0,
            "cost_savings": 0.0,
            "free_model_selections": 0
        }

        if self.enabled:
            try:
                self.router = ModelLevelRouter(config_path)
                self.hooks = ToolHooks()
                logger.info("Dynamic model routing enabled")
            except Exception as e:
                logger.error(f"Failed to initialize model routing: {e}")
                self.enabled = False

    def _is_routing_enabled(self) -> bool:
        """Check if routing is enabled via environment variable."""
        return os.getenv("ZEN_SMART_ROUTING", "false").lower() == "true"

    def wrap_get_model_provider(self, original_method: Callable) -> Callable:
        """
        Wrap the get_model_provider method to inject dynamic routing.
        
        Args:
            original_method: The original get_model_provider method from BaseTool
            
        Returns:
            Wrapped method that performs intelligent model selection
        """
        @wraps(original_method)
        def wrapped_get_model_provider(tool_instance, model_name: str, **kwargs):
            if not self.enabled:
                return original_method(tool_instance, model_name, **kwargs)

            try:
                # Extract context from tool instance and request
                context = self._extract_tool_context(tool_instance, kwargs)

                # Get routing recommendation
                routing_result = self._get_routing_recommendation(
                    model_name, tool_instance, context
                )

                if routing_result:
                    # Use routed model instead of originally requested model
                    routed_model_name = routing_result.model.name
                    self._log_routing_decision(model_name, routed_model_name, routing_result)

                    # Call original method with routed model
                    provider = original_method(tool_instance, routed_model_name, **kwargs)
                    self.metrics["routing_successes"] += 1

                    if routing_result.model.cost_per_token == 0:
                        self.metrics["free_model_selections"] += 1

                    return provider
                else:
                    # Fall back to original model
                    return original_method(tool_instance, model_name, **kwargs)

            except Exception as e:
                logger.warning(f"Model routing failed, falling back to original: {e}")
                self.metrics["routing_failures"] += 1
                return original_method(tool_instance, model_name, **kwargs)

        return wrapped_get_model_provider

    def _extract_tool_context(self, tool_instance, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context information from tool instance and request."""
        context = {}

        # Extract tool type
        context["tool_name"] = getattr(tool_instance, "name", tool_instance.__class__.__name__)

        # Extract file information if available
        if hasattr(tool_instance, "_current_request"):
            request = tool_instance._current_request
            if hasattr(request, "files") and request.files:
                context["files"] = request.files
                # Extract file types
                context["file_types"] = [
                    file_path.split(".")[-1] if "." in file_path else ""
                    for file_path in request.files
                ]

        # Extract any error context
        if hasattr(tool_instance, "_current_error"):
            context["error"] = tool_instance._current_error

        return context

    def _get_routing_recommendation(self,
                                  original_model: str,
                                  tool_instance,
                                  context: Dict[str, Any]) -> Optional[RoutingResult]:
        """Get routing recommendation for model selection."""
        if not self.router:
            return None

        # Check if routing is disabled for this specific tool
        tool_name = context.get("tool_name", "").lower()
        tool_class_name = tool_instance.__class__.__name__ if tool_instance else ""

        if self._is_tool_routing_disabled(tool_name, tool_class_name):
            logger.debug(f"Routing disabled for tool: {tool_name} ({tool_class_name})")
            return None

        try:
            # Build prompt for analysis
            prompt = self._build_analysis_prompt(tool_instance, context)

            # Get routing decision
            routing_result = self.router.select_model(
                prompt=prompt,
                context=context,
                prefer_free=True  # Default to preferring free models
            )

            self.metrics["routing_decisions"] += 1

            # Check if we should override the original model choice
            if self._should_override_model(original_model, routing_result):
                return routing_result
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get routing recommendation: {e}")
            return None

    def _build_analysis_prompt(self, tool_instance, context: Dict[str, Any]) -> str:
        """Build a prompt for complexity analysis from tool context."""
        tool_name = context.get("tool_name", "unknown")

        # Get tool-specific prompt building
        if self.hooks:
            prompt = self.hooks.build_analysis_prompt(tool_name, context)
            if prompt:
                return prompt

        # Generic prompt building
        prompt_parts = [f"Tool: {tool_name}"]

        if context.get("files"):
            prompt_parts.append(f"Files: {len(context['files'])} files")
            if context.get("file_types"):
                prompt_parts.append(f"File types: {', '.join(set(context['file_types']))}")

        if context.get("error"):
            prompt_parts.append("Task involves error handling/debugging")

        return "; ".join(prompt_parts)

    def _should_override_model(self,
                              original_model: str,
                              routing_result: RoutingResult) -> bool:
        """Determine if we should override the original model choice."""
        # Always override if we can use a free model
        if routing_result.model.cost_per_token == 0:
            return True

        # Override if original model was "auto" or not specified well
        if original_model.lower() in ["auto", "default", ""]:
            return True

        # Override if routing confidence is very high
        if routing_result.confidence > 0.8:
            return True

        # Override if we have a specialized model for the task
        if routing_result.reasoning and "specialized" in routing_result.reasoning.lower():
            return True

        return False

    def _is_tool_routing_disabled(self, tool_name: str, tool_class_name: str) -> bool:
        """Check if routing is disabled for a specific tool."""
        if not self.router or not hasattr(self.router, 'routing_config'):
            return False

        # Check environment variable exclusions first
        excluded_tools = os.getenv("ZEN_ROUTING_EXCLUDE_TOOLS", "").lower()
        if excluded_tools:
            excluded_list = [tool.strip() for tool in excluded_tools.split(",")]
            if (tool_name.lower() in excluded_list or
                tool_class_name.lower() in excluded_list):
                logger.debug(f"Tool {tool_name} excluded via ZEN_ROUTING_EXCLUDE_TOOLS")
                return True

        tool_rules = self.router.routing_config.get("tool_specific_rules", {})

        # Check by tool name (e.g., "layered_consensus")
        if tool_name in tool_rules:
            return not tool_rules[tool_name].get("enabled", True)

        # Check by tool class name (e.g., "LayeredConsensusTool")
        if tool_class_name in tool_rules:
            return not tool_rules[tool_class_name].get("enabled", True)

        # Check for partial matches (e.g., "consensus" matches "layered_consensus")
        for rule_name, rule_config in tool_rules.items():
            if (rule_name.lower() in tool_name.lower() or
                rule_name.lower() in tool_class_name.lower()):
                return not rule_config.get("enabled", True)

        return False

    def _log_routing_decision(self,
                            original_model: str,
                            routed_model: str,
                            routing_result: RoutingResult):
        """Log routing decision for monitoring."""
        logger.info(
            f"Model routing: {original_model} -> {routed_model} "
            f"(confidence: {routing_result.confidence:.2f}, "
            f"cost: ${routing_result.estimated_cost:.4f})"
        )
        logger.debug(f"Routing reasoning: {routing_result.reasoning}")

    def integrate_with_base_tool(self, base_tool_class):
        """
        Integrate routing with BaseTool class.
        
        This method patches the BaseTool class to add routing capabilities
        to all tools that inherit from it.
        """
        if not self.enabled:
            return

        # Store original method
        original_get_model_provider = base_tool_class.get_model_provider

        # Create wrapper that maintains 'self' binding correctly
        def new_get_model_provider(tool_self, model_name: str, **kwargs):
            return self.wrap_get_model_provider(original_get_model_provider)(
                tool_self, model_name, **kwargs
            )

        # Replace method on class
        base_tool_class.get_model_provider = new_get_model_provider
        logger.info("Integrated dynamic model routing with BaseTool")

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        stats = dict(self.metrics)
        stats["enabled"] = self.enabled

        if self.router:
            stats.update(self.router.get_model_stats())

        # Calculate success rate
        total_decisions = stats.get("routing_decisions", 0)
        if total_decisions > 0:
            stats["success_rate"] = stats.get("routing_successes", 0) / total_decisions
        else:
            stats["success_rate"] = 0.0

        return stats

    def update_model_performance(self, model_name: str, success: bool, error: str = None):
        """Update model performance tracking."""
        if self.router and self.enabled:
            self.router.update_model_performance(model_name, success, error)

    def get_model_recommendation(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get model recommendation for external use."""
        if not self.enabled or not self.router:
            return {"error": "Routing not enabled"}

        try:
            routing_result = self.router.select_model(prompt, context, prefer_free=True)
            return {
                "model": routing_result.model.name,
                "level": routing_result.model.level.value,
                "confidence": routing_result.confidence,
                "reasoning": routing_result.reasoning,
                "estimated_cost": routing_result.estimated_cost,
                "fallback_models": [m.name for m in routing_result.fallback_models]
            }
        except Exception as e:
            return {"error": str(e)}


# Global integration instance
_integration_instance = None

def get_integration_instance() -> ModelRoutingIntegration:
    """Get the global integration instance."""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = ModelRoutingIntegration()
    return _integration_instance

def integrate_with_server():
    """
    Main integration function to be called during server startup.
    
    This function should be called from server.py to enable model routing
    across all tools.
    """
    integration = get_integration_instance()

    if integration.enabled:
        # Import BaseTool and integrate
        try:
            from tools.shared.base_tool import BaseTool
            integration.integrate_with_base_tool(BaseTool)
            logger.info("Dynamic model routing integration complete")
        except ImportError as e:
            logger.error(f"Failed to integrate with BaseTool: {e}")

    else:
        logger.info("Dynamic model routing disabled (ZEN_SMART_ROUTING not set to true)")

def route_model_request(prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function for external model routing requests.
    
    Args:
        prompt: The task description/prompt
        context: Additional context (files, errors, etc.)
        
    Returns:
        Dict with model recommendation or error
    """
    integration = get_integration_instance()
    return integration.get_model_recommendation(prompt, context)
