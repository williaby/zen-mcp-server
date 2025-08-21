"""
Layered Consensus Custom Tool

This tool provides sophisticated multi-model consensus analysis with layered
model distribution and role-based assignments for comprehensive decision making.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent
from pydantic import BaseModel, Field

from tools.shared.base_models import ToolRequest
from tools.simple.base import SimpleTool

logger = logging.getLogger(__name__)


class LayeredConsensusRequest(ToolRequest):
    """Request model for layered consensus analysis."""

    question: str = Field(description="The question or proposal to analyze with layered consensus")
    org_level: str = Field(
        default="startup", description="Organization level (startup, scaleup, enterprise) for model distribution"
    )
    model_count: int = Field(default=5, description="Total number of models to use across all layers")
    layers: List[str] = Field(
        default=["strategic", "analytical", "practical"],
        description="Consensus layers to analyze (strategic, analytical, practical, technical)",
    )
    cost_threshold: str = Field(
        default="balanced", description="Cost preference (cost-optimized, balanced, performance)"
    )


class LayeredConsensusTool(SimpleTool):
    """Tool for multi-layered consensus analysis with model distribution."""

    def get_name(self) -> str:
        return "layered_consensus"

    def get_description(self) -> str:
        return "Performs sophisticated multi-model consensus analysis with layered model distribution and role-based assignments."

    def get_tool_fields(self) -> Dict[str, Any]:
        """Return tool-specific field definitions for schema generation."""
        return {
            "question": {"type": "string", "description": "The question or proposal to analyze with layered consensus"},
            "org_level": {
                "type": "string",
                "default": "startup",
                "enum": ["startup", "scaleup", "enterprise"],
                "description": "Organization level (startup, scaleup, enterprise) for model distribution",
            },
            "model_count": {
                "type": "integer",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
                "description": "Total number of models to use across all layers",
            },
            "layers": {
                "type": "array",
                "items": {"type": "string", "enum": ["strategic", "analytical", "practical", "technical"]},
                "default": ["strategic", "analytical", "practical"],
                "description": "Consensus layers to analyze (strategic, analytical, practical, technical)",
            },
            "cost_threshold": {
                "type": "string",
                "default": "balanced",
                "enum": ["cost-optimized", "balanced", "performance"],
                "description": "Cost preference (cost-optimized, balanced, performance)",
            },
        }

    def get_required_fields(self) -> list[str]:
        """Return list of required field names."""
        return ["question"]

    def get_system_prompt(self) -> str:
        return """You are a layered consensus analysis assistant. Your role is to coordinate multiple AI models across different analytical layers to reach comprehensive consensus.

Your responsibilities:
1. Distribute models across strategic, analytical, and practical layers
2. Assign specific roles to each model (devil's advocate, optimist, pragmatist, etc.)
3. Synthesize perspectives from each layer
4. Identify areas of agreement and disagreement
5. Provide balanced final recommendations

Maintain objectivity and ensure each layer contributes unique value to the analysis."""

    def get_request_model(self):
        return LayeredConsensusRequest

    async def prepare_prompt(self, request) -> str:
        """Prepare the layered consensus prompt."""

        # Create layer-specific analysis structure
        layer_assignments = self._create_layer_assignments(request)

        prompt = f"""Conduct a layered consensus analysis on the following:

QUESTION/PROPOSAL: {request.question}

ANALYSIS FRAMEWORK:
Organization Level: {request.org_level}
Total Models: {request.model_count}
Analysis Layers: {', '.join(request.layers)}
Cost Preference: {request.cost_threshold}

LAYER ASSIGNMENTS:
{self._format_layer_assignments(layer_assignments)}

INSTRUCTIONS:
1. For each layer, provide distinct analytical perspective
2. Consider layer-specific concerns and priorities
3. Identify consensus points and disagreements across layers
4. Synthesize findings into coherent recommendation
5. Highlight confidence levels and uncertainties

Provide comprehensive analysis covering all specified layers."""

        return prompt

    def _create_layer_assignments(self, request) -> Dict[str, List[str]]:
        """Create model assignments for each analysis layer using available models."""
        
        # Import registry system
        from providers.registry import ModelProviderRegistry
        
        # Get actually available models
        available_models = ModelProviderRegistry.get_available_model_names()
        
        if not available_models:
            logger.error("No models available in registry")
            # Ultimate fallback
            return {layer: ["gemini-2.5-flash"] for layer in request.layers}
        
        # Categorize models by capability/cost
        model_categories = self._categorize_available_models(available_models, request.cost_threshold)
        
        # Distribute models across layers based on org level and cost preference
        return self._distribute_models_to_layers(model_categories, request)

    def _categorize_available_models(self, available_models: List[str], cost_threshold: str) -> Dict[str, List[str]]:
        """Categorize available models by capability and cost."""
        
        # Define model tiers based on actual available models
        premium_models = []
        balanced_models = []
        cost_effective_models = []
        
        for model in available_models:
            model_lower = model.lower()
            
            # Premium models (high capability, higher cost)
            if any(premium in model_lower for premium in [
                "opus-4", "gpt-5", "o3", "deepseek-r1", "gemini-2.5-pro"
            ]):
                premium_models.append(model)
            
            # Cost-effective models (free or low cost)
            elif ":free" in model or any(free in model_lower for free in [
                "phi-4", "deepseek-chat", "gemini-2.0-flash", "llama"
            ]):
                cost_effective_models.append(model)
            
            # Balanced models (everything else)
            else:
                balanced_models.append(model)
        
        # Select models based on cost preference
        if cost_threshold == "performance":
            selected = premium_models + balanced_models + cost_effective_models
        elif cost_threshold == "cost-optimized":
            selected = cost_effective_models + balanced_models + premium_models
        else:  # balanced
            selected = balanced_models + cost_effective_models + premium_models
        
        # Ensure we have models to work with
        if not selected:
            selected = available_models
        
        return {
            "selected": selected[:10],  # Limit to reasonable number
            "premium": premium_models,
            "balanced": balanced_models, 
            "cost_effective": cost_effective_models
        }

    def _distribute_models_to_layers(self, model_categories: Dict[str, List[str]], request) -> Dict[str, List[str]]:
        """Distribute models intelligently across layers."""
        
        available_models = model_categories["selected"]
        models_per_layer = max(1, request.model_count // len(request.layers))
        
        # Layer-specific model preferences
        layer_preferences = {
            "strategic": model_categories["premium"] + model_categories["balanced"],  # High-level thinking
            "analytical": model_categories["balanced"] + model_categories["premium"],  # Detailed analysis  
            "practical": model_categories["cost_effective"] + model_categories["balanced"],  # Practical concerns
            "technical": model_categories["balanced"] + model_categories["premium"]  # Technical depth
        }
        
        assignments = {}
        used_models = set()
        
        for layer in request.layers:
            layer_models = []
            preferred = layer_preferences.get(layer, available_models)
            
            # Select models for this layer, avoiding duplicates where possible
            for model in preferred:
                if len(layer_models) >= models_per_layer:
                    break
                if model not in used_models or len(available_models) <= request.model_count:
                    layer_models.append(model)
                    used_models.add(model)
            
            # Fill remaining slots if needed
            while len(layer_models) < models_per_layer:
                for model in available_models:
                    if len(layer_models) >= models_per_layer:
                        break
                    if model not in layer_models:  # Allow reuse if needed
                        layer_models.append(model)
                        break
            
            assignments[layer] = layer_models
        
        return assignments

    def _format_layer_assignments(self, assignments: Dict[str, List[str]]) -> str:
        """Format layer assignments for display."""

        formatted = []
        layer_descriptions = {
            "strategic": "High-level strategic thinking, long-term implications",
            "analytical": "Detailed analysis, data-driven insights",
            "practical": "Implementation feasibility, operational considerations",
            "technical": "Technical implementation, system architecture",
        }

        for layer, models in assignments.items():
            description = layer_descriptions.get(layer, "General analysis")
            formatted.append(f"• {layer.upper()}: {', '.join(models)} - {description}")

        return "\n".join(formatted)


# Legacy compatibility - simplified implementations
class LayeredConfigV2:
    """Compatibility class for configuration."""

    def __init__(self, **kwargs):
        self.config = kwargs


class OrgLevel:
    STARTUP = "startup"
    SCALEUP = "scaleup"
    ENTERPRISE = "enterprise"


class CostThreshold:
    LOW = "cost-optimized"
    MEDIUM = "balanced"
    HIGH = "performance"


class DefaultModel:
    """Default model configurations."""

    FAST = "gpt-4o-mini"
    BALANCED = "claude-3.5-sonnet"
    PREMIUM = "gpt-4o"


# Exception classes for backward compatibility
class LayeredConsensusError(Exception):
    """Base exception for layered consensus operations."""

    pass


class ModelSelectionError(LayeredConsensusError):
    """Error in model selection process."""

    pass


class FormatConversionError(LayeredConsensusError):
    """Error in format conversion."""

    pass


class ConsensusExecutionError(LayeredConsensusError):
    """Error during consensus execution."""

    pass


class ConfigurationError(LayeredConsensusError):
    """Configuration validation error."""

    pass


class ValidationError(LayeredConsensusError):
    """Input validation error."""

    pass


# Factory function for backward compatibility
def create_layered_consensus_tool(config=None, model_selector=None):
    """Factory function to create layered consensus tool."""
    return LayeredConsensusTool()


def create_layered_consensus_v2(config=None, model_selector=None):
    """Factory function to create v2 layered consensus tool."""
    return LayeredConsensusTool()


def create_custom_layered_consensus_v2(config=None, model_selector=None):
    """Factory function to create custom v2 layered consensus tool."""
    return LayeredConsensusTool()
