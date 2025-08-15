"""
Dynamic Model Selector Custom Tool

This tool provides intelligent model selection capabilities for consensus operations
and other tasks requiring optimal model matching based on requirements.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.types import TextContent
from pydantic import BaseModel, Field

from tools.shared.base_models import ToolRequest
from tools.simple.base import SimpleTool

# Import the new modular architecture
try:
    from .model_selector.api import ModelSelector as NewModelSelector
    from .model_selector.orchestrator import create_model_selector

    HAS_MODEL_SELECTOR = True
except ImportError:
    HAS_MODEL_SELECTOR = False

logger = logging.getLogger(__name__)

# Path to the master models data file and bands configuration
MODELS_CSV_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models.csv"
BANDS_CONFIG_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "bands_config.json"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models_schema.json"


class DynamicModelSelectorRequest(ToolRequest):
    """Request model for dynamic model selection."""

    requirements: str = Field(description="Description of the task requirements for model selection")
    task_type: str = Field(default="general", description="Type of task (consensus, analysis, coding, writing, etc.)")
    complexity_level: str = Field(default="medium", description="Complexity level (low, medium, high, critical)")
    budget_preference: str = Field(
        default="balanced", description="Budget preference (cost-optimized, balanced, performance)"
    )
    num_models: int = Field(default=3, description="Number of models to select")


class DynamicModelSelectorTool(SimpleTool):
    """Tool for intelligent model selection based on requirements."""

    def get_name(self) -> str:
        return "dynamic_model_selector"

    def get_description(self) -> str:
        return "Intelligently selects optimal AI models based on task requirements, complexity, and budget preferences."

    def get_tool_fields(self) -> Dict[str, Any]:
        """Return tool-specific field definitions for schema generation."""
        return {
            "requirements": {
                "type": "string",
                "description": "Description of the task requirements for model selection",
            },
            "task_type": {
                "type": "string",
                "default": "general",
                "description": "Type of task (consensus, analysis, coding, writing, etc.)",
            },
            "complexity_level": {
                "type": "string",
                "default": "medium",
                "enum": ["low", "medium", "high", "critical"],
                "description": "Complexity level (low, medium, high, critical)",
            },
            "budget_preference": {
                "type": "string",
                "default": "balanced",
                "enum": ["cost-optimized", "balanced", "performance"],
                "description": "Budget preference (cost-optimized, balanced, performance)",
            },
            "num_models": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 10,
                "description": "Number of models to select",
            },
        }

    def get_required_fields(self) -> list[str]:
        """Return list of required field names."""
        return ["requirements"]

    def get_system_prompt(self) -> str:
        return """You are a dynamic model selection assistant. Your role is to analyze task requirements and recommend the most suitable AI models based on:

1. Task complexity and requirements
2. Budget constraints and preferences  
3. Model capabilities and strengths
4. Performance vs cost optimization

Provide clear reasoning for your model selections and explain trade-offs."""

    def get_request_model(self):
        return DynamicModelSelectorRequest

    async def prepare_prompt(self, request) -> str:
        """Prepare the model selection prompt."""

        # Try to use the new model selector if available
        if HAS_MODEL_SELECTOR:
            try:
                selector = create_model_selector()
                # Use the new selector for recommendations
                prompt = f"""Analyze the following requirements and provide model recommendations:

Task Requirements: {request.requirements}
Task Type: {request.task_type}
Complexity Level: {request.complexity_level}
Budget Preference: {request.budget_preference}
Number of Models Needed: {request.num_models}

Please provide:
1. {request.num_models} recommended models with rationale
2. Cost-benefit analysis for each recommendation
3. Alternative options if primary choices are unavailable
4. Task-specific optimization suggestions

Use the available model data to make informed recommendations."""

            except Exception as e:
                logger.warning(f"Failed to use new model selector: {e}")
                prompt = self._fallback_prompt(request)
        else:
            prompt = self._fallback_prompt(request)

        return prompt

    def _fallback_prompt(self, request) -> str:
        """Fallback prompt when model selector is not available."""
        return f"""Based on the following requirements, recommend suitable AI models:

Requirements: {request.requirements}
Task Type: {request.task_type}
Complexity: {request.complexity_level}
Budget: {request.budget_preference}
Models Needed: {request.num_models}

Provide model recommendations with:
1. Model names and reasoning
2. Strengths for this specific task
3. Cost considerations
4. Performance expectations
5. Fallback alternatives

Consider popular models like GPT-4, Claude, Gemini, and specialized models for specific tasks."""


# Legacy compatibility class
class DynamicModelSelector:
    """
    DEPRECATED: Compatibility wrapper for the new modular architecture.

    For new projects, use:
        from model_selector import ModelSelector, create_default_selector
        selector = create_default_selector()

    This class provides backward compatibility for existing code.
    """

    def __init__(self):
        """Initialize with the new modular orchestrator."""
        logger.warning(
            "DynamicModelSelector is deprecated. Use 'from model_selector import create_default_selector' "
            "for new projects. See model_selector/README.md for documentation."
        )

        # Initialize the new orchestrator
        self._orchestrator = create_model_selector(str(MODELS_CSV_PATH), str(BANDS_CONFIG_PATH), str(SCHEMA_PATH))

        # For backward compatibility
        self.models_data = []
        self.parsed_models = {}
        self.bands_config = {}
        self.schema = None

    def select_consensus_models(self, org_level: str) -> Tuple[List[str], float]:
        """Select consensus models - delegates to new architecture."""
        return self._orchestrator.select_consensus_models(org_level)

    def select_layered_consensus_models(self, org_level: str) -> Tuple[Dict[str, List[str]], float]:
        """Select layered consensus models - delegates to new architecture."""
        return self._orchestrator.select_layered_consensus_models(org_level)

    def create_layered_role_assignments(self, layered_models: Dict[str, List[str]]) -> List[Dict]:
        """Create role assignments - delegates to new architecture."""
        return self._orchestrator.create_layered_role_assignments(layered_models)

    def get_best_model_for_role(self, role: str, org_level: str) -> Optional[str]:
        """Get best model for role - delegates to new architecture."""
        return self._orchestrator.get_best_model_for_role(role, org_level)

    def get_large_context_models(self, min_context: int = 500000) -> List[str]:
        """Get large context models - delegates to new architecture."""
        return self._orchestrator.get_large_context_models(min_context)

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get model info - delegates to new architecture."""
        model_data = self._orchestrator.get_model_info(model_name)
        if model_data:
            # Convert to dict format for backward compatibility
            return {
                "name": model_data.name,
                "rank": model_data.rank,
                "tier": model_data.tier.value,
                "status": model_data.status.value,
                "context_window": model_data.context_window,
                "input_cost": model_data.input_cost,
                "output_cost": model_data.output_cost,
                "org_level": model_data.org_level.value,
                "specialization": model_data.specialization.value,
                "role": model_data.role,
                "strength": model_data.strength,
                "humaneval_score": model_data.humaneval_score,
                "swe_bench_score": model_data.swe_bench_score,
                "openrouter_url": model_data.openrouter_url,
                "last_updated": model_data.last_updated,
                "price_tier": model_data.price_tier,
            }
        return None

    def get_models_by_tier(self, tier: str) -> List[str]:
        """Get models by tier - delegates to new architecture."""
        return self._orchestrator.get_models_by_tier(tier)

    def get_models_by_specialization(self, specialization: str, tier: Optional[str] = None) -> List[str]:
        """Get models by specialization - delegates to new architecture."""
        return self._orchestrator.get_models_by_specialization(specialization, tier)

    def get_context_window_band(self, context_tokens: int) -> str:
        """Get context window band - delegates to new architecture."""
        return self._orchestrator.get_context_window_band(context_tokens)

    def get_cost_tier_band(self, input_cost: float) -> str:
        """Get cost tier band - delegates to new architecture."""
        return self._orchestrator.get_cost_tier_band(input_cost)

    def select_models_by_context_band(self, band: str, max_count: int = 5) -> List[str]:
        """Select models by context band - delegates to new architecture."""
        return self._orchestrator.select_models_by_context_band(band, max_count)

    def select_models_by_cost_tier(self, tier: str, max_count: int = 5) -> List[str]:
        """Select models by cost tier - delegates to new architecture."""
        return self._orchestrator.select_models_by_cost_tier(tier, max_count)

    def estimate_cost(self, models: List[str], org_level: str) -> float:
        """Estimate cost - delegates to new architecture."""
        return self._orchestrator.estimate_cost(models, org_level)

    def compare_model_costs(self, models: List[str]) -> List[Dict]:
        """Compare model costs - delegates to new architecture."""
        return self._orchestrator.compare_model_costs(models)

    def get_cost_efficiency_ranking(self) -> List[Dict]:
        """Get cost efficiency ranking - delegates to new architecture."""
        return self._orchestrator.get_cost_efficiency_ranking()

    def validate_data(self) -> Dict:
        """Validate data - delegates to new architecture."""
        result = self._orchestrator.validate_data()
        return {"is_valid": result.is_valid, "errors": result.errors, "warnings": result.warnings, "info": result.info}

    def reload_data(self, force: bool = False) -> Dict:
        """Reload data - delegates to new architecture."""
        result = self._orchestrator.reload_data(force)
        return {"is_valid": result.is_valid, "errors": result.errors, "warnings": result.warnings, "info": result.info}


# Factory function for backward compatibility
def get_model_selector() -> DynamicModelSelector:
    """
    Factory function to get a model selector instance.

    DEPRECATED: Use 'from model_selector import create_default_selector' instead.

    Returns:
        DynamicModelSelector instance (compatibility wrapper)
    """
    logger.warning(
        "get_model_selector() is deprecated. Use 'from model_selector import create_default_selector' "
        "for new projects."
    )
    return DynamicModelSelector()


# New factory function using the modular architecture (recommended)
def create_default_selector() -> NewModelSelector:
    """
    Create a ModelSelector with default configuration using the new modular architecture.

    This is the recommended way to create a model selector for new projects.

    Returns:
        ModelSelector instance with default configuration

    Example:
        >>> from tools.custom.dynamic_model_selector import create_default_selector
        >>> selector = create_default_selector()
        >>> models, cost = selector.select_consensus_models("senior")
    """
    return NewModelSelector(
        models_csv_path=str(MODELS_CSV_PATH), bands_config_path=str(BANDS_CONFIG_PATH), schema_path=str(SCHEMA_PATH)
    )
