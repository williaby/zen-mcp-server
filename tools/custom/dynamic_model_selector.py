"""
Dynamic Model Selector Custom Tool.

Provides intelligent AI model recommendations based on task requirements,
complexity, and budget. This is a *recommender* tool: it returns a ranked
list of suggested models with reasoning, it does NOT execute prompts against
those models.

When to use this tool vs. siblings:
- ``dynamic_model_selector`` -- ask "which models should I use for X?" and
  get a recommendation list with rationale. No model is actually called.
- ``tiered_consensus`` -- run a full multi-model consensus analysis end-to-end
  (selection + execution + synthesis) using a fixed tier (1/2/3). Use this
  when you want answers, not just recommendations.
- ``routing_status`` -- inspect the running dynamic-routing system (status,
  stats, configuration, ad-hoc recommendation). Read-only.

Backend / data source:
- Model metadata is read from ``docs/models/models.csv``,
  ``docs/models/bands_config.json``, and ``docs/models/models_schema.json``.
- Recommendation prompt is sent to whatever model the MCP client passes in
  via the standard ``model`` parameter (this is a SimpleTool); if no model
  is available, the tool falls back to a generic recommendation prompt.

Required environment for downstream execution of recommended models:
- At least one provider API key must be configured for the recommended
  models to actually be callable elsewhere (e.g. ``OPENROUTER_API_KEY``,
  ``GEMINI_API_KEY``, ``OPENAI_API_KEY``, ``XAI_API_KEY``,
  ``ANTHROPIC_API_KEY``, or ``CUSTOM_API_URL`` for local providers).
  This tool itself only needs the model running the recommendation prompt.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import Field

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

    requirements: str = Field(
        description=(
            "Free-form description of the task the recommended models will run. "
            "Be specific about goals, inputs, expected outputs, and any quality bar "
            "(e.g. 'review a 2,000-line Python diff for security issues; prioritize "
            "low false-positive rate over speed'). Required."
        ),
    )
    task_type: str = Field(
        default="general",
        description=(
            "Coarse category that biases the recommendation. Suggested values: "
            "'general', 'consensus', 'analysis', 'coding', 'writing', 'reasoning', "
            "'long_context', 'vision'. Free-form strings are accepted but only the "
            "listed categories have tuned heuristics."
        ),
    )
    complexity_level: str = Field(
        default="medium",
        description=(
            "Difficulty of the underlying task. One of: 'low' (FAQs, simple "
            "transforms), 'medium' (typical code review / Q&A), 'high' (cross-file "
            "refactors, multi-step reasoning), 'critical' (production decisions, "
            "high-stakes review). Drives the org-level band used for selection."
        ),
    )
    budget_preference: str = Field(
        default="balanced",
        description=(
            "Cost vs. capability trade-off. One of: 'cost-optimized' (prefer free "
            "and economy-tier models; accept lower ceiling), 'balanced' (mid-tier "
            "default), 'performance' (top-tier models regardless of cost)."
        ),
    )
    num_models: int = Field(
        default=3,
        description=(
            "How many models to recommend (1-10). Use 1 for a single best pick, "
            "3-5 for consensus seed sets, and higher numbers when you want a "
            "broader survey including fallbacks."
        ),
    )


class DynamicModelSelectorTool(SimpleTool):
    """
    Recommend AI models for a given task without executing the task.

    This tool reads the fork-local model registry (``docs/models/models.csv``
    and ``docs/models/bands_config.json``) and asks an LLM to produce a
    ranked recommendation. It returns natural-language suggestions, not
    structured data; the caller is expected to feed the recommendations
    into another tool (e.g. ``tiered_consensus`` or ``chat`` with an
    explicit model parameter) to actually run the work.

    Behavior:
    - Returns ``num_models`` suggestions with rationale, cost commentary,
      and fallback alternatives.
    - If the modular model selector is unavailable, falls back to a generic
      recommendation prompt that does not depend on local model metadata.
    - Does NOT contact any external API on behalf of the recommended models.

    Limitations:
    - The output is advisory text. Do not parse it as machine-readable
      output -- use ``routing_status`` for structured recommendations.
    - Recommendations are only as good as the underlying CSV; stale model
      data produces stale advice.
    """

    def get_name(self) -> str:
        return "dynamic_model_selector"

    def get_description(self) -> str:
        return (
            "Recommends AI models for a task based on free-form requirements, complexity, and budget. "
            "Returns a ranked list of suggested models with reasoning and cost notes. "
            "Does NOT execute the task -- use chat/tiered_consensus to actually run something. "
            "Use this when you need to decide which model to use; use tiered_consensus when you want answers."
        )

    def get_tool_fields(self) -> dict[str, Any]:
        """Return tool-specific field definitions for schema generation."""
        return {
            "requirements": {
                "type": "string",
                "description": (
                    "Free-form description of the task the recommended models will run. "
                    "Include goal, inputs, expected outputs, and any quality bar. Required."
                ),
            },
            "task_type": {
                "type": "string",
                "default": "general",
                "description": (
                    "Coarse task category that biases the recommendation. Suggested values: "
                    "general, consensus, analysis, coding, writing, reasoning, long_context, vision. "
                    "Free-form strings accepted; only the listed categories have tuned heuristics."
                ),
            },
            "complexity_level": {
                "type": "string",
                "default": "medium",
                "enum": ["low", "medium", "high", "critical"],
                "description": (
                    "Difficulty of the underlying task. low=FAQs/simple transforms, "
                    "medium=typical code review/Q&A, high=cross-file refactors/multi-step reasoning, "
                    "critical=production/high-stakes decisions."
                ),
            },
            "budget_preference": {
                "type": "string",
                "default": "balanced",
                "enum": ["cost-optimized", "balanced", "performance"],
                "description": (
                    "Cost vs. capability trade-off. cost-optimized=prefer free/economy tier, "
                    "balanced=mid-tier default, performance=top-tier regardless of cost."
                ),
            },
            "num_models": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 10,
                "description": (
                    "Number of models to recommend (1-10). Use 1 for a single pick, "
                    "3-5 for consensus seed sets, higher for a broader survey."
                ),
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
                create_model_selector()
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

    def select_consensus_models(self, org_level: str) -> tuple[list[str], float]:
        """Select consensus models - delegates to new architecture."""
        return self._orchestrator.select_consensus_models(org_level)

    def select_layered_consensus_models(self, org_level: str) -> tuple[dict[str, list[str]], float]:
        """Select layered consensus models - delegates to new architecture."""
        return self._orchestrator.select_layered_consensus_models(org_level)

    def create_layered_role_assignments(self, layered_models: dict[str, list[str]]) -> list[dict]:
        """Create role assignments - delegates to new architecture."""
        return self._orchestrator.create_layered_role_assignments(layered_models)

    def get_best_model_for_role(self, role: str, org_level: str) -> str | None:
        """Get best model for role - delegates to new architecture."""
        return self._orchestrator.get_best_model_for_role(role, org_level)

    def get_large_context_models(self, min_context: int = 500000) -> list[str]:
        """Get large context models - delegates to new architecture."""
        return self._orchestrator.get_large_context_models(min_context)

    def get_model_info(self, model_name: str) -> dict | None:
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

    def get_models_by_tier(self, tier: str) -> list[str]:
        """Get models by tier - delegates to new architecture."""
        return self._orchestrator.get_models_by_tier(tier)

    def get_models_by_specialization(self, specialization: str, tier: str | None = None) -> list[str]:
        """Get models by specialization - delegates to new architecture."""
        return self._orchestrator.get_models_by_specialization(specialization, tier)

    def get_context_window_band(self, context_tokens: int) -> str:
        """Get context window band - delegates to new architecture."""
        return self._orchestrator.get_context_window_band(context_tokens)

    def get_cost_tier_band(self, input_cost: float) -> str:
        """Get cost tier band - delegates to new architecture."""
        return self._orchestrator.get_cost_tier_band(input_cost)

    def select_models_by_context_band(self, band: str, max_count: int = 5) -> list[str]:
        """Select models by context band - delegates to new architecture."""
        return self._orchestrator.select_models_by_context_band(band, max_count)

    def select_models_by_cost_tier(self, tier: str, max_count: int = 5) -> list[str]:
        """Select models by cost tier - delegates to new architecture."""
        return self._orchestrator.select_models_by_cost_tier(tier, max_count)

    def estimate_cost(self, models: list[str], org_level: str) -> float:
        """Estimate cost - delegates to new architecture."""
        return self._orchestrator.estimate_cost(models, org_level)

    def compare_model_costs(self, models: list[str]) -> list[dict]:
        """Compare model costs - delegates to new architecture."""
        return self._orchestrator.compare_model_costs(models)

    def get_cost_efficiency_ranking(self) -> list[dict]:
        """Get cost efficiency ranking - delegates to new architecture."""
        return self._orchestrator.get_cost_efficiency_ranking()

    def validate_data(self) -> dict:
        """Validate data - delegates to new architecture."""
        result = self._orchestrator.validate_data()
        return {"is_valid": result.is_valid, "errors": result.errors, "warnings": result.warnings, "info": result.info}

    def reload_data(self, force: bool = False) -> dict:
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
        "get_model_selector() is deprecated. Use 'from model_selector import create_default_selector' for new projects."
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
