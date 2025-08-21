"""
Dynamic Model Routing System for Zen MCP Server

This module provides intelligent model selection based on task complexity,
cost optimization, and availability. Designed to prioritize free models
while providing escalation paths to premium models when needed.
"""

from .model_level_router import ModelLevelRouter
from .complexity_analyzer import ComplexityAnalyzer

__version__ = "1.0.0"
__all__ = ["ModelLevelRouter", "ComplexityAnalyzer"]

# Default router instance for easy importing
default_router = None

def get_default_router():
    """Get the default ModelLevelRouter instance."""
    global default_router
    if default_router is None:
        default_router = ModelLevelRouter()
    return default_router

def route_model(prompt: str, context: dict = None, prefer_free: bool = True):
    """
    Convenience function for quick model routing.
    
    Args:
        prompt: The input prompt/task description
        context: Additional context (file types, previous errors, etc.)
        prefer_free: Whether to prioritize free models
        
    Returns:
        dict: Selected model information
    """
    router = get_default_router()
    return router.select_model(prompt, context, prefer_free)