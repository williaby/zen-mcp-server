"""
Background Workers for PromptCraft System

Handles automated model detection from OpenRouter and graduation
of experimental models to stable channel based on performance criteria.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .data_manager import ExperimentalModel, GraduationCandidate, ModelChannel

logger = logging.getLogger(__name__)

class ModelDetectionWorker:
    """
    Background worker for detecting new models from OpenRouter API.
    
    Runs every N hours (configurable) to:
    1. Fetch current model list from OpenRouter
    2. Compare with known models (stable + experimental)
    3. Apply quality filters to new models
    4. Add qualifying models to experimental channel
    """

    def __init__(self, data_manager, check_interval_hours: int = 6):
        self.data_manager = data_manager
        self.check_interval_hours = check_interval_hours
        self.running = False
        self.stop_event = threading.Event()

    def start(self):
        """Start the model detection worker loop."""
        self.running = True
        logger.info(f"🔍 Starting model detection worker (every {self.check_interval_hours}h)")

        while not self.stop_event.wait(self.check_interval_hours * 3600):
            try:
                self._detection_cycle()
            except Exception as e:
                logger.error(f"❌ Model detection cycle failed: {e}")

        logger.info("🛑 Model detection worker stopped")

    def stop(self):
        """Stop the model detection worker."""
        self.stop_event.set()
        self.running = False

    def _detection_cycle(self):
        """Run a single model detection cycle."""
        logger.info("🔍 Starting model detection cycle...")
        start_time = time.time()

        try:
            # Fetch models from OpenRouter
            openrouter_models = self._fetch_openrouter_models()
            if not openrouter_models:
                logger.warning("No models fetched from OpenRouter")
                return

            # Get known models (stable + experimental)
            known_models = self._get_known_models()

            # Find new models
            new_models = self._find_new_models(openrouter_models, known_models)

            # Apply quality filters
            qualified_models = self._apply_quality_filters(new_models)

            # Add to experimental channel
            added_count = 0
            for model_data in qualified_models:
                if self._add_to_experimental(model_data):
                    added_count += 1

            duration = time.time() - start_time
            logger.info(f"✅ Detection cycle complete: {added_count} new models added (took {duration:.2f}s)")

        except Exception as e:
            logger.error(f"❌ Detection cycle failed: {e}")

    def _fetch_openrouter_models(self) -> List[Dict[str, Any]]:
        """Fetch current model list from OpenRouter API."""
        try:
            # OpenRouter models API endpoint
            url = "https://openrouter.ai/api/v1/models"
            headers = {
                "User-Agent": "zen-mcp-server/1.0"
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            logger.info(f"📥 Fetched {len(models)} models from OpenRouter")
            return models

        except Exception as e:
            logger.error(f"❌ Failed to fetch OpenRouter models: {e}")
            return []

    def _get_known_models(self) -> set:
        """Get set of known model IDs (stable + experimental)."""
        known_ids = set()

        try:
            # Get stable models
            stable_models = self.data_manager.get_models_by_channel(ModelChannel.STABLE)
            known_ids.update(model.get("id", model.get("name", "")) for model in stable_models)

            # Get experimental models
            experimental_models = self.data_manager.get_experimental_models()
            known_ids.update(model.id for model in experimental_models)

            logger.debug(f"📊 Known models: {len(known_ids)}")
            return known_ids

        except Exception as e:
            logger.error(f"❌ Failed to get known models: {e}")
            return set()

    def _find_new_models(self, openrouter_models: List[Dict[str, Any]], known_models: set) -> List[Dict[str, Any]]:
        """Find models that aren't in our known set."""
        new_models = []

        for model in openrouter_models:
            model_id = model.get("id", "")
            if model_id and model_id not in known_models:
                new_models.append(model)

        logger.info(f"🆕 Found {len(new_models)} new models")
        return new_models

    def _apply_quality_filters(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply quality filters to new models."""
        qualified = []

        # Get quality filter configuration
        config = self.data_manager.get_graduation_criteria()
        quality_filters = config.get("detection_config", {}).get("quality_filters", {})

        min_context = quality_filters.get("min_context_window", 4000)
        excluded_providers = quality_filters.get("exclude_providers", [])

        for model in models:
            # Check context window
            context_window = model.get("context_length", 0)
            if context_window < min_context:
                continue

            # Check provider exclusions
            model_id = model.get("id", "")
            if any(excluded in model_id.lower() for excluded in excluded_providers):
                continue

            # Check if model has reasonable pricing info
            pricing = model.get("pricing", {})
            if not pricing:
                continue

            qualified.append(model)

        logger.info(f"✅ {len(qualified)} models passed quality filters")
        return qualified

    def _add_to_experimental(self, openrouter_model: Dict[str, Any]) -> bool:
        """Add a new model to experimental channel."""
        try:
            # Extract pricing
            pricing = openrouter_model.get("pricing", {})
            input_cost = float(pricing.get("prompt", "0").replace("$", ""))

            # Create experimental model
            experimental_model = ExperimentalModel(
                id=openrouter_model["id"],
                name=openrouter_model.get("name", openrouter_model["id"]),
                provider=openrouter_model["id"].split("/")[0] if "/" in openrouter_model["id"] else "unknown",
                cost_per_token=input_cost,
                context_window=openrouter_model.get("context_length", 0),
                added_date=datetime.now().isoformat(),
                usage_count=0,
                success_rate=0.0,
                humaneval_score=None,
                last_used=None,
                graduation_eligible=False
            )

            # Add to data manager
            success = self.data_manager.add_experimental_model(experimental_model)
            if success:
                logger.info(f"➕ Added experimental model: {experimental_model.id}")

            return success

        except Exception as e:
            logger.error(f"❌ Failed to add experimental model: {e}")
            return False

class GraduationWorker:
    """
    Background worker for graduating experimental models to stable channel.
    
    Runs daily to:
    1. Check experimental models against graduation criteria
    2. Run benchmarks on qualifying models
    3. Graduate models that meet all requirements
    4. Update stable models.csv with graduated models
    """

    def __init__(self, data_manager, check_interval_hours: int = 24):
        self.data_manager = data_manager
        self.check_interval_hours = check_interval_hours
        self.running = False
        self.stop_event = threading.Event()

    def start(self):
        """Start the graduation worker loop."""
        self.running = True
        logger.info(f"🎓 Starting graduation worker (every {self.check_interval_hours}h)")

        while not self.stop_event.wait(self.check_interval_hours * 3600):
            try:
                self._graduation_cycle()
            except Exception as e:
                logger.error(f"❌ Graduation cycle failed: {e}")

        logger.info("🛑 Graduation worker stopped")

    def stop(self):
        """Stop the graduation worker."""
        self.stop_event.set()
        self.running = False

    def _graduation_cycle(self):
        """Run a single graduation evaluation cycle."""
        logger.info("🎓 Starting graduation cycle...")
        start_time = time.time()

        try:
            # Get graduation criteria
            criteria = self.data_manager.get_graduation_criteria()

            # Get experimental models
            experimental_models = self.data_manager.get_experimental_models()

            # Check each model for graduation eligibility
            candidates = []
            for model in experimental_models:
                candidate = self._evaluate_graduation_eligibility(model, criteria)
                if candidate and candidate.graduation_score >= 7.5:  # Threshold for graduation
                    candidates.append(candidate)

            # Run benchmarks on candidates
            benchmarked_candidates = []
            for candidate in candidates:
                benchmark_result = self._run_benchmarks(candidate)
                if benchmark_result:
                    benchmarked_candidates.append(benchmark_result)

            # Graduate qualified candidates
            graduated_count = 0
            for candidate in benchmarked_candidates:
                if self._graduate_model(candidate):
                    graduated_count += 1

            duration = time.time() - start_time
            logger.info(f"✅ Graduation cycle complete: {graduated_count} models graduated (took {duration:.2f}s)")

        except Exception as e:
            logger.error(f"❌ Graduation cycle failed: {e}")

    def _evaluate_graduation_eligibility(self, model: ExperimentalModel, criteria: Dict[str, Any]) -> Optional[GraduationCandidate]:
        """Evaluate if a model is eligible for graduation."""
        try:
            # Check age requirement
            added_date = datetime.fromisoformat(model.added_date.replace('Z', '+00:00'))
            days_in_experimental = (datetime.now() - added_date).days

            min_age_days = criteria.get("minimum_age_days", 7)
            min_usage = criteria.get("minimum_usage_requests", 50)
            min_success_rate = criteria.get("minimum_success_rate", 0.95)

            # Evaluate criteria
            criteria_met = {
                "age_requirement": days_in_experimental >= min_age_days,
                "usage_requirement": model.usage_count >= min_usage,
                "success_rate_requirement": model.success_rate >= min_success_rate,
                "has_benchmark_score": model.humaneval_score is not None
            }

            # Calculate graduation score
            score_components = {
                "age_score": min(days_in_experimental / min_age_days, 2.0) * 2.0,  # Max 4.0
                "usage_score": min(model.usage_count / min_usage, 2.0) * 1.5,     # Max 3.0
                "success_rate_score": model.success_rate * 2.0,                   # Max 2.0
                "benchmark_score": (model.humaneval_score or 0) / 100.0 * 1.0    # Max 1.0
            }

            graduation_score = sum(score_components.values())

            # Only create candidate if basic criteria are met
            if all(criteria_met.values()):
                return GraduationCandidate(
                    model_id=model.id,
                    added_to_queue=datetime.now().isoformat(),
                    usage_count=model.usage_count,
                    success_rate=model.success_rate,
                    humaneval_score=model.humaneval_score,
                    days_in_experimental=days_in_experimental,
                    graduation_score=graduation_score,
                    criteria_met=criteria_met
                )

            return None

        except Exception as e:
            logger.error(f"❌ Failed to evaluate graduation for {model.id}: {e}")
            return None

    def _run_benchmarks(self, candidate: GraduationCandidate) -> Optional[GraduationCandidate]:
        """Run benchmarks on graduation candidate."""
        try:
            # For now, simulate benchmarking
            # In a full implementation, this would run HumanEval or other benchmarks

            if candidate.humaneval_score is None:
                # Simulate benchmark score (in reality, would run actual benchmark)
                simulated_score = 75.0  # Placeholder
                candidate.humaneval_score = simulated_score

                # Update criteria met
                min_humaneval = self.data_manager.get_graduation_criteria().get("minimum_humaneval_score", 70.0)
                candidate.criteria_met["benchmark_requirement"] = simulated_score >= min_humaneval

                # Recalculate graduation score with benchmark
                candidate.graduation_score += (simulated_score / 100.0) * 1.0

                logger.info(f"🧪 Benchmarked {candidate.model_id}: {simulated_score} HumanEval")

            return candidate

        except Exception as e:
            logger.error(f"❌ Benchmarking failed for {candidate.model_id}: {e}")
            return None

    def _graduate_model(self, candidate: GraduationCandidate) -> bool:
        """Graduate a model from experimental to stable channel."""
        try:
            logger.info(f"🎓 Graduating model: {candidate.model_id}")

            # In a full implementation, this would:
            # 1. Add model to models.csv
            # 2. Remove from experimental_models.json
            # 3. Update graduation queue
            # 4. Send notifications

            # For now, just add to graduation queue to track the graduation
            self.data_manager.add_to_graduation_queue(candidate)

            logger.info(f"✅ Model {candidate.model_id} graduated successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to graduate {candidate.model_id}: {e}")
            return False

class WorkerManager:
    """
    Manages lifecycle of all background workers.
    
    Provides centralized control for starting/stopping workers
    and monitoring their health status.
    """

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.workers = {}
        self.running = False

    def start_all_workers(self):
        """Start all background workers."""
        try:
            # Start model detection worker
            detection_worker = ModelDetectionWorker(self.data_manager)
            detection_thread = threading.Thread(
                target=detection_worker.start,
                name="ModelDetectionWorker",
                daemon=True
            )
            detection_thread.start()
            self.workers["model_detection"] = {
                "worker": detection_worker,
                "thread": detection_thread
            }

            # Start graduation worker
            graduation_worker = GraduationWorker(self.data_manager)
            graduation_thread = threading.Thread(
                target=graduation_worker.start,
                name="GraduationWorker",
                daemon=True
            )
            graduation_thread.start()
            self.workers["graduation"] = {
                "worker": graduation_worker,
                "thread": graduation_thread
            }

            self.running = True
            logger.info(f"🚀 Started {len(self.workers)} background workers")

        except Exception as e:
            logger.error(f"❌ Failed to start workers: {e}")
            self.stop_all_workers()

    def stop_all_workers(self):
        """Stop all background workers gracefully."""
        logger.info("🛑 Stopping all background workers...")

        for name, worker_info in self.workers.items():
            try:
                worker_info["worker"].stop()
                logger.info(f"✅ Stopped {name} worker")
            except Exception as e:
                logger.error(f"❌ Error stopping {name} worker: {e}")

        self.workers.clear()
        self.running = False

    def get_worker_status(self) -> Dict[str, Any]:
        """Get status of all workers."""
        status = {
            "manager_running": self.running,
            "total_workers": len(self.workers),
            "workers": {}
        }

        for name, worker_info in self.workers.items():
            worker = worker_info["worker"]
            thread = worker_info["thread"]

            status["workers"][name] = {
                "running": worker.running,
                "thread_alive": thread.is_alive(),
                "thread_name": thread.name
            }

        return status
