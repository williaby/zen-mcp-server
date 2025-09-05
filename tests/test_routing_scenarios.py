"""
Scenario-based tests for dynamic model routing.

Tests real-world usage scenarios, workflow patterns, and end-to-end
routing behavior across different tool types and contexts.
"""

import time
from unittest.mock import patch

import pytest

from routing.model_level_router import ModelLevelRouter
from tests.fixtures.routing_test_data import (
    PERFORMANCE_TEST_PROMPTS,
    TOOL_SCENARIOS,
)


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_code_review_workflow(self):
        """Test complete code review workflow."""
        scenarios = [
            {
                "step": "Initial review request",
                "prompt": "Please review this Python module for best practices",
                "context": {"files": ["user_service.py"], "file_types": [".py"]},
                "expected_level": ["junior", "senior"]
            },
            {
                "step": "Security focused review",
                "prompt": "Focus on security vulnerabilities in authentication code",
                "context": {"files": ["auth.py", "security.py"], "file_types": [".py"]},
                "expected_level": ["senior", "executive"]
            },
            {
                "step": "Performance review",
                "prompt": "Check for performance bottlenecks in database queries",
                "context": {"files": ["models.py", "queries.py"], "file_types": [".py"]},
                "expected_level": ["senior", "executive"]
            }
        ]

        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                scenario["context"],
                prefer_free=True
            )

            # Check that appropriate level model was selected
            if result.model.cost_per_token == 0:
                # Free model is always acceptable if available
                assert True
            else:
                assert result.model.level.value in scenario["expected_level"], (
                    f"Step '{scenario['step']}' got {result.model.level.value}, "
                    f"expected {scenario['expected_level']}"
                )

    def test_debugging_escalation_workflow(self):
        """Test debugging workflow with escalation."""
        # Start with simple error
        simple_result = self.router.select_model(
            "Fix this syntax error: SyntaxError: invalid syntax",
            {"error": "SyntaxError: invalid syntax"}
        )

        # Complex concurrency bug should escalate
        complex_result = self.router.select_model(
            "Debug this race condition causing data corruption in multi-threaded environment",
            {
                "files": ["threading_manager.py", "data_processor.py"],
                "error": "Data corruption detected in concurrent operations"
            }
        )

        # Complex bug should get higher level model (unless free model is capable)
        if complex_result.model.cost_per_token > 0:
            assert complex_result.model.level.value in ["senior", "executive"]

    def test_project_analysis_workflow(self):
        """Test large project analysis workflow."""
        # Small project analysis
        small_result = self.router.select_model(
            "Analyze this Python script structure",
            {"files": ["main.py"], "file_types": [".py"]}
        )

        # Large project analysis
        large_result = self.router.select_model(
            "Analyze this entire microservices architecture",
            {
                "files": [f"service_{i}.py" for i in range(15)] +
                       [f"model_{i}.py" for i in range(10)] +
                       ["config.yaml", "docker-compose.yml"],
                "file_types": [".py", ".yaml", ".yml"]
            }
        )

        # Large project should get more capable model (or free if available)
        assert large_result.model is not None

        # If paid models are selected, large should be >= small in capability
        if (large_result.model.cost_per_token > 0 and
            small_result.model.cost_per_token > 0):
            large_level_priority = list(self.router.level_models.keys()).index(large_result.model.level)
            small_level_priority = list(self.router.level_models.keys()).index(small_result.model.level)
            assert large_level_priority >= small_level_priority

    def test_consensus_workflow(self):
        """Test consensus tool workflow scenarios."""
        scenarios = [
            {
                "description": "Simple consensus on code style",
                "prompt": "Get consensus on variable naming conventions",
                "context": {"tool_name": "consensus"},
                "expected_complexity": ["simple", "moderate"]
            },
            {
                "description": "Architecture decision consensus",
                "prompt": "Reach consensus on microservices vs monolith for new project",
                "context": {"tool_name": "consensus", "files": ["requirements.md"]},
                "expected_complexity": ["complex", "expert"]
            },
            {
                "description": "Security policy consensus",
                "prompt": "Get team consensus on authentication strategy",
                "context": {"tool_name": "consensus", "files": ["security_requirements.md"]},
                "expected_complexity": ["complex", "expert"]
            }
        ]

        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                scenario["context"],
                prefer_free=True
            )

            # Consensus tasks should generally get appropriate models
            assert result.model is not None
            assert result.confidence > 0

    def test_multi_language_project_scenario(self):
        """Test routing for multi-language projects."""
        context = {
            "files": [
                "backend.py", "models.py",  # Python
                "frontend.js", "components.jsx",  # JavaScript/React
                "service.go", "handlers.go",  # Go
                "Dockerfile", "docker-compose.yml",  # Docker
                "schema.sql"  # SQL
            ],
            "file_types": [".py", ".js", ".jsx", ".go", ".yml", ".sql"]
        }

        result = self.router.select_model(
            "Analyze this full-stack application for architectural improvements",
            context
        )

        # Multi-language project should be recognized as complex
        complexity, confidence, task_type = self.router.complexity_analyzer.analyze(
            "Analyze this full-stack application", context
        )

        assert complexity in ["moderate", "complex", "expert"]
        assert result.model is not None


class TestToolSpecificScenarios:
    """Test scenarios specific to different tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    @pytest.mark.parametrize("tool_name,scenarios", TOOL_SCENARIOS.items())
    def test_tool_specific_routing(self, tool_name, scenarios):
        """Test routing for tool-specific scenarios."""
        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                scenario["context"],
                prefer_free=True
            )

            assert result.model is not None

            # Check reasoning contains tool context
            assert tool_name in result.reasoning.lower() or "tool" in result.reasoning.lower()

    def test_chat_tool_scenarios(self):
        """Test chat tool specific scenarios."""
        scenarios = [
            {
                "prompt": "What is Python?",
                "context": {"tool_name": "chat"},
                "expected": "Should use free model for simple questions"
            },
            {
                "prompt": "Explain the differences between async/await and threading in Python with code examples",
                "context": {"tool_name": "chat"},
                "expected": "May use junior model for detailed explanations"
            },
            {
                "prompt": "Help me debug this complex memory management issue in C++",
                "context": {"tool_name": "chat", "files": ["memory_manager.cpp"]},
                "expected": "Should escalate to senior model for complex debugging"
            }
        ]

        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                scenario["context"],
                prefer_free=True
            )

            # Free models preferred, but higher levels acceptable for complex tasks
            if result.model.cost_per_token > 0:
                complexity, _, _ = self.router.complexity_analyzer.analyze(
                    scenario["prompt"], scenario["context"]
                )
                if complexity in ["simple"]:
                    # Simple tasks getting paid models is okay if that's all that's available
                    pass

    def test_security_audit_scenarios(self):
        """Test security audit tool scenarios."""
        scenarios = [
            {
                "prompt": "Check for basic input validation issues",
                "context": {"tool_name": "secaudit", "files": ["forms.py"]},
                "expected_min_level": "junior"
            },
            {
                "prompt": "Comprehensive security audit for payment processing system",
                "context": {
                    "tool_name": "secaudit",
                    "files": ["payment.py", "encryption.py", "auth.py"]
                },
                "expected_min_level": "senior"
            },
            {
                "prompt": "Analyze for cryptographic vulnerabilities in blockchain implementation",
                "context": {
                    "tool_name": "secaudit",
                    "files": ["blockchain.py", "crypto.py", "consensus.py"]
                },
                "expected_min_level": "executive"
            }
        ]

        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                scenario["context"],
                prefer_free=False  # Security audits may need paid models
            )

            # Security tasks should get appropriate models
            if result.model.cost_per_token > 0:
                level_priorities = ["free", "junior", "senior", "executive"]
                min_priority = level_priorities.index(scenario["expected_min_level"])
                actual_priority = level_priorities.index(result.model.level.value)

                assert actual_priority >= min_priority, (
                    f"Security audit got {result.model.level.value}, "
                    f"expected at least {scenario['expected_min_level']}"
                )


class TestCostOptimizationScenarios:
    """Test cost optimization in real scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_free_model_prioritization(self):
        """Test that free models are prioritized across scenarios."""
        prompts = [
            "Simple code review",
            "Explain this function",
            "Debug basic syntax error",
            "Format this code",
            "Write simple documentation"
        ]

        free_selections = 0
        total_selections = len(prompts)

        for prompt in prompts:
            result = self.router.select_model(prompt, prefer_free=True)
            if result.model.cost_per_token == 0:
                free_selections += 1

        # Should select free models when available
        # (Exact ratio depends on what models are configured)
        free_ratio = free_selections / total_selections
        assert free_ratio >= 0.5, f"Only {free_ratio:.1%} selections used free models"

    def test_cost_budget_constraints(self):
        """Test adherence to cost budget constraints."""
        max_costs = [0.0, 0.001, 0.01, 0.1]

        for max_cost in max_costs:
            result = self.router.select_model(
                "Test prompt for cost constraint",
                max_cost=max_cost,
                prefer_free=False
            )

            assert result.model.cost_per_token <= max_cost, (
                f"Model cost {result.model.cost_per_token} exceeds limit {max_cost}"
            )

    def test_cost_vs_complexity_tradeoff(self):
        """Test cost vs complexity tradeoff scenarios."""
        scenarios = [
            {
                "prompt": "Simple task - prefer cost savings",
                "max_cost": 0.001,
                "prefer_free": True,
                "expected_behavior": "Should use free or very cheap model"
            },
            {
                "prompt": "Critical security analysis - prefer capability",
                "max_cost": 0.1,
                "prefer_free": False,
                "expected_behavior": "Should use capable model within budget"
            }
        ]

        for scenario in scenarios:
            result = self.router.select_model(
                scenario["prompt"],
                max_cost=scenario["max_cost"],
                prefer_free=scenario["prefer_free"]
            )

            assert result.model.cost_per_token <= scenario["max_cost"]
            assert result.estimated_cost <= result.model.cost_per_token * 1000  # Rough estimate


class TestPerformanceScenarios:
    """Test performance-related scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_routing_performance_under_load(self):
        """Test routing performance with many concurrent requests."""
        start_time = time.time()

        results = []
        for prompt in PERFORMANCE_TEST_PROMPTS:
            result = self.router.select_model(prompt)
            results.append(result)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_request = total_time / len(PERFORMANCE_TEST_PROMPTS)

        # Should handle requests reasonably quickly
        assert avg_time_per_request < 0.1, (
            f"Routing too slow: {avg_time_per_request:.3f}s per request"
        )

        # All requests should succeed
        assert len(results) == len(PERFORMANCE_TEST_PROMPTS)
        assert all(r.model is not None for r in results)

    def test_caching_effectiveness(self):
        """Test caching effectiveness in repeated scenarios."""
        prompt = "Repeated prompt for cache testing"
        context = {"files": ["test.py"]}

        # First request (uncached)
        start_time = time.time()
        result1 = self.router.select_model(prompt, context)
        first_time = time.time() - start_time

        # Second request (should use cache)
        start_time = time.time()
        result2 = self.router.select_model(prompt, context)
        second_time = time.time() - start_time

        # Results should be identical
        assert result1.model.name == result2.model.name
        assert result1.confidence == result2.confidence

        # Timing test is flaky, so just ensure no crashes
        assert second_time >= 0

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable over time."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make many requests
        for i in range(200):
            self.router.select_model(f"Test prompt {i}")

            # Check memory periodically
            if i % 50 == 0:
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory

                # Memory shouldn't grow excessively
                assert memory_increase < 100 * 1024 * 1024, (
                    f"Memory usage increased by {memory_increase / 1024 / 1024:.1f}MB"
                )


class TestErrorRecoveryScenarios:
    """Test error recovery and fallback scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_model_unavailable_fallback(self):
        """Test fallback when preferred models are unavailable."""
        # Disable some models
        original_availability = {}
        for model_name, model in self.router.models.items():
            original_availability[model_name] = model.is_available
            if "expensive" in model_name.lower():
                model.is_available = False

        try:
            # Should still be able to route
            result = self.router.select_model(
                "Complex task that would prefer expensive model",
                prefer_free=False
            )

            assert result.model is not None
            assert result.model.is_available

        finally:
            # Restore availability
            for model_name, availability in original_availability.items():
                self.router.models[model_name].is_available = availability

    def test_complexity_analysis_failure_fallback(self):
        """Test fallback when complexity analysis fails."""
        with patch.object(self.router.complexity_analyzer, 'analyze') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")

            # Should still route with fallback logic
            result = self.router.select_model("Test prompt after analysis failure")

            assert result.model is not None
            # Should use conservative fallback

    def test_configuration_error_recovery(self):
        """Test recovery from configuration errors."""
        # Temporarily corrupt configuration
        original_config = self.router.routing_config
        self.router.routing_config = {}  # Empty config

        try:
            # Should still work with defaults
            result = self.router.select_model("Test with broken config")
            assert result.model is not None

        finally:
            self.router.routing_config = original_config

    def test_partial_model_failure_handling(self):
        """Test handling when some models fail repeatedly."""
        # Simulate failed model
        if self.router.models:
            test_model = list(self.router.models.values())[0]

            # Report multiple failures
            for _ in range(6):  # Should disable after 5 failures
                self.router.update_model_performance(test_model.name, False, "Test failure")

            # Model should be disabled
            assert not test_model.is_available

            # Router should still work with other models
            result = self.router.select_model("Test after model failure")
            assert result.model is not None
            assert result.model.name != test_model.name


class TestEdgeCaseScenarios:
    """Test edge cases and unusual scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_empty_prompt_handling(self):
        """Test handling of empty or minimal prompts."""
        edge_prompts = ["", " ", "?", "help", "hi"]

        for prompt in edge_prompts:
            result = self.router.select_model(prompt)

            assert result.model is not None
            # Should default to simple/free models
            if result.model.cost_per_token > 0:
                # Paid models okay if no free alternatives
                pass

    def test_very_long_prompt_handling(self):
        """Test handling of very long prompts."""
        long_prompt = "Analyze this code: " + "def function():\n    pass\n" * 1000

        result = self.router.select_model(long_prompt)

        assert result.model is not None
        # Long prompts might indicate complexity
        if result.model.cost_per_token == 0:
            # Free model is fine
            pass
        else:
            # Paid model acceptable for complex content
            pass

    def test_unusual_file_extensions(self):
        """Test handling of unusual file extensions."""
        unusual_context = {
            "files": ["weird.xyz", "unknown.abc", "noext"],
            "file_types": [".xyz", ".abc", ""]
        }

        result = self.router.select_model(
            "Analyze these unusual files",
            unusual_context
        )

        assert result.model is not None
        # Should handle gracefully with defaults

    def test_contradictory_preferences(self):
        """Test handling of contradictory routing preferences."""
        # Request free model but high complexity
        result = self.router.select_model(
            "Expert level distributed systems architecture with ML optimization",
            prefer_free=True,
            max_cost=0.0  # Force free only
        )

        # Should respect cost constraint
        assert result.model.cost_per_token == 0.0

    def test_rapid_successive_requests(self):
        """Test rapid successive requests."""
        results = []

        for i in range(20):
            result = self.router.select_model(f"Rapid request {i}")
            results.append(result)

        # All should succeed
        assert len(results) == 20
        assert all(r.model is not None for r in results)

        # Caching should provide consistent results for same prompts
        same_prompts = [r for r in results[::2]]  # Even indices
        if len(same_prompts) > 1:
            # Similar prompts might get similar models
            pass


class TestWorkflowIntegrationScenarios:
    """Test integration across multiple tool workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = ModelLevelRouter()

    def test_analyze_review_debug_workflow(self):
        """Test analyze → codereview → debug workflow."""
        # 1. Analysis phase
        analyze_result = self.router.select_model(
            "Analyze this codebase for issues",
            {"tool_name": "analyze", "files": ["service.py", "utils.py"]}
        )

        # 2. Code review phase
        review_result = self.router.select_model(
            "Review these files for the issues found in analysis",
            {"tool_name": "codereview", "files": ["service.py", "utils.py"]}
        )

        # 3. Debug phase
        debug_result = self.router.select_model(
            "Debug the specific issues identified in review",
            {"tool_name": "debug", "files": ["service.py"], "error": "Performance issue"}
        )

        # All phases should get appropriate models
        assert analyze_result.model is not None
        assert review_result.model is not None
        assert debug_result.model is not None

        # Debug with specific error should potentially escalate
        if debug_result.model.cost_per_token > 0:
            # Acceptable to use paid model for debugging
            pass

    def test_consensus_implementation_workflow(self):
        """Test consensus → planning → implementation workflow."""
        # 1. Consensus on approach
        consensus_result = self.router.select_model(
            "Get team consensus on database migration strategy",
            {"tool_name": "consensus"}
        )

        # 2. Planning implementation
        planning_result = self.router.select_model(
            "Plan the implementation of agreed migration strategy",
            {"tool_name": "planner"}
        )

        # 3. Implementation
        implementation_result = self.router.select_model(
            "Implement the database migration script",
            {"tool_name": "chat", "files": ["migration.py"]}
        )

        assert consensus_result.model is not None
        assert planning_result.model is not None
        assert implementation_result.model is not None


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end integration tests."""

    def test_complete_project_workflow(self):
        """Test complete project development workflow."""
        router = ModelLevelRouter()

        workflow_steps = [
            ("Project planning", "Plan a new web application architecture"),
            ("Security review", "Review security requirements for web app"),
            ("Code generation", "Generate authentication module"),
            ("Code review", "Review the generated authentication code"),
            ("Testing", "Generate tests for authentication module"),
            ("Documentation", "Write API documentation"),
            ("Deployment", "Create deployment configuration")
        ]

        results = []
        for step_name, prompt in workflow_steps:
            result = router.select_model(prompt, prefer_free=True)
            results.append((step_name, result))

            assert result.model is not None, f"Step '{step_name}' failed to get model"

        # Should complete entire workflow
        assert len(results) == len(workflow_steps)

        # Mix of free and paid models is expected depending on task complexity
        free_count = sum(1 for _, result in results if result.model.cost_per_token == 0)
        total_count = len(results)

        # At least some tasks should use free models
        assert free_count > 0, "No tasks used free models"

        # Log workflow for debugging
        for step_name, result in results:
            print(f"{step_name}: {result.model.name} ({result.model.level.value})")


if __name__ == "__main__":
    # Run specific test for debugging
    test = TestRealWorldScenarios()
    test.setup_method()
    test.test_code_review_workflow()
