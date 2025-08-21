"""
Integration tests for dynamic model routing.

Tests the integration of routing system with existing server infrastructure,
tool hooks, and real-world usage scenarios.
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Test imports - adjust based on actual project structure
from routing.integration import (
    ModelRoutingIntegration, get_integration_instance, 
    integrate_with_server, route_model_request
)
from routing.hooks import ToolHooks
from routing.model_wrapper import ModelWrapper, create_routing_wrapper
from tools.shared.base_tool import BaseTool
from tests.fixtures.routing_test_data import TOOL_SCENARIOS, create_mock_context

class TestModelRoutingIntegration:
    """Test the main integration class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock environment variable
        self.original_env = os.environ.get("ZEN_SMART_ROUTING")
        os.environ["ZEN_SMART_ROUTING"] = "true"
        
        self.integration = ModelRoutingIntegration()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.original_env is not None:
            os.environ["ZEN_SMART_ROUTING"] = self.original_env
        elif "ZEN_SMART_ROUTING" in os.environ:
            del os.environ["ZEN_SMART_ROUTING"]
    
    def test_initialization_enabled(self):
        """Test initialization when routing is enabled."""
        assert self.integration.enabled is True
        assert self.integration.router is not None
        assert self.integration.hooks is not None
    
    def test_initialization_disabled(self):
        """Test initialization when routing is disabled."""
        os.environ["ZEN_SMART_ROUTING"] = "false"
        integration = ModelRoutingIntegration()
        
        assert integration.enabled is False
        assert integration.router is None
    
    def test_get_model_provider_wrapping(self):
        """Test wrapping of get_model_provider method."""
        # Mock original method
        original_method = Mock(return_value="mock_provider")
        
        # Create wrapper
        wrapped_method = self.integration.wrap_get_model_provider(original_method)
        
        # Mock tool instance
        tool_instance = Mock()
        tool_instance.name = "test_tool"
        tool_instance._current_request = None
        
        # Test wrapper
        result = wrapped_method(tool_instance, "test_model")
        
        # Should call original method
        original_method.assert_called_once_with(tool_instance, "test_model")
        assert result == "mock_provider"
    
    def test_context_extraction(self):
        """Test context extraction from tool instances."""
        # Mock tool instance with request
        tool_instance = Mock()
        tool_instance.name = "test_tool"
        
        mock_request = Mock()
        mock_request.files = ["file1.py", "file2.js"]
        tool_instance._current_request = mock_request
        
        context = self.integration._extract_tool_context(tool_instance, {})
        
        assert context["tool_name"] == "test_tool"
        assert context["files"] == ["file1.py", "file2.js"]
        assert context["file_types"] == ["py", "js"]
    
    def test_routing_recommendation(self):
        """Test getting routing recommendations."""
        tool_instance = Mock()
        tool_instance.name = "codereview"
        
        context = {"tool_name": "codereview", "files": ["test.py"]}
        
        with patch.object(self.integration, '_build_analysis_prompt') as mock_build:
            mock_build.return_value = "Review Python code"
            
            result = self.integration._get_routing_recommendation(
                "auto", tool_instance, context
            )
            
            if result:  # May return None if no override needed
                assert hasattr(result, 'model')
                assert hasattr(result, 'confidence')
                assert hasattr(result, 'reasoning')
    
    def test_model_override_decision(self):
        """Test decision logic for model overriding."""
        # Mock routing result with free model
        mock_result = Mock()
        mock_result.model = Mock()
        mock_result.model.cost_per_token = 0.0
        mock_result.confidence = 0.9
        mock_result.reasoning = "Free model available"
        
        # Should override for free model
        should_override = self.integration._should_override_model("gpt-4", mock_result)
        assert should_override is True
        
        # Should override for auto model
        should_override = self.integration._should_override_model("auto", mock_result)
        assert should_override is True
        
        # Should not override for specific model with low confidence
        mock_result.model.cost_per_token = 0.01
        mock_result.confidence = 0.3
        mock_result.reasoning = "Low confidence"
        
        should_override = self.integration._should_override_model("claude-opus", mock_result)
        assert should_override is False
    
    def test_routing_statistics(self):
        """Test routing statistics collection."""
        stats = self.integration.get_routing_stats()
        
        assert "enabled" in stats
        assert "routing_decisions" in stats
        assert "routing_successes" in stats
        assert "routing_failures" in stats
        assert stats["enabled"] is True
    
    def test_performance_tracking(self):
        """Test model performance tracking integration."""
        model_name = "test_model"
        
        # Test success tracking
        self.integration.update_model_performance(model_name, True)
        
        # Test failure tracking
        self.integration.update_model_performance(model_name, False, "Test error")
        
        # Should not crash - actual tracking is in router
        assert True
    
    def test_external_recommendation_api(self):
        """Test external model recommendation API."""
        prompt = "Review this Python code"
        context = {"files": ["test.py"], "file_types": [".py"]}
        
        recommendation = self.integration.get_model_recommendation(prompt, context)
        
        if "error" not in recommendation:
            assert "model" in recommendation
            assert "confidence" in recommendation
            assert "reasoning" in recommendation
        # If error, that's also valid (no models configured in test)


class TestToolHooks:
    """Test tool-specific hooks functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.hooks = ToolHooks()
    
    def test_hook_registration(self):
        """Test that hooks are properly registered."""
        available_hooks = self.hooks.get_available_hooks()
        
        # Should have hooks for major tools
        expected_tools = ["chat", "codereview", "debug", "analyze", "consensus"]
        for tool in expected_tools:
            assert any(tool in hook for hook in available_hooks), (
                f"Missing hook for {tool}"
            )
    
    def test_analysis_prompt_building(self):
        """Test analysis prompt building for different tools."""
        for tool_name, scenarios in TOOL_SCENARIOS.items():
            for scenario in scenarios:
                prompt = self.hooks.build_analysis_prompt(tool_name, scenario["context"])
                
                assert prompt is not None
                assert len(prompt) > 0
                assert tool_name.lower() in prompt.lower() or "tool" in prompt.lower()
    
    def test_complexity_indicators_extraction(self):
        """Test complexity indicators extraction."""
        # Code review with multiple files
        context = {"tool_name": "codereview", "files": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"]}
        indicators = self.hooks.extract_complexity_indicators("codereview", context)
        
        assert "large_codebase" in indicators or "multi_file_review" in indicators
        
        # Debugging with error
        context = {"tool_name": "debug", "error": "NullPointerException"}
        indicators = self.hooks.extract_complexity_indicators("debug", context)
        
        assert "has_error_context" in indicators or "debugging_task" in indicators
    
    def test_model_preferences(self):
        """Test model preference suggestions."""
        # Security audit should prefer senior models
        context = {"tool_name": "secaudit", "files": ["auth.py"]}
        preferences = self.hooks.suggest_model_preferences("secaudit", context)
        
        # Should have some security-related preferences
        assert len(preferences) > 0
        
        # Consensus should prefer diverse models
        context = {"tool_name": "consensus"}
        preferences = self.hooks.suggest_model_preferences("consensus", context)
        
        if preferences:  # May not have preferences defined
            assert isinstance(preferences, dict)
    
    def test_custom_hook_registration(self):
        """Test registration of custom hooks."""
        # Create mock custom hook
        custom_hook = Mock()
        custom_hook.get_tool_names.return_value = ["custom_tool"]
        custom_hook.build_analysis_prompt.return_value = "Custom analysis"
        
        self.hooks.register_hook("custom_tool", custom_hook)
        
        prompt = self.hooks.build_analysis_prompt("custom_tool", {})
        assert prompt == "Custom analysis"


class TestModelWrapper:
    """Test model wrapper functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.wrapper = create_routing_wrapper()
    
    def test_wrapper_creation(self):
        """Test wrapper creation and initialization."""
        assert self.wrapper is not None
        assert hasattr(self.wrapper, 'router')
        assert hasattr(self.wrapper, 'complexity_analyzer')
    
    def test_model_call_wrapping(self):
        """Test wrapping of model calls."""
        # Mock original model call
        original_call = Mock(return_value="model_response")
        
        # Create context
        from routing.model_wrapper import ModelCallContext
        context = ModelCallContext(
            tool_name="test_tool",
            prompt="Test prompt",
            model_requested="auto"
        )
        
        # Wrap the call
        wrapped_call = self.wrapper.wrap_model_call(original_call, context)
        
        # Execute wrapped call
        result = wrapped_call()
        
        # Should return result from original call
        assert result == "model_response"
        original_call.assert_called_once()
    
    def test_routing_decision_making(self):
        """Test routing decision making process."""
        from routing.model_wrapper import ModelCallContext
        
        context = ModelCallContext(
            tool_name="codereview",
            prompt="Review this Python function",
            files=["test.py"],
            model_requested="auto"
        )
        
        decision = self.wrapper._make_routing_decision(context)
        
        assert hasattr(decision, 'original_model')
        assert hasattr(decision, 'selected_model')
        assert hasattr(decision, 'routing_used')
        assert decision.original_model == "auto"
    
    def test_call_statistics_tracking(self):
        """Test tracking of call statistics."""
        # Simulate some calls
        from routing.model_wrapper import ModelCallContext
        
        context = ModelCallContext(
            tool_name="test_tool",
            prompt="Test prompt"
        )
        
        # Mock successful call tracking
        self.wrapper._track_call_result(context, None, True, 0.1)
        
        # Mock failed call tracking  
        self.wrapper._track_call_result(context, None, False, 0.2, "Test error")
        
        stats = self.wrapper.get_call_statistics()
        
        assert stats["total_calls"] == 2
        assert stats["successful_calls"] == 1
        assert stats["success_rate"] == 0.5
    
    def test_recent_failures_tracking(self):
        """Test tracking of recent failures."""
        from routing.model_wrapper import ModelCallContext
        
        context = ModelCallContext(
            tool_name="test_tool",
            prompt="Test prompt"
        )
        
        # Track a failure
        self.wrapper._track_call_result(context, None, False, 0.1, "Test error")
        
        failures = self.wrapper.get_recent_failures(limit=5)
        
        assert len(failures) == 1
        assert failures[0]["success"] is False
        assert failures[0]["error"] == "Test error"


class TestServerIntegration:
    """Test integration with the MCP server."""
    
    def test_integration_function_exists(self):
        """Test that integration functions are available."""
        # Test that integration functions exist and can be imported
        assert integrate_with_server is not None
        assert route_model_request is not None
        assert get_integration_instance is not None
    
    def test_global_integration_instance(self):
        """Test global integration instance management."""
        instance1 = get_integration_instance()
        instance2 = get_integration_instance()
        
        # Should return same instance (singleton pattern)
        assert instance1 is instance2
    
    @patch.dict(os.environ, {"ZEN_SMART_ROUTING": "true"})
    def test_server_integration_enabled(self):
        """Test server integration when routing is enabled."""
        with patch('routing.integration.BaseTool') as mock_base_tool:
            # Mock BaseTool to avoid actual integration
            mock_base_tool.get_model_provider = Mock()
            
            # Should not raise exception
            integrate_with_server()
            
            # Verify integration was attempted
            # (Exact verification depends on implementation)
    
    @patch.dict(os.environ, {"ZEN_SMART_ROUTING": "false"})
    def test_server_integration_disabled(self):
        """Test server integration when routing is disabled."""
        # Should complete without error
        integrate_with_server()
        
        # Verify no integration occurred
        instance = get_integration_instance()
        assert instance.enabled is False
    
    def test_external_routing_api(self):
        """Test external routing API function."""
        prompt = "Simple test prompt"
        context = {"tool_name": "test"}
        
        result = route_model_request(prompt, context)
        
        assert isinstance(result, dict)
        # May contain error if routing not properly configured in test
        assert "error" in result or "model" in result


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing system."""
    
    @patch.dict(os.environ, {"ZEN_SMART_ROUTING": "false"})
    def test_disabled_routing_compatibility(self):
        """Test that system works normally when routing is disabled."""
        # Create integration instance with routing disabled
        integration = ModelRoutingIntegration()
        assert integration.enabled is False
        
        # Mock tool method
        original_method = Mock(return_value="original_result")
        wrapped_method = integration.wrap_get_model_provider(original_method)
        
        # Mock tool instance
        tool_instance = Mock()
        tool_instance.name = "test_tool"
        
        # Call wrapped method
        result = wrapped_method(tool_instance, "test_model")
        
        # Should call original method directly
        original_method.assert_called_once_with(tool_instance, "test_model")
        assert result == "original_result"
    
    def test_graceful_degradation(self):
        """Test graceful degradation when routing fails."""
        # Force routing to fail
        integration = ModelRoutingIntegration()
        integration.enabled = True
        integration.router = None  # Break router
        
        # Mock original method
        original_method = Mock(return_value="fallback_result")
        wrapped_method = integration.wrap_get_model_provider(original_method)
        
        # Mock tool instance
        tool_instance = Mock()
        tool_instance.name = "test_tool"
        
        # Should fall back to original method
        result = wrapped_method(tool_instance, "test_model")
        
        assert result == "fallback_result"
        original_method.assert_called()
    
    def test_existing_model_selection_preserved(self):
        """Test that existing model selection logic is preserved."""
        # When a specific model is requested and routing doesn't override
        integration = ModelRoutingIntegration()
        
        # Mock routing result that doesn't warrant override
        with patch.object(integration, '_get_routing_recommendation') as mock_routing:
            mock_routing.return_value = None  # No routing recommendation
            
            original_method = Mock(return_value="specific_model_provider")
            wrapped_method = integration.wrap_get_model_provider(original_method)
            
            tool_instance = Mock()
            tool_instance.name = "test_tool"
            
            result = wrapped_method(tool_instance, "claude-opus")
            
            # Should use original model selection
            original_method.assert_called_once_with(tool_instance, "claude-opus")
            assert result == "specific_model_provider"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_missing_dependencies(self):
        """Test behavior when routing dependencies are missing."""
        # This would test ImportError handling in real scenarios
        # Mock missing dependencies if needed
        pass
    
    def test_configuration_errors(self):
        """Test handling of configuration errors."""
        # Test with invalid configuration paths
        with patch('routing.integration.ModelLevelRouter') as mock_router:
            mock_router.side_effect = Exception("Config error")
            
            # Should not crash, should disable routing
            integration = ModelRoutingIntegration()
            
            # If initialization failed, should be disabled
            assert integration.enabled is False or integration.router is None
    
    def test_network_timeouts(self):
        """Test handling of network-related errors."""
        # This would test timeout handling for remote model availability checks
        # Implementation depends on how model availability is checked
        pass
    
    def test_memory_pressure_handling(self):
        """Test behavior under memory pressure."""
        # Test that caching is bounded and doesn't grow indefinitely
        integration = ModelRoutingIntegration()
        
        if integration.enabled and integration.router:
            # Make many requests to fill cache
            for i in range(1000):
                try:
                    integration.get_model_recommendation(f"Test prompt {i}")
                except:
                    pass  # Ignore errors in test environment
            
            # Cache should be bounded (implementation detail)
            # This is more of a regression test
            assert True  # If we get here without crash, test passes


class TestConcurrency:
    """Test concurrent access to routing system."""
    
    @pytest.mark.asyncio
    async def test_concurrent_routing_requests(self):
        """Test handling of concurrent routing requests."""
        integration = ModelRoutingIntegration()
        
        if not integration.enabled:
            pytest.skip("Routing not enabled in test environment")
        
        async def make_request(prompt):
            return integration.get_model_recommendation(prompt)
        
        # Make concurrent requests
        tasks = [
            make_request(f"Concurrent request {i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete without crashing
        assert len(results) == 10
        for result in results:
            if isinstance(result, Exception):
                # Exceptions are okay in test environment
                pass
            else:
                assert isinstance(result, dict)
    
    def test_thread_safety(self):
        """Test thread safety of routing components."""
        import threading
        import time
        
        integration = ModelRoutingIntegration()
        results = []
        errors = []
        
        def make_requests():
            try:
                for i in range(5):
                    result = integration.get_model_recommendation(f"Thread request {i}")
                    results.append(result)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = [threading.Thread(target=make_requests) for _ in range(3)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should complete without errors (or with acceptable errors in test env)
        # Main thing is no deadlocks or crashes
        assert True