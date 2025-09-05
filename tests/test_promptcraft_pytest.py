"""
PromptCraft Integration Tests using pytest

Comprehensive test suite for PromptCraft system components
using pytest conventions and fixtures.
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from plugins.promptcraft_system import PromptCraftSystemPlugin
from plugins.promptcraft_system.api_server import PromptCraftAPIServer
from plugins.promptcraft_system.background_workers import GraduationWorker, ModelDetectionWorker

# Import PromptCraft components
from plugins.promptcraft_system.data_manager import (
    ExperimentalModel,
    GraduationCandidate,
    ModelChannel,
    PromptCraftDataManager,
)


@pytest.fixture
def temp_data_dir():
    """Provide a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def data_manager(temp_data_dir):
    """Provide a test data manager instance."""
    return PromptCraftDataManager(temp_data_dir)


@pytest.fixture
def sample_experimental_model():
    """Provide a sample experimental model for testing."""
    return ExperimentalModel(
        id="test/sample-model:free",
        name="Sample Test Model",
        provider="test",
        cost_per_token=0.0,
        context_window=8000,
        added_date=datetime.now().isoformat(),
        usage_count=0,
        success_rate=0.0
    )


@pytest.fixture
def sample_graduation_candidate():
    """Provide a sample graduation candidate."""
    return GraduationCandidate(
        model_id="test/graduation-candidate:free",
        added_to_queue=datetime.now().isoformat(),
        usage_count=100,
        success_rate=0.96,
        humaneval_score=80.0,
        days_in_experimental=10,
        graduation_score=8.5,
        criteria_met={
            "age_requirement": True,
            "usage_requirement": True,
            "success_rate_requirement": True,
            "benchmark_requirement": True
        }
    )


class TestDataManager:
    """Test PromptCraft data manager functionality."""

    def test_initialization(self, data_manager, temp_data_dir):
        """Test data manager initialization."""
        assert data_manager.data_dir == temp_data_dir
        assert data_manager.experimental_models_path.exists()
        assert data_manager.graduation_queue_path.exists()
        assert data_manager.performance_metrics_path.exists()
        assert data_manager.channel_config_path.exists()
        assert data_manager.health_check()

    def test_add_experimental_model(self, data_manager, sample_experimental_model):
        """Test adding experimental models."""
        # Add model
        assert data_manager.add_experimental_model(sample_experimental_model)

        # Verify model was added
        models = data_manager.get_experimental_models()
        assert len(models) == 1
        assert models[0].id == sample_experimental_model.id
        assert models[0].name == sample_experimental_model.name

        # Test duplicate prevention
        assert not data_manager.add_experimental_model(sample_experimental_model)

    def test_model_usage_tracking(self, data_manager, sample_experimental_model):
        """Test usage statistics tracking."""
        # Add model
        data_manager.add_experimental_model(sample_experimental_model)

        # Update usage with mixed results
        assert data_manager.update_model_usage(sample_experimental_model.id, success=True)
        assert data_manager.update_model_usage(sample_experimental_model.id, success=True)
        assert data_manager.update_model_usage(sample_experimental_model.id, success=False)

        # Verify statistics
        models = data_manager.get_experimental_models()
        model = models[0]
        assert model.usage_count == 3
        assert abs(model.success_rate - (2/3)) < 0.001  # 66.7% success rate
        assert model.last_used is not None

    def test_graduation_queue_operations(self, data_manager, sample_graduation_candidate):
        """Test graduation queue management."""
        # Add to queue
        assert data_manager.add_to_graduation_queue(sample_graduation_candidate)

        # Verify addition
        queue = data_manager.get_graduation_queue()
        assert len(queue) == 1
        assert queue[0].model_id == sample_graduation_candidate.model_id
        assert queue[0].graduation_score == sample_graduation_candidate.graduation_score

        # Test duplicate prevention
        assert not data_manager.add_to_graduation_queue(sample_graduation_candidate)

        # Remove from queue
        assert data_manager.remove_from_graduation_queue(sample_graduation_candidate.model_id)
        queue = data_manager.get_graduation_queue()
        assert len(queue) == 0

    def test_graduation_criteria(self, data_manager):
        """Test graduation criteria retrieval."""
        criteria = data_manager.get_graduation_criteria()
        assert "minimum_age_days" in criteria
        assert "minimum_usage_requests" in criteria
        assert "minimum_success_rate" in criteria
        assert "minimum_humaneval_score" in criteria

    def test_performance_metrics(self, data_manager):
        """Test performance metrics management."""
        test_metrics = {
            "test_metric": 123,
            "api_calls": 456
        }

        assert data_manager.update_performance_metrics(test_metrics)

        # Get stats should include our metrics
        stats = data_manager.get_stats()
        assert "experimental_models" in stats
        assert "graduation_queue" in stats
        assert "last_updated" in stats

    def test_models_by_channel(self, data_manager, sample_experimental_model):
        """Test channel-based model filtering."""
        # Add experimental model
        data_manager.add_experimental_model(sample_experimental_model)

        # Get experimental models
        experimental_models = data_manager.get_models_by_channel(ModelChannel.EXPERIMENTAL)
        assert len(experimental_models) >= 1

        # Check that our model is there
        model_ids = [m.get("id", m.get("name", "")) for m in experimental_models]
        assert sample_experimental_model.id in model_ids


class TestAPIServer:
    """Test PromptCraft API server functionality."""

    @pytest.fixture
    def api_server(self, data_manager):
        """Provide API server instance."""
        return PromptCraftAPIServer(data_manager)

    def test_initialization(self, api_server):
        """Test API server initialization."""
        assert api_server.app is not None
        assert api_server.model_router is not None
        assert api_server.complexity_analyzer is not None
        assert api_server.data_manager is not None

    def test_metrics_tracking(self, api_server):
        """Test API metrics functionality."""
        initial_metrics = api_server.get_metrics()

        # Verify metric structure
        expected_keys = ["total_requests", "successful_requests", "success_rate", "average_response_time"]
        for key in expected_keys:
            assert key in initial_metrics

        # Simulate request processing
        api_server.request_count += 2
        api_server.successful_requests += 1
        api_server.total_response_time += 1.5

        updated_metrics = api_server.get_metrics()
        assert updated_metrics["total_requests"] == 2
        assert updated_metrics["successful_requests"] == 1
        assert updated_metrics["success_rate"] == 0.5
        assert updated_metrics["average_response_time"] == 0.75

    @pytest.mark.asyncio
    async def test_complexity_analysis(self, api_server):
        """Test prompt complexity analysis."""
        test_prompt = "Write a Python function to calculate fibonacci numbers"

        with patch.object(api_server.complexity_analyzer, 'analyze') as mock_analyze:
            # Mock analysis result
            mock_result = Mock()
            mock_result.task_type = "code_generation"
            mock_result.complexity_score = 0.7
            mock_result.complexity_level = "moderate"
            mock_result.indicators = ["algorithm", "recursion"]
            mock_analyze.return_value = mock_result

            # Test analysis
            analysis = await api_server._analyze_prompt_complexity(test_prompt)

            assert analysis["task_type"] == "code_generation"
            assert analysis["complexity_score"] == 0.7
            assert analysis["complexity_level"] == "moderate"
            assert "algorithm" in analysis["indicators"]

    def test_display_name_generation(self, api_server):
        """Test model display name formatting."""
        # Test free model
        free_model = {
            "name": "Free Coding Model",
            "cost_per_token": 0.0,
            "specialization": "coding",
            "humaneval_score": 85.5
        }

        display_name = api_server._generate_display_name(free_model)
        assert "🆓" in display_name
        assert "CODING" in display_name
        assert "85.5" in display_name

        # Test paid model
        paid_model = {
            "name": "Premium Model",
            "cost_per_token": 0.005,
            "specialization": "general",
            "humaneval_score": 0
        }

        display_name = api_server._generate_display_name(paid_model)
        assert "🆓" not in display_name
        assert "Premium Model" in display_name


class TestBackgroundWorkers:
    """Test background worker functionality."""

    @pytest.fixture
    def mock_data_manager(self):
        """Provide mock data manager."""
        mock = Mock()
        mock.get_experimental_models.return_value = []
        mock.get_models_by_channel.return_value = []
        mock.get_graduation_criteria.return_value = {
            "minimum_age_days": 7,
            "minimum_usage_requests": 50,
            "minimum_success_rate": 0.95,
            "minimum_humaneval_score": 70.0,
            "detection_config": {
                "quality_filters": {
                    "min_context_window": 4000,
                    "exclude_providers": ["test", "demo"]
                }
            }
        }
        return mock

    def test_model_detection_worker_init(self, mock_data_manager):
        """Test model detection worker initialization."""
        worker = ModelDetectionWorker(mock_data_manager, check_interval_hours=1)

        assert worker.data_manager is mock_data_manager
        assert worker.check_interval_hours == 1
        assert not worker.running

    @patch('requests.get')
    def test_detection_cycle(self, mock_get, mock_data_manager):
        """Test model detection cycle."""
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
                },
                {
                    "id": "filtered/low-context:free",
                    "name": "Low Context Model",
                    "context_length": 2000,  # Below threshold
                    "pricing": {"prompt": "$0", "completion": "$0"}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock data manager responses
        mock_data_manager.add_experimental_model.return_value = True

        worker = ModelDetectionWorker(mock_data_manager, check_interval_hours=1)

        # Run detection cycle
        worker._detection_cycle()

        # Verify OpenRouter API was called
        mock_get.assert_called_once()

        # Verify data manager was called (only for models that pass filters)
        mock_data_manager.add_experimental_model.assert_called()

    def test_graduation_worker_init(self, mock_data_manager):
        """Test graduation worker initialization."""
        worker = GraduationWorker(mock_data_manager, check_interval_hours=24)

        assert worker.data_manager is mock_data_manager
        assert worker.check_interval_hours == 24
        assert not worker.running

    def test_graduation_eligibility_evaluation(self, mock_data_manager):
        """Test graduation eligibility evaluation."""
        worker = GraduationWorker(mock_data_manager)

        # Create qualified model
        qualified_model = ExperimentalModel(
            id="qualified/model:free",
            name="Qualified Model",
            provider="qualified",
            cost_per_token=0.0,
            context_window=8000,
            added_date="2025-01-01T00:00:00Z",  # Old enough
            usage_count=100,  # Above threshold
            success_rate=0.97,  # Above threshold
            humaneval_score=85.0  # Above threshold
        )

        criteria = {
            "minimum_age_days": 7,
            "minimum_usage_requests": 50,
            "minimum_success_rate": 0.95,
            "minimum_humaneval_score": 70.0
        }

        candidate = worker._evaluate_graduation_eligibility(qualified_model, criteria)

        assert candidate is not None
        assert candidate.model_id == qualified_model.id
        assert candidate.graduation_score >= 7.5  # Should meet threshold
        assert all(candidate.criteria_met.values())


class TestPluginIntegration:
    """Test complete plugin integration."""

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = PromptCraftSystemPlugin()

        assert plugin.name == "promptcraft_system"
        assert plugin.version == "1.0.0"
        assert not plugin.initialized

        # Initialize plugin
        assert plugin.initialize()
        assert plugin.initialized
        assert plugin.data_manager is not None
        assert plugin.api_server is not None

    def test_plugin_status(self):
        """Test plugin status reporting."""
        plugin = PromptCraftSystemPlugin()
        plugin.initialize()

        status = plugin.get_status()

        expected_keys = [
            "plugin_name", "plugin_version", "initialized",
            "api_server_running", "background_workers", "data_manager_healthy"
        ]

        for key in expected_keys:
            assert key in status

        assert status["plugin_name"] == "promptcraft_system"
        assert status["initialized"] is True

    def test_plugin_tools_interface(self):
        """Test plugin tools interface."""
        plugin = PromptCraftSystemPlugin()
        plugin.initialize()

        tools = plugin.get_tools()
        assert isinstance(tools, dict)
        # API-based integration should return empty dict

    @patch.dict('os.environ', {'ENABLE_PROMPTCRAFT_WORKERS': 'false'})
    def test_plugin_without_workers(self):
        """Test plugin with workers disabled."""
        plugin = PromptCraftSystemPlugin()

        assert plugin.initialize()
        assert len(plugin.background_workers) == 0


class TestRoutingIntegration:
    """Test integration with existing zen-mcp-server routing."""

    def test_routing_imports(self):
        """Test that routing components can be imported."""
        from routing.complexity_analyzer import ComplexityAnalyzer
        from routing.model_level_router import ModelLevelRouter

        # Should be able to instantiate
        router = ModelLevelRouter()
        analyzer = ComplexityAnalyzer()

        assert router is not None
        assert analyzer is not None

    def test_api_server_routing_integration(self, data_manager):
        """Test API server integration with routing components."""
        api_server = PromptCraftAPIServer(data_manager)

        # Should have routing components
        assert hasattr(api_server, 'model_router')
        assert hasattr(api_server, 'complexity_analyzer')

        # Should be able to use them
        assert api_server.model_router is not None
        assert api_server.complexity_analyzer is not None


# Integration tests that require actual components
class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.fixture
    def plugin_system(self):
        """Set up complete plugin system."""
        plugin = PromptCraftSystemPlugin()
        plugin.initialize()
        return plugin

    def test_complete_workflow(self, plugin_system, sample_experimental_model):
        """Test a complete workflow from model addition to potential graduation."""
        # Add experimental model
        assert plugin_system.data_manager.add_experimental_model(sample_experimental_model)

        # Simulate usage
        model_id = sample_experimental_model.id
        for i in range(10):
            success = i % 4 != 0  # 75% success rate
            plugin_system.data_manager.update_model_usage(model_id, success)

        # Check that model statistics are tracked
        models = plugin_system.data_manager.get_experimental_models()
        test_model = next(m for m in models if m.id == model_id)

        assert test_model.usage_count == 10
        assert test_model.success_rate == 0.75

        # Check system health
        status = plugin_system.get_status()
        assert status["data_manager_healthy"] is True

    def test_data_persistence(self, temp_data_dir, sample_experimental_model):
        """Test that data persists across manager instances."""
        # Create first data manager and add model
        dm1 = PromptCraftDataManager(temp_data_dir)
        dm1.add_experimental_model(sample_experimental_model)

        # Create second data manager (should load existing data)
        dm2 = PromptCraftDataManager(temp_data_dir)
        models = dm2.get_experimental_models()

        assert len(models) == 1
        assert models[0].id == sample_experimental_model.id


if __name__ == "__main__":
    # Run with pytest from command line or programmatically
    pytest.main([__file__, "-v"])
