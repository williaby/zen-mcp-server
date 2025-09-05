"""
Core PromptCraft functionality tests.

Focused tests for the essential PromptCraft components without complex scenarios.
"""

import tempfile
from datetime import datetime

import pytest

from plugins.promptcraft_system.data_manager import ExperimentalModel, PromptCraftDataManager


class TestPromptCraftCore:
    """Test core PromptCraft functionality."""

    def test_data_manager_basic_flow(self):
        """Test basic data manager operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dm = PromptCraftDataManager(temp_dir)

            # Verify initialization
            assert dm.health_check()
            assert dm.get_experimental_models() == []

            # Add a model
            model = ExperimentalModel(
                id="test/model:free",
                name="Test Model",
                provider="test",
                cost_per_token=0.0,
                context_window=4000,
                added_date=datetime.now().isoformat()
            )

            assert dm.add_experimental_model(model)

            # Verify retrieval
            models = dm.get_experimental_models()
            assert len(models) == 1
            assert models[0].id == "test/model:free"

            # Test usage tracking
            assert dm.update_model_usage("test/model:free", success=True)
            updated_models = dm.get_experimental_models()
            assert updated_models[0].usage_count == 1
            assert updated_models[0].success_rate == 1.0

    def test_api_server_initialization(self):
        """Test API server can be created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dm = PromptCraftDataManager(temp_dir)

            from plugins.promptcraft_system.api_server import PromptCraftAPIServer
            api_server = PromptCraftAPIServer(dm)

            assert api_server.app is not None
            assert api_server.data_manager is dm

            # Test metrics
            metrics = api_server.get_metrics()
            assert "total_requests" in metrics
            assert metrics["total_requests"] == 0

    def test_plugin_initialization(self):
        """Test plugin can be initialized."""
        from plugins.promptcraft_system import PromptCraftSystemPlugin

        plugin = PromptCraftSystemPlugin()
        assert not plugin.initialized

        # Initialize (this creates data manager and API server)
        success = plugin.initialize()
        assert success
        assert plugin.initialized
        assert plugin.data_manager is not None
        assert plugin.api_server is not None

        # Test status
        status = plugin.get_status()
        assert status["plugin_name"] == "promptcraft_system"
        assert status["initialized"] is True

    def test_routing_integration(self):
        """Test integration with existing routing components."""
        # Import should work
        from routing.complexity_analyzer import ComplexityAnalyzer
        from routing.model_level_router import ModelLevelRouter

        router = ModelLevelRouter()
        analyzer = ComplexityAnalyzer()

        assert router is not None
        assert analyzer is not None

    def test_background_workers_init(self):
        """Test background workers can be initialized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dm = PromptCraftDataManager(temp_dir)

            from plugins.promptcraft_system.background_workers import GraduationWorker, ModelDetectionWorker

            # Should be able to create workers
            detection_worker = ModelDetectionWorker(dm, check_interval_hours=1)
            graduation_worker = GraduationWorker(dm, check_interval_hours=1)

            assert not detection_worker.running
            assert not graduation_worker.running
            assert detection_worker.data_manager is dm
            assert graduation_worker.data_manager is dm


def test_imports_work():
    """Test that all main components can be imported."""
    # These should not raise exceptions
    from plugins.promptcraft_system import PromptCraftSystemPlugin
    from plugins.promptcraft_system.api_server import PromptCraftAPIServer
    from plugins.promptcraft_system.background_workers import ModelDetectionWorker
    from plugins.promptcraft_system.data_manager import PromptCraftDataManager

    # Should be able to create instances
    assert PromptCraftSystemPlugin is not None
    assert PromptCraftDataManager is not None
    assert PromptCraftAPIServer is not None
    assert ModelDetectionWorker is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
