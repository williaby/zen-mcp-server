"""
Model Level Router - Core routing logic for dynamic model selection.

Categorizes models into levels (free, junior, senior, executive) and
provides intelligent selection based on task complexity and cost optimization.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .complexity_analyzer import ComplexityAnalyzer, TaskType

logger = logging.getLogger(__name__)

class ModelLevel(Enum):
    """Model capability levels."""
    FREE = "free"
    JUNIOR = "junior"
    SENIOR = "senior"
    EXECUTIVE = "executive"

@dataclass
class ModelInfo:
    """Model information container."""
    name: str
    level: ModelLevel
    cost_per_token: float = 0.0
    specializations: List[TaskType] = field(default_factory=list)
    max_tokens: int = 4096
    context_window: int = 4096
    is_available: bool = True
    last_error: Optional[str] = None
    error_count: int = 0
    success_rate: float = 1.0
    aliases: List[str] = field(default_factory=list)

@dataclass
class RoutingResult:
    """Model selection result."""
    model: ModelInfo
    confidence: float
    reasoning: str
    fallback_models: List[ModelInfo]
    estimated_cost: float = 0.0

class ModelLevelRouter:
    """
    Dynamic model routing system with level-based selection.
    
    Features:
    - Free model prioritization
    - Intelligent complexity analysis
    - Automatic fallback handling
    - Cost tracking and optimization
    - Performance monitoring
    """

    def __init__(self, config_path: Optional[str] = None, models_config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.models_config_path = models_config_path or self._get_default_models_config_path()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.models: Dict[str, ModelInfo] = {}
        self.level_models: Dict[ModelLevel, List[ModelInfo]] = {
            level: [] for level in ModelLevel
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

        self._load_configurations()
        self._initialize_models()

    def _get_default_config_path(self) -> str:
        """Get default routing configuration path."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "routing", "model_routing_config.json")

    def _get_default_models_config_path(self) -> str:
        """Get default models configuration path."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "conf", "custom_models.json")

    def _load_configurations(self):
        """Load routing and model configurations."""
        try:
            # Load routing config
            if os.path.exists(self.config_path):
                with open(self.config_path) as f:
                    self.routing_config = json.load(f)
            else:
                logger.warning(f"Routing config not found: {self.config_path}")
                self.routing_config = self._get_default_routing_config()

            # Load models config
            if os.path.exists(self.models_config_path):
                with open(self.models_config_path) as f:
                    self.models_config = json.load(f)
            else:
                logger.warning(f"Models config not found: {self.models_config_path}")
                self.models_config = {}

        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            self.routing_config = self._get_default_routing_config()
            self.models_config = {}

    def _get_default_routing_config(self) -> Dict[str, Any]:
        """Get default routing configuration."""
        return {
            "levels": {
                "free": {"cost_limit": 0.0, "priority": 1},
                "junior": {"cost_limit": 0.001, "priority": 2},
                "senior": {"cost_limit": 0.01, "priority": 3},
                "executive": {"cost_limit": 0.1, "priority": 4}
            },
            "complexity_thresholds": {
                "simple": {"max_level": "free", "confidence_threshold": 0.8},
                "moderate": {"max_level": "junior", "confidence_threshold": 0.7},
                "complex": {"max_level": "senior", "confidence_threshold": 0.6},
                "expert": {"max_level": "executive", "confidence_threshold": 0.5}
            },
            "fallback_strategy": "escalate",
            "cost_optimization": True,
            "free_model_preference": True
        }

    def _initialize_models(self):
        """Initialize model information from configurations."""
        self.models.clear()
        for level in ModelLevel:
            self.level_models[level].clear()

        # Process models from custom_models.json - using the actual structure
        models_list = self.models_config.get("models", [])

        for model_config in models_list:
            if not isinstance(model_config, dict):
                continue

            model_name = model_config.get("model_name", "")
            if not model_name:
                continue

            # Determine model level
            level = self._determine_model_level(model_name, model_config)

            # Extract model info
            model_info = ModelInfo(
                name=model_name,
                level=level,
                cost_per_token=self._estimate_cost_per_token(model_name, model_config),
                max_tokens=model_config.get('max_output_tokens', 4096),
                context_window=model_config.get('context_window', 4096),
                specializations=self._extract_specializations(model_config),
                aliases=model_config.get('aliases', [])
            )

            self.models[model_info.name] = model_info
            self.level_models[level].append(model_info)

        # Sort models by preference within each level
        for level in ModelLevel:
            self.level_models[level].sort(key=self._model_sort_key)

        logger.info(f"Initialized {len(self.models)} models across {len(ModelLevel)} levels")

    def _determine_model_level(self, model_name: str, model_config: Dict[str, Any]) -> ModelLevel:
        """Determine the level of a model based on its configuration."""
        # Check if explicitly marked as free
        if (model_name.endswith(':free') or
            'free' in model_name.lower() or
            model_config.get('is_custom', False)):  # Local models are typically free
            return ModelLevel.FREE

        # Check routing config for level mappings
        level_mappings = self.routing_config.get('model_level_mappings', {})
        for level_name, model_patterns in level_mappings.items():
            if any(pattern in model_name.lower() for pattern in model_patterns):
                return ModelLevel(level_name)

        # Heuristic-based level determination based on model names
        model_lower = model_name.lower()

        # Executive level (premium models)
        if any(keyword in model_lower for keyword in [
            'gpt-4', 'gpt-5', 'claude-opus', 'claude-4', 'o3-pro', 'o4'
        ]):
            return ModelLevel.EXECUTIVE

        # Senior level (capable models)
        elif any(keyword in model_lower for keyword in [
            'gpt-3.5', 'claude-sonnet', 'claude-3', 'gemini-pro', 'gemini-2.5-pro',
            'o3-mini', 'mistral-large'
        ]):
            return ModelLevel.SENIOR

        # Junior level (entry-level paid models)
        elif any(keyword in model_lower for keyword in [
            'claude-haiku', 'gemini-flash', 'mistral', 'llama-3-70b'
        ]):
            return ModelLevel.JUNIOR

        # Default to FREE for everything else (especially local models)
        else:
            return ModelLevel.FREE

    def _estimate_cost_per_token(self, model_name: str, model_config: Dict[str, Any]) -> float:
        """Estimate cost per token based on model type."""
        # Free models (local, marked as free)
        if (model_name.endswith(':free') or
            'free' in model_name.lower() or
            model_config.get('is_custom', False)):
            return 0.0

        # Rough cost estimates (per 1K tokens)
        model_lower = model_name.lower()

        if any(keyword in model_lower for keyword in ['gpt-4', 'gpt-5', 'o3-pro', 'o4']):
            return 0.03  # Premium models
        elif any(keyword in model_lower for keyword in ['claude-opus', 'claude-4']):
            return 0.015  # High-end Claude
        elif any(keyword in model_lower for keyword in ['claude-sonnet', 'gemini-pro']):
            return 0.003  # Mid-tier
        elif any(keyword in model_lower for keyword in ['claude-haiku', 'gpt-3.5']):
            return 0.0005  # Entry level
        else:
            return 0.001  # Default estimate

    def _extract_specializations(self, model_config: Dict[str, Any]) -> List[TaskType]:
        """Extract task type specializations from model config."""
        specializations = []

        # Check explicit specializations
        if 'specializations' in model_config:
            for spec in model_config['specializations']:
                try:
                    specializations.append(TaskType(spec))
                except ValueError:
                    continue

        # Infer specializations from model description or name
        description = model_config.get('description', '').lower()
        model_name = model_config.get('model_name', '').lower()

        # Code-related specializations
        if any(keyword in description + model_name for keyword in ['code', 'coder', 'programming']):
            specializations.extend([TaskType.CODE_GENERATION, TaskType.CODE_REVIEW])

        # Analysis specializations
        if any(keyword in description for keyword in ['analysis', 'reasoning', 'thinking']):
            specializations.append(TaskType.ANALYSIS)

        # Debugging specializations
        if any(keyword in description for keyword in ['debug', 'fix', 'problem']):
            specializations.append(TaskType.DEBUGGING)

        # Vision models for analysis
        if model_config.get('supports_images', False):
            specializations.append(TaskType.ANALYSIS)

        return specializations or [TaskType.GENERAL]

    def _model_sort_key(self, model: ModelInfo) -> Tuple[int, float, float]:
        """Sorting key for model preference (lower is better)."""
        # Priority: cost (free first), success rate (higher better), error count (lower better)
        cost_priority = 0 if model.cost_per_token == 0 else 1
        success_penalty = 1.0 - model.success_rate
        return (cost_priority, success_penalty, model.error_count)

    def analyze_task_complexity(self, prompt: str, context: Dict[str, Any] = None) -> Tuple[str, float, TaskType]:
        """
        Analyze task complexity and type.
        
        Args:
            prompt: The input prompt/task description
            context: Additional context information
            
        Returns:
            tuple: (complexity_level, confidence, task_type)
        """
        return self.complexity_analyzer.analyze(prompt, context)

    def select_model(self,
                    prompt: str,
                    context: Dict[str, Any] = None,
                    prefer_free: bool = True,
                    max_cost: float = None) -> RoutingResult:
        """
        Select the best model for a given prompt and context.
        
        Args:
            prompt: The input prompt/task description
            context: Additional context (file types, errors, etc.)
            prefer_free: Whether to prioritize free models
            max_cost: Maximum allowed cost per token
            
        Returns:
            RoutingResult with selected model and reasoning
        """
        cache_key = self._get_cache_key(prompt, context, prefer_free, max_cost)

        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result

        # Analyze task complexity and type
        complexity, confidence, task_type = self.analyze_task_complexity(prompt, context)

        # Determine required model level
        required_level = self._get_required_level(complexity, confidence)

        # Get candidate models
        candidates = self._get_candidate_models(required_level, task_type, max_cost, prefer_free)

        if not candidates:
            # Fallback to any available model
            candidates = self._get_fallback_models(max_cost)

        if not candidates:
            raise RuntimeError("No suitable models available")

        # Select best model
        selected_model = candidates[0]
        fallback_models = candidates[1:5]  # Top 5 alternatives

        # Calculate estimated cost
        estimated_tokens = self._estimate_token_count(prompt)
        estimated_cost = estimated_tokens * selected_model.cost_per_token

        # Create result
        result = RoutingResult(
            model=selected_model,
            confidence=confidence,
            reasoning=self._generate_reasoning(selected_model, complexity, task_type, prefer_free),
            fallback_models=fallback_models,
            estimated_cost=estimated_cost
        )

        # Cache result
        self.cache[cache_key] = (result, time.time())

        return result

    def _get_cache_key(self, prompt: str, context: Dict[str, Any], prefer_free: bool, max_cost: float) -> str:
        """Generate cache key for model selection."""
        context_str = str(sorted(context.items())) if context else ""
        return f"{hash(prompt)}_{hash(context_str)}_{prefer_free}_{max_cost}"

    def _get_required_level(self, complexity: str, confidence: float) -> ModelLevel:
        """Determine required model level based on complexity analysis."""
        thresholds = self.routing_config.get('complexity_thresholds', {})

        if complexity in thresholds:
            threshold_config = thresholds[complexity]
            if confidence >= threshold_config.get('confidence_threshold', 0.5):
                return ModelLevel(threshold_config['max_level'])

        # Default mapping
        level_mapping = {
            'simple': ModelLevel.FREE,
            'moderate': ModelLevel.JUNIOR,
            'complex': ModelLevel.SENIOR,
            'expert': ModelLevel.EXECUTIVE
        }

        return level_mapping.get(complexity, ModelLevel.JUNIOR)

    def _get_candidate_models(self,
                            required_level: ModelLevel,
                            task_type: TaskType,
                            max_cost: float = None,
                            prefer_free: bool = True) -> List[ModelInfo]:
        """Get candidate models for selection."""
        candidates = []

        # Start with free models if preferred
        levels_to_check = []
        if prefer_free and self.routing_config.get('free_model_preference', True):
            levels_to_check.append(ModelLevel.FREE)

        # Add required level and potentially higher levels
        current_level_index = list(ModelLevel).index(required_level)
        for i in range(current_level_index, len(ModelLevel)):
            level = list(ModelLevel)[i]
            if level not in levels_to_check:
                levels_to_check.append(level)

        # Collect candidates from each level
        for level in levels_to_check:
            level_candidates = []

            for model in self.level_models[level]:
                # Check availability
                if not model.is_available:
                    continue

                # Check cost constraint
                if max_cost is not None and model.cost_per_token > max_cost:
                    continue

                # Check specialization match
                specialization_bonus = 0
                if task_type in model.specializations:
                    specialization_bonus = 10  # Boost specialized models

                level_candidates.append((model, specialization_bonus))

            # Sort by specialization and model preference
            level_candidates.sort(key=lambda x: (-x[1], self._model_sort_key(x[0])))
            candidates.extend([model for model, _ in level_candidates])

            # If we have good free options and prefer free, stop here
            if (prefer_free and level == ModelLevel.FREE and
                len(candidates) >= 3 and self.routing_config.get('cost_optimization', True)):
                break

        return candidates

    def _get_fallback_models(self, max_cost: float = None) -> List[ModelInfo]:
        """Get fallback models when no suitable models found."""
        fallbacks = []

        for level in [ModelLevel.FREE, ModelLevel.JUNIOR, ModelLevel.SENIOR, ModelLevel.EXECUTIVE]:
            for model in self.level_models[level]:
                if model.is_available:
                    if max_cost is None or model.cost_per_token <= max_cost:
                        fallbacks.append(model)

        return sorted(fallbacks, key=self._model_sort_key)

    def _estimate_token_count(self, prompt: str) -> int:
        """Rough estimation of token count for cost calculation."""
        # Simple heuristic: ~4 characters per token for English text
        return max(len(prompt) // 4, 10)

    def _generate_reasoning(self,
                          model: ModelInfo,
                          complexity: str,
                          task_type: TaskType,
                          prefer_free: bool) -> str:
        """Generate human-readable reasoning for model selection."""
        reasons = []

        if model.cost_per_token == 0:
            reasons.append("selected free model to minimize costs")

        if task_type in model.specializations:
            reasons.append(f"specialized for {task_type.value} tasks")

        reasons.append(f"appropriate for {complexity} complexity level")

        if model.success_rate < 1.0:
            reasons.append(f"model has {model.success_rate:.1%} success rate")

        if prefer_free and model.level == ModelLevel.FREE:
            reasons.append("prioritized due to free model preference")

        return f"Selected {model.name}: " + ", ".join(reasons)

    def update_model_performance(self, model_name: str, success: bool, error: str = None):
        """Update model performance metrics."""
        if model_name not in self.models:
            return

        model = self.models[model_name]

        if success:
            model.error_count = max(0, model.error_count - 1)  # Decay error count
            model.last_error = None
        else:
            model.error_count += 1
            model.last_error = error

            # Disable model if too many consecutive errors
            if model.error_count >= 5:
                model.is_available = False
                logger.warning(f"Disabled model {model_name} due to repeated failures")

        # Update success rate (rolling average)
        total_requests = getattr(model, 'total_requests', 0) + 1
        if success:
            successful_requests = getattr(model, 'successful_requests', 0) + 1
        else:
            successful_requests = getattr(model, 'successful_requests', 0)

        model.success_rate = successful_requests / total_requests
        model.total_requests = total_requests
        model.successful_requests = successful_requests

    def get_model_stats(self) -> Dict[str, Any]:
        """Get routing and model performance statistics."""
        stats = {
            'total_models': len(self.models),
            'available_models': sum(1 for m in self.models.values() if m.is_available),
            'models_by_level': {},
            'cache_size': len(self.cache),
            'top_performers': []
        }

        # Models by level
        for level in ModelLevel:
            level_models = self.level_models[level]
            stats['models_by_level'][level.value] = {
                'total': len(level_models),
                'available': sum(1 for m in level_models if m.is_available),
                'average_success_rate': sum(m.success_rate for m in level_models) / len(level_models) if level_models else 0
            }

        # Top performers
        sorted_models = sorted(
            [m for m in self.models.values() if getattr(m, 'total_requests', 0) > 0],
            key=lambda m: m.success_rate,
            reverse=True
        )
        stats['top_performers'] = [
            {
                'name': m.name,
                'level': m.level.value,
                'success_rate': m.success_rate,
                'total_requests': getattr(m, 'total_requests', 0)
            }
            for m in sorted_models[:5]
        ]

        return stats

    def get_models_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Get models for a specific level."""
        try:
            model_level = ModelLevel(level)
            return [
                {
                    'name': model.name,
                    'aliases': model.aliases,
                    'cost_per_token': model.cost_per_token,
                    'context_window': model.context_window,
                    'max_tokens': model.max_tokens,
                    'specializations': [spec.value for spec in model.specializations],
                    'is_available': model.is_available,
                    'success_rate': model.success_rate
                }
                for model in self.level_models[model_level]
            ]
        except ValueError:
            return []
