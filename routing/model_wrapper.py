"""
Model Wrapper for Dynamic Routing

This module provides a wrapper around model calls to enable automatic routing
based on prompt analysis while maintaining compatibility with existing code.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from functools import wraps

from .model_level_router import ModelLevelRouter, RoutingResult
from .complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ModelCallContext:
    """Context information for a model call."""
    tool_name: str
    prompt: str
    files: List[str] = None
    model_requested: str = None
    temperature: float = None
    max_tokens: int = None
    additional_context: Dict[str, Any] = None

@dataclass
class RoutingDecision:
    """Information about a routing decision."""
    original_model: str
    selected_model: str
    routing_used: bool
    confidence: float = 0.0
    reasoning: str = ""
    estimated_cost: float = 0.0
    fallback_reason: Optional[str] = None

class ModelWrapper:
    """
    Wrapper for model calls that provides automatic routing capabilities.
    
    This class intercepts model calls and applies intelligent routing decisions
    while maintaining full compatibility with existing model provider interfaces.
    """
    
    def __init__(self, router: Optional[ModelLevelRouter] = None):
        self.router = router or ModelLevelRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.call_history: List[Dict[str, Any]] = []
        self.performance_tracking: Dict[str, Dict[str, Any]] = {}
        
    def wrap_model_call(self, 
                       original_call: Callable,
                       context: ModelCallContext) -> Callable:
        """
        Wrap a model call to add routing capabilities.
        
        Args:
            original_call: The original model call function
            context: Context information for the call
            
        Returns:
            Wrapped function with routing capabilities
        """
        @wraps(original_call)
        def wrapped_call(*args, **kwargs):
            start_time = time.time()
            routing_decision = None
            
            try:
                # Get routing decision
                routing_decision = self._make_routing_decision(context)
                
                # Apply routing if recommended
                if routing_decision.routing_used:
                    # Modify the model parameter
                    if 'model' in kwargs:
                        kwargs['model'] = routing_decision.selected_model
                    elif len(args) > 0 and hasattr(args[0], 'model'):
                        # Handle case where model is in first argument object
                        args[0].model = routing_decision.selected_model
                
                # Make the actual call
                result = original_call(*args, **kwargs)
                
                # Track success
                self._track_call_result(context, routing_decision, True, time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Track failure
                self._track_call_result(context, routing_decision, False, time.time() - start_time, str(e))
                
                # If routing was used and it failed, try with original model
                if (routing_decision and routing_decision.routing_used and 
                    routing_decision.original_model != routing_decision.selected_model):
                    
                    logger.warning(f"Routed model failed, falling back to {routing_decision.original_model}")
                    
                    try:
                        # Restore original model and retry
                        if 'model' in kwargs:
                            kwargs['model'] = routing_decision.original_model
                        elif len(args) > 0 and hasattr(args[0], 'model'):
                            args[0].model = routing_decision.original_model
                            
                        result = original_call(*args, **kwargs)
                        
                        # Track fallback success
                        fallback_decision = RoutingDecision(
                            original_model=routing_decision.original_model,
                            selected_model=routing_decision.original_model,
                            routing_used=False,
                            fallback_reason="Routed model failed"
                        )
                        self._track_call_result(context, fallback_decision, True, time.time() - start_time)
                        
                        return result
                        
                    except Exception as fallback_error:
                        logger.error(f"Both routed and original model failed: {fallback_error}")
                        raise fallback_error
                else:
                    raise e
                
        return wrapped_call
    
    def _make_routing_decision(self, context: ModelCallContext) -> RoutingDecision:
        """Make a routing decision based on context."""
        original_model = context.model_requested or "auto"
        
        try:
            # Build analysis context
            analysis_context = {
                "tool_name": context.tool_name,
                "files": context.files or [],
                "file_types": self._extract_file_types(context.files or [])
            }
            
            if context.additional_context:
                analysis_context.update(context.additional_context)
            
            # Get routing recommendation
            routing_result = self.router.select_model(
                prompt=context.prompt,
                context=analysis_context,
                prefer_free=True
            )
            
            # Decide whether to use routing
            should_route = self._should_apply_routing(original_model, routing_result)
            
            return RoutingDecision(
                original_model=original_model,
                selected_model=routing_result.model.name if should_route else original_model,
                routing_used=should_route,
                confidence=routing_result.confidence,
                reasoning=routing_result.reasoning,
                estimated_cost=routing_result.estimated_cost
            )
            
        except Exception as e:
            logger.error(f"Failed to make routing decision: {e}")
            return RoutingDecision(
                original_model=original_model,
                selected_model=original_model,
                routing_used=False,
                fallback_reason=f"Routing failed: {str(e)}"
            )
    
    def _extract_file_types(self, files: List[str]) -> List[str]:
        """Extract file extensions from file paths."""
        extensions = []
        for file_path in files:
            if "." in file_path:
                ext = "." + file_path.split(".")[-1]
                extensions.append(ext)
        return extensions
    
    def _should_apply_routing(self, original_model: str, routing_result: RoutingResult) -> bool:
        """Determine if routing should be applied."""
        # Always route if we can use a free model
        if routing_result.model.cost_per_token == 0:
            return True
        
        # Route if original model was auto/default
        if original_model.lower() in ["auto", "default", ""]:
            return True
            
        # Route if confidence is very high
        if routing_result.confidence > 0.8:
            return True
            
        # Route if we have a specialized model
        if "specialized" in routing_result.reasoning.lower():
            return True
            
        # Route if original model is not available
        original_available = self._is_model_available(original_model)
        if not original_available:
            return True
            
        return False
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available."""
        try:
            # Try to find the model in our router's model list
            return model_name in self.router.models
        except Exception:
            return True  # Assume available if we can't check
    
    def _track_call_result(self, 
                          context: ModelCallContext,
                          routing_decision: Optional[RoutingDecision],
                          success: bool,
                          duration: float,
                          error: str = None):
        """Track the result of a model call."""
        call_record = {
            "timestamp": time.time(),
            "tool_name": context.tool_name,
            "success": success,
            "duration": duration,
            "error": error
        }
        
        if routing_decision:
            call_record.update({
                "original_model": routing_decision.original_model,
                "selected_model": routing_decision.selected_model,
                "routing_used": routing_decision.routing_used,
                "confidence": routing_decision.confidence,
                "reasoning": routing_decision.reasoning,
                "estimated_cost": routing_decision.estimated_cost
            })
            
            # Update router performance tracking
            if self.router:
                self.router.update_model_performance(
                    routing_decision.selected_model, 
                    success, 
                    error
                )
        
        self.call_history.append(call_record)
        
        # Keep only last 1000 records
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """Get statistics about model calls."""
        if not self.call_history:
            return {"total_calls": 0}
        
        total_calls = len(self.call_history)
        successful_calls = sum(1 for call in self.call_history if call["success"])
        routed_calls = sum(1 for call in self.call_history if call.get("routing_used", False))
        free_model_calls = sum(1 for call in self.call_history 
                              if call.get("estimated_cost", 1) == 0)
        
        total_cost = sum(call.get("estimated_cost", 0) for call in self.call_history)
        avg_duration = sum(call["duration"] for call in self.call_history) / total_calls
        
        # Tool breakdown
        tool_stats = {}
        for call in self.call_history:
            tool = call["tool_name"]
            if tool not in tool_stats:
                tool_stats[tool] = {"calls": 0, "successes": 0, "routed": 0}
            tool_stats[tool]["calls"] += 1
            if call["success"]:
                tool_stats[tool]["successes"] += 1
            if call.get("routing_used", False):
                tool_stats[tool]["routed"] += 1
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "routed_calls": routed_calls,
            "routing_rate": routed_calls / total_calls if total_calls > 0 else 0,
            "free_model_calls": free_model_calls,
            "free_model_rate": free_model_calls / total_calls if total_calls > 0 else 0,
            "total_estimated_cost": total_cost,
            "average_duration": avg_duration,
            "tool_breakdown": tool_stats
        }
    
    def get_recent_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent failed calls for debugging."""
        failures = [call for call in self.call_history if not call["success"]]
        return failures[-limit:] if failures else []
    
    def clear_history(self):
        """Clear call history."""
        self.call_history.clear()


class RoutingModelProvider:
    """
    A model provider wrapper that adds routing capabilities.
    
    This class can wrap existing model providers to add intelligent routing
    while maintaining the same interface.
    """
    
    def __init__(self, original_provider, wrapper: ModelWrapper):
        self.original_provider = original_provider
        self.wrapper = wrapper
        
        # Preserve original provider interface
        for attr_name in dir(original_provider):
            if not attr_name.startswith('_') and not hasattr(self, attr_name):
                attr = getattr(original_provider, attr_name)
                if callable(attr):
                    setattr(self, attr_name, attr)
    
    def create_model(self, *args, **kwargs):
        """Wrap model creation with routing."""
        # Extract context for routing
        context = ModelCallContext(
            tool_name=kwargs.get('tool_name', 'unknown'),
            prompt=kwargs.get('prompt', ''),
            model_requested=kwargs.get('model', 'auto'),
            temperature=kwargs.get('temperature'),
            max_tokens=kwargs.get('max_tokens')
        )
        
        # Create wrapped call
        original_create = self.original_provider.create_model
        wrapped_create = self.wrapper.wrap_model_call(original_create, context)
        
        return wrapped_create(*args, **kwargs)


def create_routing_wrapper(router: Optional[ModelLevelRouter] = None) -> ModelWrapper:
    """
    Create a model wrapper for routing capabilities.
    
    Args:
        router: Optional router instance, creates default if None
        
    Returns:
        ModelWrapper instance ready for use
    """
    return ModelWrapper(router)

def wrap_provider_with_routing(provider, wrapper: ModelWrapper):
    """
    Wrap a model provider with routing capabilities.
    
    Args:
        provider: Original model provider
        wrapper: ModelWrapper instance
        
    Returns:
        RoutingModelProvider that adds routing to the original provider
    """
    return RoutingModelProvider(provider, wrapper)