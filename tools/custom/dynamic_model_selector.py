"""
Dynamic Model Selector for Consensus Tools

DEPRECATED: This module is now a compatibility wrapper.

The dynamic model selector has been refactored into a modular architecture:
- For new projects: Use `from model_selector import ModelSelector, create_default_selector`
- For advanced usage: Import from `model_selector` package components
- For backward compatibility: This module still provides the original DynamicModelSelector

See model_selector/README.md for full documentation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import the new modular architecture
from .model_selector.orchestrator import create_model_selector
from .model_selector.api import ModelSelector as NewModelSelector

logger = logging.getLogger(__name__)

# Path to the master models data file and bands configuration
MODELS_CSV_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models.csv"
BANDS_CONFIG_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "bands_config.json"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models_schema.json"


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
        self._orchestrator = create_model_selector(
            str(MODELS_CSV_PATH),
            str(BANDS_CONFIG_PATH), 
            str(SCHEMA_PATH)
        )
        
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
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info
        }
    
    def reload_data(self, force: bool = False) -> Dict:
        """Reload data - delegates to new architecture."""
        result = self._orchestrator.reload_data(force)
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info
        }


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
        models_csv_path=str(MODELS_CSV_PATH),
        bands_config_path=str(BANDS_CONFIG_PATH),
        schema_path=str(SCHEMA_PATH)
    )