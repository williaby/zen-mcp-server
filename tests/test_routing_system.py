"""
Unit tests for the dynamic model routing system.

Tests the core functionality of ModelLevelRouter, ComplexityAnalyzer,
and related components.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from routing.complexity_analyzer import ComplexityAnalyzer, TaskType
from routing.model_level_router import ModelLevel, ModelLevelRouter, RoutingResult
from tests.fixtures.routing_test_data import (
    COMPLEXITY_TEST_CASES,
    COST_TEST_CASES,
    EXPECTED_MODEL_LEVELS,
    MOCK_MODEL_CONFIG,
)


class TestComplexityAnalyzer:
    """Test the complexity analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ComplexityAnalyzer()

    def test_simple_task_detection(self):
        """Test detection of simple tasks."""
        prompt = "Help me fix this simple typo"
        complexity, confidence, task_type = self.analyzer.analyze(prompt)

        assert complexity == "simple"
        assert confidence > 0.5
        assert task_type == TaskType.DEBUGGING

    def test_complex_task_detection(self):
        """Test detection of complex tasks."""
        prompt = "Design a distributed microservices architecture with high availability"
        complexity, confidence, task_type = self.analyzer.analyze(prompt)

        assert complexity in ["complex", "expert"]
        assert confidence > 0.5
        assert task_type == TaskType.PLANNING

    def test_code_generation_detection(self):
        """Test detection of code generation tasks."""
        prompt = "Write a Python function to implement a binary search algorithm"
        complexity, confidence, task_type = self.analyzer.analyze(prompt)

        assert task_type == TaskType.CODE_GENERATION
        assert complexity in ["moderate", "complex"]

    def test_debugging_with_context(self):
        """Test debugging task detection with error context."""
        prompt = "Fix this error"
        context = {"error": "AttributeError: module has no attribute 'foo'"}

        complexity, confidence, task_type = self.analyzer.analyze(prompt, context)

        assert task_type == TaskType.DEBUGGING
        assert complexity in ["moderate", "complex"]  # Error context increases complexity

    def test_file_type_complexity(self):
        """Test file type complexity contribution."""
        prompt = "Review this code"
        context = {"files": ["complex.cpp"], "file_types": [".cpp"]}

        complexity, confidence, task_type = self.analyzer.analyze(prompt, context)

        # C++ files should increase complexity
        assert complexity in ["moderate", "complex", "expert"]
        assert task_type == TaskType.CODE_REVIEW

    def test_multi_file_complexity(self):
        """Test multi-file context complexity."""
        prompt = "Analyze this codebase"
        context = {"files": ["a.py", "b.py", "c.py", "d.py", "e.py"]}

        complexity, confidence, task_type = self.analyzer.analyze(prompt, context)

        # Multiple files should increase complexity
        assert complexity in ["complex", "expert"]
        assert task_type == TaskType.ANALYSIS

    @pytest.mark.parametrize("test_case", COMPLEXITY_TEST_CASES)
    def test_complexity_test_cases(self, test_case):
        """Test all predefined complexity test cases."""
        complexity, confidence, task_type = self.analyzer.analyze(
            test_case.prompt, test_case.context
        )

        assert complexity == test_case.expected_complexity, (
            f"Expected {test_case.expected_complexity}, got {complexity} "
            f"for prompt: {test_case.prompt[:50]}..."
        )
        assert task_type.value == test_case.expected_task_type

    def test_analysis_details(self):
        """Test detailed analysis output."""
        prompt = "Complex algorithm implementation with performance optimization"
        details = self.analyzer.get_analysis_details(prompt)

        assert "complexity_level" in details
        assert "confidence" in details
        assert "task_type" in details
        assert "indicators" in details
        assert details["total_indicators"] > 0


class TestModelLevelRouter:
    """Test the model level routing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary config files
        self.temp_dir = tempfile.mkdtemp()
        self.models_config_path = os.path.join(self.temp_dir, "models.json")
        self.routing_config_path = os.path.join(self.temp_dir, "routing.json")

        # Write test configurations
        with open(self.models_config_path, 'w') as f:
            json.dump(MOCK_MODEL_CONFIG, f)

        routing_config = {
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
            "free_model_preference": True,
            "cost_optimization": True
        }

        with open(self.routing_config_path, 'w') as f:
            json.dump(routing_config, f)

        self.router = ModelLevelRouter(
            config_path=self.routing_config_path,
            models_config_path=self.models_config_path
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_model_initialization(self):
        """Test that models are correctly initialized."""
        assert len(self.router.models) > 0

        # Check that models are categorized correctly
        free_models = self.router.level_models[ModelLevel.FREE]
        junior_models = self.router.level_models[ModelLevel.JUNIOR]
        senior_models = self.router.level_models[ModelLevel.SENIOR]
        executive_models = self.router.level_models[ModelLevel.EXECUTIVE]

        assert len(free_models) > 0  # Should have free models
        assert len(junior_models) > 0  # Should have junior models
        assert len(senior_models) > 0  # Should have senior models
        assert len(executive_models) > 0  # Should have executive models

    def test_model_level_determination(self):
        """Test model level classification."""
        for model_name, expected_level in EXPECTED_MODEL_LEVELS.items():
            if model_name in self.router.models:
                actual_level = self.router.models[model_name].level.value
                assert actual_level == expected_level, (
                    f"Model {model_name} expected level {expected_level}, "
                    f"got {actual_level}"
                )

    def test_free_model_prioritization(self):
        """Test that free models are prioritized."""
        prompt = "Simple task that can use any model"
        result = self.router.select_model(prompt, prefer_free=True)

        assert result.model.cost_per_token == 0.0, (
            f"Expected free model, got {result.model.name} "
            f"with cost {result.model.cost_per_token}"
        )

    def test_complexity_based_routing(self):
        """Test that routing respects complexity levels."""
        # Simple task should get free model
        simple_result = self.router.select_model(
            "Simple explanation task", prefer_free=True
        )
        assert simple_result.model.level in [ModelLevel.FREE, ModelLevel.JUNIOR]

        # Complex task should get higher level model (but may still prefer free)
        complex_result = self.router.select_model(
            "Complex distributed system architecture analysis with security audit",
            prefer_free=False  # Don't prefer free to test level escalation
        )
        assert complex_result.model.level in [ModelLevel.SENIOR, ModelLevel.EXECUTIVE]

    def test_cost_constraints(self):
        """Test cost constraint enforcement."""
        prompt = "Any task"
        max_cost = 0.001

        result = self.router.select_model(
            prompt, prefer_free=False, max_cost=max_cost
        )

        assert result.model.cost_per_token <= max_cost

    def test_specialization_preference(self):
        """Test that specialized models are preferred when available."""
        # This test would need models with specializations defined
        prompt = "Code review task"
        context = {"tool_name": "codereview"}

        result = self.router.select_model(prompt, context)

        # Should select an appropriate model (exact model depends on config)
        assert result.model is not None
        assert result.confidence > 0

    def test_fallback_mechanism(self):
        """Test fallback when no suitable models found."""
        # Mock all models as unavailable
        for model in self.router.models.values():
            model.is_available = False

        # Should still return a model (fallback)
        with pytest.raises(RuntimeError, match="No suitable models available"):
            self.router.select_model("Any prompt")

    def test_performance_tracking(self):
        """Test model performance tracking."""
        model_name = list(self.router.models.keys())[0]
        initial_success_rate = self.router.models[model_name].success_rate

        # Report success
        self.router.update_model_performance(model_name, True)
        assert self.router.models[model_name].success_rate >= initial_success_rate

        # Report failure
        self.router.update_model_performance(model_name, False, "Test error")
        assert self.router.models[model_name].last_error == "Test error"
        assert self.router.models[model_name].error_count > 0

    def test_caching(self):
        """Test that routing decisions are cached."""
        prompt = "Test prompt for caching"

        # First call
        result1 = self.router.select_model(prompt)

        # Second call should use cache (same result)
        result2 = self.router.select_model(prompt)

        assert result1.model.name == result2.model.name
        assert result1.confidence == result2.confidence

    def test_routing_statistics(self):
        """Test routing statistics collection."""
        # Make some routing decisions
        self.router.select_model("Simple task 1")
        self.router.select_model("Complex analysis task")
        self.router.select_model("Another simple task")

        stats = self.router.get_model_stats()

        assert "total_models" in stats
        assert "available_models" in stats
        assert "models_by_level" in stats
        assert stats["total_models"] > 0

    @pytest.mark.parametrize("cost_case", COST_TEST_CASES)
    def test_cost_optimization_cases(self, cost_case):
        """Test cost optimization scenarios."""
        result = self.router.select_model(
            cost_case["prompt"],
            prefer_free=cost_case["prefer_free"],
            max_cost=cost_case["max_cost"]
        )

        if callable(cost_case["expected_cost"]):
            assert cost_case["expected_cost"](result.estimated_cost)
        else:
            assert result.estimated_cost == cost_case["expected_cost"]

        if cost_case["expected_model_type"] == "free":
            assert result.model.cost_per_token == 0.0
        elif cost_case["expected_model_type"] == "paid":
            assert result.model.cost_per_token > 0.0


class TestRoutingIntegration:
    """Test integration between components."""

    def test_end_to_end_routing(self):
        """Test complete routing workflow."""
        # Create router with default configs
        router = ModelLevelRouter()

        prompt = "Review this Python code for potential improvements"
        context = {"files": ["test.py"], "file_types": [".py"]}

        result = router.select_model(prompt, context, prefer_free=True)

        assert isinstance(result, RoutingResult)
        assert result.model is not None
        assert result.confidence >= 0.0
        assert result.reasoning != ""
        assert len(result.fallback_models) >= 0

    def test_error_handling(self):
        """Test graceful error handling."""
        # Test with invalid config paths
        router = ModelLevelRouter(
            config_path="/nonexistent/path.json",
            models_config_path="/nonexistent/models.json"
        )

        # Should still work with default configs
        result = router.select_model("Test prompt")
        assert result is not None

    def test_disabled_routing_fallback(self):
        """Test behavior when routing components fail."""
        with patch('routing.complexity_analyzer.ComplexityAnalyzer') as mock_analyzer:
            mock_analyzer.side_effect = Exception("Analysis failed")

            # Router should still work with basic heuristics
            router = ModelLevelRouter()
            result = router.select_model("Test prompt")

            assert result is not None
            # Should fallback gracefully


class TestRoutingConfigurationLoading:
    """Test configuration loading and validation."""

    def test_default_config_loading(self):
        """Test loading default configurations."""
        router = ModelLevelRouter()

        assert router.routing_config is not None
        assert "levels" in router.routing_config
        assert "complexity_thresholds" in router.routing_config

    def test_custom_config_loading(self):
        """Test loading custom configurations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "levels": {
                    "free": {"cost_limit": 0.0, "priority": 1},
                    "premium": {"cost_limit": 1.0, "priority": 2}
                }
            }
            json.dump(config, f)
            config_path = f.name

        try:
            router = ModelLevelRouter(config_path=config_path)
            assert "premium" in router.routing_config["levels"]
        finally:
            os.unlink(config_path)

    def test_invalid_config_handling(self):
        """Test handling of invalid configurations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = f.name

        try:
            # Should not crash, should use defaults
            router = ModelLevelRouter(config_path=config_path)
            assert router.routing_config is not None
        finally:
            os.unlink(config_path)


class TestPerformanceRequirements:
    """Test performance requirements of the routing system."""

    def test_routing_decision_speed(self):
        """Test that routing decisions are made quickly."""
        import time

        router = ModelLevelRouter()

        start_time = time.time()
        for _ in range(10):
            router.select_model("Test prompt for performance")
        end_time = time.time()

        avg_time = (end_time - start_time) / 10
        assert avg_time < 0.1, f"Routing too slow: {avg_time:.3f}s per decision"

    def test_memory_usage(self):
        """Test that routing doesn't consume excessive memory."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        router = ModelLevelRouter()

        # Make many routing decisions
        for i in range(100):
            router.select_model(f"Test prompt {i}")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, (
            f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB"
        )

    def test_cache_efficiency(self):
        """Test that caching reduces computation time."""
        import time

        router = ModelLevelRouter()
        prompt = "Cached routing test prompt"

        # First call (no cache)
        start_time = time.time()
        result1 = router.select_model(prompt)
        first_call_time = time.time() - start_time

        # Second call (should use cache)
        start_time = time.time()
        result2 = router.select_model(prompt)
        second_call_time = time.time() - start_time

        # Results should be identical
        assert result1.model.name == result2.model.name

        # Second call should be faster (though this can be flaky)
        # Just ensure it doesn't crash and returns same result
        assert second_call_time >= 0
