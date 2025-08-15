"""
Automated Model Evaluation Criteria
Implements quantitative decision framework for model replacement recommendations
"""

import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Standardized model performance and operational metrics"""

    name: str
    provider: str
    humaneval_score: float
    swe_bench_score: float
    mmlu_score: float
    hellaswag_score: float
    gsm8k_score: Optional[float] = None
    math_score: Optional[float] = None

    # Cost metrics (per million tokens)
    input_cost: float
    output_cost: float

    # Technical specifications
    context_window: int
    max_tokens_per_second: Optional[int] = None

    # Operational metrics
    api_availability: float  # percentage uptime
    rate_limits: Optional[dict] = None
    regional_availability: list[str] = None

    # Strategic factors
    has_multimodal: bool = False
    has_vision: bool = False
    has_code_execution: bool = False
    training_cutoff_date: Optional[str] = None


class ModelEvaluator:
    """
    Automated model evaluation and replacement recommendation system
    """

    def __init__(self, config_path: str = "model_allocation_config.yaml"):
        self.config = self._load_config(config_path)
        self.current_models = []
        self.benchmark_sources = [
            "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard",
            "https://evalplus.github.io/leaderboard.html",
            # Additional benchmark sources
        ]

    def evaluate_model_for_replacement(self, openrouter_url: str) -> dict:
        """
        Main evaluation function - takes OpenRouter URL and returns replacement recommendation

        Args:
            openrouter_url: URL to OpenRouter model page

        Returns:
            Dict with evaluation results and replacement recommendation
        """
        try:
            # Phase 1: Extract model data from OpenRouter
            model_data = self._extract_openrouter_data(openrouter_url)
            if not model_data:
                return {"error": "Failed to extract model data from OpenRouter URL"}

            # Phase 2: Gather performance benchmarks
            metrics = self._gather_model_metrics(model_data)
            if not metrics:
                return {"error": "Failed to gather sufficient performance metrics"}

            # Phase 3: Basic qualification check
            if not self._passes_basic_qualification(metrics):
                return {
                    "qualified": False,
                    "reason": "Model does not meet basic qualification thresholds",
                    "metrics": metrics,
                }

            # Phase 4: Find replacement candidates
            candidates = self._find_replacement_candidates(metrics)
            if not candidates:
                return {
                    "qualified": True,
                    "replacement_recommended": False,
                    "reason": "No suitable replacement candidates found",
                    "metrics": metrics,
                }

            # Phase 5: Calculate replacement scores
            best_replacement = self._calculate_best_replacement(metrics, candidates)

            return {
                "qualified": True,
                "replacement_recommended": best_replacement["score"] >= 7.5,
                "replacement_score": best_replacement["score"],
                "target_model": best_replacement["target"],
                "detailed_analysis": best_replacement["analysis"],
                "implementation_plan": self._generate_implementation_plan(best_replacement),
                "metrics": metrics,
            }

        except Exception as e:
            logger.error(f"Evaluation failed for {openrouter_url}: {e}")
            return {"error": f"Evaluation failed: {str(e)}"}

    def _extract_openrouter_data(self, url: str) -> Optional[dict]:
        """Extract model information from OpenRouter URL"""
        try:
            # Parse model name from URL
            model_name = self._parse_model_name_from_url(url)

            # Fetch model details from OpenRouter API
            api_url = f"https://openrouter.ai/api/v1/models/{model_name}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"OpenRouter API returned {response.status_code} for {model_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to extract OpenRouter data: {e}")
            return None

    def _gather_model_metrics(self, model_data: dict) -> Optional[ModelMetrics]:
        """Gather comprehensive metrics from multiple sources"""
        try:
            # Extract basic info from OpenRouter
            name = model_data.get("id", "")
            provider = name.split("/")[0] if "/" in name else "unknown"

            # Cost information
            pricing = model_data.get("pricing", {})
            input_cost = float(pricing.get("prompt", 0)) * 1_000_000  # Convert to per million
            output_cost = float(pricing.get("completion", 0)) * 1_000_000

            # Technical specs
            context_window = model_data.get("context_length", 0)

            # Gather benchmark scores from multiple sources
            benchmarks = self._fetch_benchmark_scores(name)

            return ModelMetrics(
                name=name,
                provider=provider,
                humaneval_score=benchmarks.get("humaneval", 0),
                swe_bench_score=benchmarks.get("swe_bench", 0),
                mmlu_score=benchmarks.get("mmlu", 0),
                hellaswag_score=benchmarks.get("hellaswag", 0),
                gsm8k_score=benchmarks.get("gsm8k"),
                math_score=benchmarks.get("math"),
                input_cost=input_cost,
                output_cost=output_cost,
                context_window=context_window,
                api_availability=model_data.get("availability", {}).get("uptime", 95),
                has_multimodal=self._detect_multimodal_capability(model_data),
                has_vision=self._detect_vision_capability(model_data),
                training_cutoff_date=model_data.get("training_cutoff"),
            )

        except Exception as e:
            logger.error(f"Failed to gather metrics: {e}")
            return None

    def _passes_basic_qualification(self, metrics: ModelMetrics) -> bool:
        """Check if model meets basic qualification thresholds"""
        return (
            metrics.context_window >= 32000
            and metrics.humaneval_score >= 60
            and metrics.mmlu_score >= 65
            and metrics.input_cost >= 0
            and metrics.api_availability >= 90
        )

    def _find_replacement_candidates(self, new_model: ModelMetrics) -> list[ModelMetrics]:
        """Find existing models that could be replaced by the new model"""
        candidates = []

        # Determine if this is a protected provider (Tier 1)
        is_protected_provider = new_model.provider in ["openai", "anthropic", "google"]

        # Determine price tier of new model
        new_tier = self._classify_price_tier(new_model.input_cost)

        # Determine capability category
        new_capabilities = self._classify_capabilities(new_model)

        # Find models in same tier and capability categories
        for existing in self.current_models:
            existing_tier = self._classify_price_tier(existing.input_cost)
            existing_capabilities = self._classify_capabilities(existing)

            # Apply protected model logic for Tier 1 providers
            if is_protected_provider and existing.provider == new_model.provider:
                # Same provider replacement rules
                if self._is_same_generation_upgrade(new_model, existing):
                    # Same generation upgrade (e.g., Opus 4 -> 4.1)
                    candidates.append(existing)
                elif self._is_cross_generation_replacement(new_model, existing):
                    # Cross generation (e.g., GPT-5 replacing GPT-4 series)
                    candidates.append(existing)
                # Protected models from same provider require special handling
                continue

            # Standard replacement logic for non-protected scenarios
            if existing_tier == new_tier or self._adjacent_tiers(new_tier, existing_tier):

                # Same capability overlap
                if any(cap in existing_capabilities for cap in new_capabilities):
                    # Don't replace protected models unless special conditions met
                    if self._is_protected_model(existing) and not self._meets_protection_exception(existing):
                        continue
                    candidates.append(existing)

        return candidates

    def _calculate_best_replacement(self, new_model: ModelMetrics, candidates: list[ModelMetrics]) -> dict:
        """Calculate replacement score for best candidate"""
        best_score = 0
        best_target = None
        best_analysis = {}

        for candidate in candidates:
            score_breakdown = self._calculate_replacement_score(new_model, candidate)
            total_score = sum(
                score_breakdown[metric] * weight
                for metric, weight in [
                    ("performance", 0.4),
                    ("cost_efficiency", 0.3),
                    ("strategic_value", 0.2),
                    ("operational_benefit", 0.1),
                ]
            )

            if total_score > best_score:
                best_score = total_score
                best_target = candidate
                best_analysis = {
                    "score_breakdown": score_breakdown,
                    "total_score": total_score,
                    "reasoning": self._generate_replacement_reasoning(score_breakdown, new_model, candidate),
                }

        return {"score": best_score, "target": best_target, "analysis": best_analysis}

    def _calculate_replacement_score(self, new_model: ModelMetrics, existing_model: ModelMetrics) -> dict[str, float]:
        """Calculate detailed replacement scores across all criteria"""

        # Check for same-generation upgrade special rules
        is_same_generation = self._is_same_generation_upgrade(new_model, existing_model)
        is_protected_provider = new_model.provider in ["openai", "anthropic", "google"]

        if is_same_generation and is_protected_provider:
            return self._calculate_same_generation_score(new_model, existing_model)

        # Performance improvement (0-10 scale)
        performance_scores = []
        for benchmark in ["humaneval_score", "mmlu_score", "hellaswag_score"]:
            new_score = getattr(new_model, benchmark)
            existing_score = getattr(existing_model, benchmark)
            if existing_score > 0:
                improvement = ((new_score - existing_score) / existing_score) * 100
                performance_scores.append(min(10, max(0, improvement / 5)))  # 50% improvement = 10/10

        performance_score = sum(performance_scores) / len(performance_scores) if performance_scores else 0

        # Cost efficiency (0-10 scale)
        cost_efficiency = 0
        if existing_model.output_cost > 0:
            cost_reduction = ((existing_model.output_cost - new_model.output_cost) / existing_model.output_cost) * 100
            # Score 10/10 for 50% cost reduction, 5/10 for break-even with better performance
            if cost_reduction > 0:
                cost_efficiency = min(10, cost_reduction / 5)
            elif performance_score > 6:  # If significantly better performance
                cost_efficiency = 5  # Neutral score for same cost but better performance

        # Strategic value (0-10 scale)
        strategic_score = 5  # Base neutral score

        # Provider diversity bonus
        if new_model.provider != existing_model.provider:
            strategic_score += 2

        # Capability enhancement bonus
        if (new_model.has_multimodal and not existing_model.has_multimodal) or (
            new_model.context_window > existing_model.context_window * 1.5
        ):
            strategic_score += 2

        # Context window improvement
        if new_model.context_window > existing_model.context_window:
            context_improvement = (
                new_model.context_window - existing_model.context_window
            ) / existing_model.context_window
            strategic_score += min(1, context_improvement)

        strategic_score = min(10, strategic_score)

        # Operational benefit (0-10 scale)
        operational_score = 5  # Base score

        # Reliability improvement
        if new_model.api_availability > existing_model.api_availability:
            operational_score += min(2, (new_model.api_availability - existing_model.api_availability) / 5)

        # Speed improvement (if available)
        if (
            new_model.max_tokens_per_second
            and existing_model.max_tokens_per_second
            and new_model.max_tokens_per_second > existing_model.max_tokens_per_second
        ):
            operational_score += 1

        operational_score = min(10, operational_score)

        return {
            "performance": performance_score,
            "cost_efficiency": cost_efficiency,
            "strategic_value": strategic_score,
            "operational_benefit": operational_score,
        }

    def _generate_replacement_reasoning(
        self, score_breakdown: dict, new_model: ModelMetrics, existing_model: ModelMetrics
    ) -> str:
        """Generate human-readable reasoning for replacement recommendation"""
        reasons = []

        if score_breakdown["performance"] > 7:
            perf_improvement = (
                (new_model.humaneval_score - existing_model.humaneval_score) / existing_model.humaneval_score
            ) * 100
            reasons.append(f"Significant performance improvement: +{perf_improvement:.1f}% on key benchmarks")

        if score_breakdown["cost_efficiency"] > 7:
            cost_reduction = ((existing_model.output_cost - new_model.output_cost) / existing_model.output_cost) * 100
            reasons.append(f"Substantial cost savings: -{cost_reduction:.1f}% output cost reduction")

        if score_breakdown["strategic_value"] > 7:
            if new_model.provider != existing_model.provider:
                reasons.append("Improves provider diversity")
            if new_model.context_window > existing_model.context_window * 1.2:
                reasons.append(
                    f"Larger context window: {new_model.context_window:,} vs {existing_model.context_window:,} tokens"
                )

        if score_breakdown["operational_benefit"] > 7:
            reasons.append(
                f"Better reliability: {new_model.api_availability}% vs {existing_model.api_availability}% uptime"
            )

        return " | ".join(reasons) if reasons else "Marginal improvements across multiple criteria"

    def _generate_implementation_plan(self, replacement_result: dict) -> dict:
        """Generate implementation timeline and steps"""
        if not replacement_result["target"]:
            return {}

        return {
            "timeline": "2-4 weeks",
            "phases": [
                {
                    "phase": "Testing & Validation",
                    "duration": "1 week",
                    "tasks": [
                        "Deploy model in test environment",
                        "Run benchmark validation tests",
                        "Validate API integration",
                        "Performance regression testing",
                    ],
                },
                {
                    "phase": "Gradual Rollout",
                    "duration": "1 week",
                    "tasks": [
                        "Deploy to 10% of consensus operations",
                        "Monitor performance and costs",
                        "Collect user feedback",
                        "Scale to 50% if successful",
                    ],
                },
                {
                    "phase": "Full Deployment",
                    "duration": "1 week",
                    "tasks": [
                        "Replace target model completely",
                        "Update model allocation configurations",
                        "Monitor for 48 hours",
                        "Document lessons learned",
                    ],
                },
            ],
            "rollback_plan": "Automatic rollback if performance drops >5% or costs increase >20%",
            "success_metrics": [
                f"Performance improvement ≥ {replacement_result['analysis']['score_breakdown']['performance']:.1f}/10",
                f"Cost efficiency ≥ {replacement_result['analysis']['score_breakdown']['cost_efficiency']:.1f}/10",
                "No service disruptions during transition",
                "User satisfaction maintained or improved",
            ],
        }

    def _classify_price_tier(self, input_cost: float) -> str:
        """Classify model into price tier based on input cost"""
        if input_cost == 0:
            return "free"
        elif input_cost <= 2.0:
            return "value"
        else:
            return "premium"

    def _classify_capabilities(self, model: ModelMetrics) -> list[str]:
        """Classify model capabilities based on performance and features"""
        capabilities = []

        if model.humaneval_score >= 75:
            capabilities.append("coding_specialists")
        if model.gsm8k_score and model.gsm8k_score >= 80:
            capabilities.append("reasoning_experts")
        if model.has_multimodal or model.has_vision:
            capabilities.append("multimodal")
        if model.mmlu_score >= 75 and model.hellaswag_score >= 80:
            capabilities.append("general_purpose")

        # Conversation capability inference
        if "chat" in model.name.lower() or "instruct" in model.name.lower():
            capabilities.append("conversation")

        return capabilities if capabilities else ["general_purpose"]

    def _adjacent_tiers(self, tier1: str, tier2: str) -> bool:
        """Check if two price tiers are adjacent (allowing cross-tier replacement)"""
        tier_order = ["free", "value", "premium"]
        try:
            idx1, idx2 = tier_order.index(tier1), tier_order.index(tier2)
            return abs(idx1 - idx2) <= 1
        except ValueError:
            return False

    def _is_protected_model(self, model: ModelMetrics) -> bool:
        """Check if model is protected (top 2 from Tier 1 providers)"""
        tier_1_providers = ["openai", "anthropic", "google"]
        return model.provider in tier_1_providers

    def _is_same_generation_upgrade(self, new_model: ModelMetrics, existing_model: ModelMetrics) -> bool:
        """Detect same-generation upgrades (e.g., Opus 4 -> Opus 4.1)"""
        new_name = new_model.name.lower()
        existing_name = existing_model.name.lower()

        # Pattern matching for version upgrades
        version_patterns = [
            # Anthropic patterns: opus-4 -> opus-4.1, sonnet-3.5 -> sonnet-3.6
            (r"opus-(\d+)\.(\d+)", r"opus-(\d+)$"),
            (r"sonnet-(\d+)\.(\d+)", r"sonnet-(\d+)$"),
            # OpenAI patterns: gpt-4-turbo -> gpt-4, gpt-4.1 -> gpt-4
            (r"gpt-(\d+)-turbo", r"gpt-(\d+)$"),
            (r"gpt-(\d+)\.(\d+)", r"gpt-(\d+)$"),
            # Google patterns: gemini-2.5-pro -> gemini-2-pro
            (r"gemini-(\d+)\.(\d+)", r"gemini-(\d+)"),
        ]

        import re

        for new_pattern, existing_pattern in version_patterns:
            if re.search(new_pattern, new_name) and re.search(existing_pattern, existing_name):
                return True

        return False

    def _is_cross_generation_replacement(self, new_model: ModelMetrics, existing_model: ModelMetrics) -> bool:
        """Detect cross-generation replacements (e.g., GPT-5 replacing GPT-4 series)"""
        new_name = new_model.name.lower()
        existing_name = existing_model.name.lower()

        # Cross-generation patterns
        cross_gen_patterns = [
            # GPT-5 can replace GPT-4 series
            (r"gpt-5", r"gpt-4"),
            (r"gpt-(\d+)", r"gpt-(\d+)"),  # Any GPT version jump
            # Claude Opus 4 can replace Opus 3 series
            (r"opus-4", r"opus-3"),
            # Gemini 3.x can replace 2.x series
            (r"gemini-3", r"gemini-2"),
        ]

        import re

        for new_pattern, existing_pattern in cross_gen_patterns:
            new_match = re.search(new_pattern, new_name)
            existing_match = re.search(existing_pattern, existing_name)

            if new_match and existing_match:
                # Extract version numbers if available
                try:
                    new_ver = int(new_match.group(1)) if new_match.groups() else 5
                    existing_ver = int(existing_match.group(1)) if existing_match.groups() else 4
                    return new_ver > existing_ver
                except (ValueError, IndexError):
                    return True  # Assume cross-generation if pattern matches

        return False

    def _meets_protection_exception(self, model: ModelMetrics) -> bool:
        """Check if protected model meets exception criteria for replacement"""
        # Check for end-of-life announcements (would need external data source)
        # Check for extended unavailability
        # Check for significant cost increases

        # For now, basic availability check
        return model.api_availability < 85

    def _calculate_same_generation_score(
        self, new_model: ModelMetrics, existing_model: ModelMetrics
    ) -> dict[str, float]:
        """
        Special scoring for same-generation upgrades (e.g., Opus 4 -> Opus 4.1)
        Rule: Replace if no cost increase, regardless of performance improvement size
        """
        # Check cost increase
        cost_increase = 0
        if existing_model.output_cost > 0:
            cost_increase = ((new_model.output_cost - existing_model.output_cost) / existing_model.output_cost) * 100

        # Check any performance improvement
        has_any_improvement = False
        for benchmark in ["humaneval_score", "mmlu_score", "hellaswag_score"]:
            new_score = getattr(new_model, benchmark)
            existing_score = getattr(existing_model, benchmark)
            if new_score > existing_score:
                has_any_improvement = True
                break

        # Same-generation upgrade scoring
        if cost_increase <= 0 and has_any_improvement:
            # Automatic approval for no cost increase + any improvement
            return {
                "performance": 8.0,  # High score for any measurable improvement
                "cost_efficiency": 9.0,  # High score for no cost increase
                "strategic_value": 8.0,  # High score for staying current
                "operational_benefit": 7.0,  # Good score for version currency
            }
        elif cost_increase <= 0:
            # Approval even without measurable performance gain (version currency)
            return {
                "performance": 7.0,  # Good score for version currency
                "cost_efficiency": 9.0,  # High score for no cost increase
                "strategic_value": 8.0,  # High score for staying current
                "operational_benefit": 7.0,  # Good score for version currency
            }
        else:
            # Cost increase detected - apply standard scoring with penalty
            return {
                "performance": 3.0,  # Low score due to cost increase
                "cost_efficiency": 2.0,  # Very low due to cost penalty
                "strategic_value": 4.0,  # Reduced strategic value
                "operational_benefit": 3.0,  # Reduced operational benefit
            }

    def _fetch_benchmark_scores(self, model_name: str) -> dict[str, float]:
        """Fetch benchmark scores from multiple sources"""
        # Implementation would fetch from various benchmark leaderboards
        # For now, return placeholder structure
        return {"humaneval": 0, "swe_bench": 0, "mmlu": 0, "hellaswag": 0, "gsm8k": 0, "math": 0}

    def _detect_multimodal_capability(self, model_data: dict) -> bool:
        """Detect if model has multimodal capabilities"""
        description = model_data.get("description", "").lower()
        return any(keyword in description for keyword in ["multimodal", "vision", "image", "visual"])

    def _detect_vision_capability(self, model_data: dict) -> bool:
        """Detect if model has vision processing capabilities"""
        description = model_data.get("description", "").lower()
        return any(keyword in description for keyword in ["vision", "image", "visual", "sight", "ocr"])

    def _parse_model_name_from_url(self, url: str) -> str:
        """Extract model name from OpenRouter URL"""
        # Example: https://openrouter.ai/openai/gpt-4 -> openai/gpt-4
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            return "/".join(parts[-2:])
        return parts[-1] if parts else ""

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        # Implementation would load the YAML configuration
        return {}


# Example usage:
"""
evaluator = ModelEvaluator()
result = evaluator.evaluate_model_for_replacement("https://openrouter.ai/openai/gpt-5")

if result.get("replacement_recommended"):
    print(f"RECOMMENDATION: Replace {result['target_model'].name}")
    print(f"Replacement Score: {result['replacement_score']:.1f}/10")
    print(f"Reasoning: {result['detailed_analysis']['reasoning']}")
    print(f"Implementation Timeline: {result['implementation_plan']['timeline']}")
else:
    print("No replacement recommended")
"""
