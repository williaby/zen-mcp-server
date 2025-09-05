"""
Integration tests for PromptCraft system.

Tests the complete PromptCraft integration including API endpoints,
data management, background workers, and routing integration.
"""

import pytest
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any
import requests
from unittest.mock import Mock, patch, MagicMock

# Import PromptCraft components
from plugins.promptcraft_system import PromptCraftSystemPlugin
from plugins.promptcraft_system.data_manager import PromptCraftDataManager, ExperimentalModel, GraduationCandidate
from plugins.promptcraft_system.api_server import PromptCraftAPIServer
from plugins.promptcraft_system.background_workers import ModelDetectionWorker, GraduationWorker


class TestPromptCraftDataManager:
    """Test the data management functionality."""
    
    def setup_method(self):
        """Setup test data manager with temporary directory."""
        self.test_data_dir = Path("/tmp/test_promptcraft_data")
        self.test_data_dir.mkdir(exist_ok=True)
        self.data_manager = PromptCraftDataManager(self.test_data_dir)
    
    def teardown_method(self):
        """Cleanup test data."""
        import shutil
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test that data manager initializes correctly."""
        assert self.data_manager.data_dir == self.test_data_dir
        assert self.data_manager.experimental_models_path.exists()
        assert self.data_manager.graduation_queue_path.exists()
        assert self.data_manager.performance_metrics_path.exists()
        assert self.data_manager.channel_config_path.exists()
    
    def test_experimental_model_operations(self):
        """Test adding and retrieving experimental models."""
        # Create test model
        test_model = ExperimentalModel(
            id="test/test-model:free",
            name="Test Model",
            provider="test",
            cost_per_token=0.0,
            context_window=4000,
            added_date="2025-01-05T10:00:00Z"
        )
        
        # Add model
        assert self.data_manager.add_experimental_model(test_model)
        
        # Retrieve models
        models = self.data_manager.get_experimental_models()
        assert len(models) == 1
        assert models[0].id == "test/test-model:free"
        assert models[0].name == "Test Model"
        
        # Test duplicate addition
        assert not self.data_manager.add_experimental_model(test_model)
    
    def test_model_usage_tracking(self):
        """Test model usage statistics tracking."""
        # Add test model
        test_model = ExperimentalModel(
            id="test/usage-model:free",
            name="Usage Test Model",
            provider="test",
            cost_per_token=0.0,
            context_window=4000,
            added_date="2025-01-05T10:00:00Z"
        )
        self.data_manager.add_experimental_model(test_model)
        
        # Update usage - successful requests
        assert self.data_manager.update_model_usage("test/usage-model:free", success=True)
        assert self.data_manager.update_model_usage("test/usage-model:free", success=True)
        assert self.data_manager.update_model_usage("test/usage-model:free", success=False)
        
        # Check statistics
        models = self.data_manager.get_experimental_models()
        model = models[0]
        assert model.usage_count == 3
        assert model.success_rate == 2.0 / 3.0  # 2 successful out of 3
        assert model.last_used is not None
    
    def test_graduation_queue_operations(self):
        """Test graduation queue management."""
        # Create graduation candidate
        candidate = GraduationCandidate(
            model_id="test/graduation-model:free",
            added_to_queue="2025-01-05T10:00:00Z",
            usage_count=100,
            success_rate=0.96,
            humaneval_score=75.0,
            days_in_experimental=10,
            graduation_score=8.5,
            criteria_met={
                "age_requirement": True,
                "usage_requirement": True,
                "success_rate_requirement": True,
                "benchmark_requirement": True
            }
        )
        
        # Add to queue
        assert self.data_manager.add_to_graduation_queue(candidate)
        
        # Retrieve queue
        queue = self.data_manager.get_graduation_queue()
        assert len(queue) == 1
        assert queue[0].model_id == "test/graduation-model:free"
        assert queue[0].graduation_score == 8.5
        
        # Remove from queue
        assert self.data_manager.remove_from_graduation_queue("test/graduation-model:free")
        queue = self.data_manager.get_graduation_queue()
        assert len(queue) == 0
    
    def test_health_check(self):
        """Test data manager health check."""
        assert self.data_manager.health_check()
        
        # Test with corrupted file
        with open(self.data_manager.experimental_models_path, 'w') as f:
            f.write("invalid json")
        
        assert not self.data_manager.health_check()


class TestPromptCraftAPIServer:
    """Test the API server functionality."""
    
    def setup_method(self):
        """Setup test API server."""
        self.test_data_dir = Path("/tmp/test_api_data")
        self.test_data_dir.mkdir(exist_ok=True)
        self.data_manager = PromptCraftDataManager(self.test_data_dir)
        self.api_server = PromptCraftAPIServer(self.data_manager)
    
    def teardown_method(self):
        """Cleanup test data."""
        import shutil
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
    
    def test_app_initialization(self):
        """Test that FastAPI app is properly initialized."""
        assert self.api_server.app is not None
        assert self.api_server.model_router is not None
        assert self.api_server.complexity_analyzer is not None
    
    @patch('plugins.promptcraft_system.api_server.ComplexityAnalyzer')
    def test_complexity_analysis(self, mock_analyzer_class):
        """Test prompt complexity analysis."""
        # Mock analyzer result
        mock_result = Mock()
        mock_result.task_type = "code_generation"
        mock_result.complexity_score = 0.7
        mock_result.complexity_level = "moderate"
        mock_result.indicators = ["function_creation"]
        
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.analyze.return_value = mock_result
        
        # Create new API server with mocked analyzer
        api_server = PromptCraftAPIServer(self.data_manager)
        api_server.complexity_analyzer = mock_analyzer
        
        # Test analysis
        import asyncio
        analysis = asyncio.run(api_server._analyze_prompt_complexity("def test(): pass"))
        
        assert analysis["task_type"] == "code_generation"
        assert analysis["complexity_score"] == 0.7
        assert analysis["complexity_level"] == "moderate"
        assert "function_creation" in analysis["indicators"]
    
    def test_metrics_tracking(self):
        """Test API metrics tracking."""
        initial_count = self.api_server.request_count
        initial_success = self.api_server.successful_requests
        
        # Simulate request processing
        self.api_server.request_count += 1
        self.api_server.successful_requests += 1
        self.api_server.total_response_time += 0.5
        
        metrics = self.api_server.get_metrics()
        assert metrics["total_requests"] == initial_count + 1
        assert metrics["successful_requests"] == initial_success + 1
        assert metrics["average_response_time"] == 0.5


class TestBackgroundWorkers:
    """Test background worker functionality."""
    
    def setup_method(self):
        """Setup test environment for workers."""
        self.test_data_dir = Path("/tmp/test_worker_data")
        self.test_data_dir.mkdir(exist_ok=True)
        self.data_manager = PromptCraftDataManager(self.test_data_dir)
    
    def teardown_method(self):
        """Cleanup test data."""
        import shutil
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
    
    @patch('requests.get')
    def test_model_detection_worker(self, mock_get):
        """Test model detection from OpenRouter."""
        # Mock OpenRouter API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "new/test-model:free",
                    "name": "New Test Model",
                    "context_length": 8000,
                    "pricing": {
                        "prompt": "$0.000000",
                        "completion": "$0.000000"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create worker with short interval for testing
        worker = ModelDetectionWorker(self.data_manager, check_interval_hours=0.001)
        
        # Run single detection cycle
        worker._detection_cycle()
        
        # Check that model was added
        experimental_models = self.data_manager.get_experimental_models()
        assert len(experimental_models) >= 1
        
        # Find our test model
        test_model = next(
            (m for m in experimental_models if m.id == "new/test-model:free"), 
            None
        )
        assert test_model is not None
        assert test_model.name == "New Test Model"
        assert test_model.context_window == 8000
    
    def test_graduation_worker_evaluation(self):
        """Test graduation candidate evaluation."""
        # Add experimental model that meets graduation criteria
        qualified_model = ExperimentalModel(
            id="qualified/model:free",
            name="Qualified Model",
            provider="qualified",
            cost_per_token=0.0,
            context_window=4000,
            added_date="2025-01-01T10:00:00Z",  # 4+ days old
            usage_count=100,  # > 50 required
            success_rate=0.98,  # > 0.95 required
            humaneval_score=80.0  # > 70.0 required
        )
        self.data_manager.add_experimental_model(qualified_model)
        
        # Create graduation worker
        worker = GraduationWorker(self.data_manager)
        
        # Get graduation criteria
        criteria = self.data_manager.get_graduation_criteria()
        
        # Evaluate model
        candidate = worker._evaluate_graduation_eligibility(qualified_model, criteria)
        
        assert candidate is not None
        assert candidate.model_id == "qualified/model:free"
        assert candidate.graduation_score >= 7.5  # Should meet graduation threshold
        assert all(candidate.criteria_met.values())  # All criteria should be met


class TestPromptCraftIntegration:
    """Integration tests for the complete PromptCraft system."""
    
    def setup_method(self):
        """Setup complete test environment."""
        self.test_data_dir = Path("/tmp/test_integration_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
    
    def test_plugin_initialization(self):
        """Test complete plugin initialization."""
        plugin = PromptCraftSystemPlugin()
        
        # Initialize plugin
        assert plugin.initialize()
        assert plugin.initialized
        assert plugin.data_manager is not None
        assert plugin.api_server is not None
    
    def test_plugin_status_reporting(self):
        """Test plugin status and health reporting."""
        plugin = PromptCraftSystemPlugin()
        plugin.initialize()
        
        status = plugin.get_status()
        
        assert status["plugin_name"] == "promptcraft_system"
        assert status["plugin_version"] == "1.0.0"
        assert status["initialized"] is True
        assert "api_server_running" in status
        assert "data_manager_healthy" in status
    
    @patch.dict('os.environ', {'ENABLE_PROMPTCRAFT_WORKERS': 'false'})
    def test_plugin_without_workers(self):
        """Test plugin initialization without background workers."""
        plugin = PromptCraftSystemPlugin()
        
        assert plugin.initialize()
        assert len(plugin.background_workers) == 0
    
    def test_data_consistency(self):
        """Test data consistency across components."""
        # Initialize plugin
        plugin = PromptCraftSystemPlugin()
        plugin.initialize()
        
        # Add experimental model through data manager
        test_model = ExperimentalModel(
            id="consistency/test-model:free",
            name="Consistency Test",
            provider="test",
            cost_per_token=0.0,
            context_window=4000,
            added_date="2025-01-05T10:00:00Z"
        )
        
        assert plugin.data_manager.add_experimental_model(test_model)
        
        # Verify model appears in experimental channel
        from plugins.promptcraft_system.data_manager import ModelChannel
        experimental_models = plugin.data_manager.get_models_by_channel(ModelChannel.EXPERIMENTAL)
        
        assert len(experimental_models) >= 1
        test_model_found = any(
            model.get("id") == "consistency/test-model:free" 
            for model in experimental_models
        )
        assert test_model_found


# API Endpoint Tests (require running server)
class TestPromptCraftAPIEndpoints:
    """Test API endpoints with actual HTTP requests."""
    
    @pytest.fixture(scope="class")
    def api_server_url(self):
        """Provide API server URL for testing."""
        return "http://localhost:3000"  # Assumes server is running for tests
    
    @pytest.mark.integration
    def test_health_endpoint(self, api_server_url):
        """Test health check endpoint."""
        try:
            response = requests.get(f"{api_server_url}/health", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert data["service"] == "promptcraft-api"
            
        except requests.ConnectionError:
            pytest.skip("API server not running for integration tests")
    
    @pytest.mark.integration 
    def test_route_analysis_endpoint(self, api_server_url):
        """Test route analysis endpoint."""
        try:
            payload = {
                "prompt": "Write a Python function to sort a list",
                "user_tier": "free",
                "task_type": "code_generation"
            }
            
            response = requests.post(
                f"{api_server_url}/api/promptcraft/route/analyze",
                json=payload,
                timeout=10
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "analysis" in data
            assert "recommendations" in data
            assert data["analysis"]["task_type"] in ["code_generation", "coding", "general"]
            
        except requests.ConnectionError:
            pytest.skip("API server not running for integration tests")
    
    @pytest.mark.integration
    def test_models_list_endpoint(self, api_server_url):
        """Test models list endpoint."""
        try:
            params = {
                "user_tier": "free",
                "channel": "stable",
                "include_metadata": "true"
            }
            
            response = requests.get(
                f"{api_server_url}/api/promptcraft/models/available",
                params=params,
                timeout=10
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "models" in data
            assert data["channel"] == "stable"
            assert data["user_tier"] == "free"
            assert data["total_models"] >= 0
            
        except requests.ConnectionError:
            pytest.skip("API server not running for integration tests")


# Test Utilities
class TestPromptCraftUtilities:
    """Test utility functions and helpers."""
    
    def test_model_display_name_generation(self):
        """Test model display name formatting for UI."""
        api_server = PromptCraftAPIServer(Mock())
        
        # Test free model
        free_model = {
            "name": "Free Test Model",
            "cost_per_token": 0.0,
            "specialization": "coding",
            "humaneval_score": 85.0
        }
        
        display_name = api_server._generate_display_name(free_model)
        assert "🆓" in display_name
        assert "CODING" in display_name
        assert "85.0" in display_name
        
        # Test paid model
        paid_model = {
            "name": "Premium Model",
            "cost_per_token": 0.005,
            "specialization": "general",
            "humaneval_score": 0.0
        }
        
        display_name = api_server._generate_display_name(paid_model)
        assert "🆓" not in display_name
        assert "Premium Model" in display_name


if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running basic PromptCraft integration tests...")
    
    # Test data manager
    data_test = TestPromptCraftDataManager()
    data_test.setup_method()
    try:
        data_test.test_initialization()
        data_test.test_experimental_model_operations()
        print("✅ Data manager tests passed")
    finally:
        data_test.teardown_method()
    
    # Test plugin initialization
    integration_test = TestPromptCraftIntegration()
    integration_test.setup_method()
    try:
        integration_test.test_plugin_initialization()
        print("✅ Plugin initialization tests passed")
    finally:
        integration_test.teardown_method()
    
    print("🎉 Basic PromptCraft integration tests completed successfully!")