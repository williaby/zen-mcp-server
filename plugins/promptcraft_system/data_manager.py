"""
Data Management for PromptCraft System

Handles persistence and management of experimental models, graduation queue,
performance metrics, and channel configuration data.
"""

import json
import logging
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ModelChannel(Enum):
    STABLE = "stable"
    EXPERIMENTAL = "experimental"

@dataclass
class ExperimentalModel:
    """Data structure for experimental models."""
    id: str
    name: str
    provider: str
    cost_per_token: float
    context_window: int
    added_date: str
    usage_count: int = 0
    success_rate: float = 0.0
    humaneval_score: Optional[float] = None
    last_used: Optional[str] = None
    graduation_eligible: bool = False

@dataclass
class GraduationCandidate:
    """Data structure for models in graduation queue."""
    model_id: str
    added_to_queue: str
    usage_count: int
    success_rate: float
    humaneval_score: Optional[float]
    days_in_experimental: int
    graduation_score: float
    criteria_met: Dict[str, bool]

class PromptCraftDataManager:
    """
    Manages all data persistence for the PromptCraft system.
    
    Handles:
    - Experimental models storage and retrieval
    - Graduation queue management  
    - Performance metrics tracking
    - Channel configuration management
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            self.data_dir = Path("data/promptcraft")
        else:
            self.data_dir = Path(data_dir) if isinstance(data_dir, str) else data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.experimental_models_path = self.data_dir / "experimental_models.json"
        self.graduation_queue_path = self.data_dir / "graduation_queue.json"
        self.performance_metrics_path = self.data_dir / "performance_metrics.json"
        self.channel_config_path = self.data_dir / "channel_config.json"

        # Thread lock for concurrent access
        self._lock = threading.Lock()

        # Initialize files if they don't exist
        self._initialize_data_files()

    def _initialize_data_files(self):
        """Initialize data files with default structures if they don't exist."""
        default_files = {
            self.experimental_models_path: [],
            self.graduation_queue_path: [],
            self.performance_metrics_path: {
                "model_performance": {},
                "api_metrics": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "average_response_time": 0.0,
                    "last_updated": datetime.now().isoformat()
                }
            },
            self.channel_config_path: {
                "graduation_criteria": {
                    "minimum_age_days": 7,
                    "minimum_usage_requests": 50,
                    "minimum_success_rate": 0.95,
                    "minimum_humaneval_score": 70.0
                },
                "detection_config": {
                    "check_interval_hours": 6,
                    "quality_filters": {
                        "min_context_window": 4000,
                        "exclude_providers": ["experimental", "test"]
                    }
                },
                "last_updated": datetime.now().isoformat()
            }
        }

        for file_path, default_content in default_files.items():
            if not file_path.exists():
                try:
                    with open(file_path, 'w') as f:
                        json.dump(default_content, f, indent=2)
                    logger.info(f"✅ Initialized {file_path.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {file_path.name}: {e}")

    def get_experimental_models(self) -> List[ExperimentalModel]:
        """Get all experimental models."""
        with self._lock:
            try:
                with open(self.experimental_models_path) as f:
                    data = json.load(f)
                return [ExperimentalModel(**model) for model in data]
            except Exception as e:
                logger.error(f"Error loading experimental models: {e}")
                return []

    def add_experimental_model(self, model: ExperimentalModel) -> bool:
        """Add a new experimental model."""
        with self._lock:
            try:
                models = self.get_experimental_models()

                # Check if model already exists
                if any(m.id == model.id for m in models):
                    logger.warning(f"Model {model.id} already exists in experimental channel")
                    return False

                # Add new model
                models.append(model)

                # Save to file
                with open(self.experimental_models_path, 'w') as f:
                    json.dump([asdict(m) for m in models], f, indent=2)

                logger.info(f"✅ Added experimental model: {model.id}")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to add experimental model {model.id}: {e}")
                return False

    def update_model_usage(self, model_id: str, success: bool) -> bool:
        """Update usage statistics for a model."""
        with self._lock:
            try:
                models = self.get_experimental_models()

                for model in models:
                    if model.id == model_id:
                        model.usage_count += 1
                        model.last_used = datetime.now().isoformat()

                        # Update success rate
                        if model.usage_count == 1:
                            model.success_rate = 1.0 if success else 0.0
                        else:
                            # Calculate running average
                            old_total = model.success_rate * (model.usage_count - 1)
                            new_total = old_total + (1.0 if success else 0.0)
                            model.success_rate = new_total / model.usage_count

                        break

                # Save updated models
                with open(self.experimental_models_path, 'w') as f:
                    json.dump([asdict(m) for m in models], f, indent=2)

                return True

            except Exception as e:
                logger.error(f"❌ Failed to update model usage for {model_id}: {e}")
                return False

    def get_graduation_queue(self) -> List[GraduationCandidate]:
        """Get all models in graduation queue."""
        with self._lock:
            try:
                with open(self.graduation_queue_path) as f:
                    data = json.load(f)
                return [GraduationCandidate(**candidate) for candidate in data]
            except Exception as e:
                logger.error(f"Error loading graduation queue: {e}")
                return []

    def add_to_graduation_queue(self, candidate: GraduationCandidate) -> bool:
        """Add a model to graduation queue."""
        with self._lock:
            try:
                queue = self.get_graduation_queue()

                # Check if already in queue
                if any(c.model_id == candidate.model_id for c in queue):
                    logger.info(f"Model {candidate.model_id} already in graduation queue")
                    return False

                queue.append(candidate)

                with open(self.graduation_queue_path, 'w') as f:
                    json.dump([asdict(c) for c in queue], f, indent=2)

                logger.info(f"✅ Added {candidate.model_id} to graduation queue")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to add {candidate.model_id} to graduation queue: {e}")
                return False

    def remove_from_graduation_queue(self, model_id: str) -> bool:
        """Remove a model from graduation queue (after graduation)."""
        with self._lock:
            try:
                queue = self.get_graduation_queue()
                original_length = len(queue)

                queue = [c for c in queue if c.model_id != model_id]

                if len(queue) < original_length:
                    with open(self.graduation_queue_path, 'w') as f:
                        json.dump([asdict(c) for c in queue], f, indent=2)
                    logger.info(f"✅ Removed {model_id} from graduation queue")
                    return True
                else:
                    logger.warning(f"Model {model_id} not found in graduation queue")
                    return False

            except Exception as e:
                logger.error(f"❌ Failed to remove {model_id} from graduation queue: {e}")
                return False

    def get_graduation_criteria(self) -> Dict[str, Any]:
        """Get current graduation criteria configuration."""
        try:
            with open(self.channel_config_path) as f:
                config = json.load(f)
            return config.get("graduation_criteria", {})
        except Exception as e:
            logger.error(f"Error loading graduation criteria: {e}")
            return {}

    def update_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Update system performance metrics."""
        with self._lock:
            try:
                with open(self.performance_metrics_path) as f:
                    current_metrics = json.load(f)

                # Update metrics
                current_metrics.update(metrics)
                current_metrics["last_updated"] = datetime.now().isoformat()

                with open(self.performance_metrics_path, 'w') as f:
                    json.dump(current_metrics, f, indent=2)

                return True

            except Exception as e:
                logger.error(f"❌ Failed to update performance metrics: {e}")
                return False

    def get_models_by_channel(self, channel: ModelChannel) -> List[Dict[str, Any]]:
        """Get models filtered by channel (stable or experimental)."""
        if channel == ModelChannel.STABLE:
            # Load from stable models.csv
            try:
                import pandas as pd
                models_csv_path = Path("docs/models/models.csv")
                if models_csv_path.exists():
                    df = pd.read_csv(models_csv_path)
                    return df.to_dict('records')
                else:
                    logger.debug("models.csv not found, returning empty list")
                    return []
            except ImportError:
                logger.debug("pandas not available, returning empty list for stable models")
                return []
            except Exception as e:
                logger.debug(f"Error loading stable models: {e}")
                return []

        elif channel == ModelChannel.EXPERIMENTAL:
            experimental_models = self.get_experimental_models()
            return [asdict(m) for m in experimental_models]

        return []

    def health_check(self) -> bool:
        """Check if data manager is healthy and all files are accessible."""
        try:
            # Check if all required files exist and are readable
            required_files = [
                self.experimental_models_path,
                self.graduation_queue_path,
                self.performance_metrics_path,
                self.channel_config_path
            ]

            for file_path in required_files:
                if not file_path.exists():
                    logger.error(f"Required file missing: {file_path}")
                    return False

                # Try to read each file
                with open(file_path) as f:
                    json.load(f)

            return True

        except Exception as e:
            logger.error(f"Data manager health check failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics for the PromptCraft system."""
        try:
            experimental_models = self.get_experimental_models()
            graduation_queue = self.get_graduation_queue()

            with open(self.performance_metrics_path) as f:
                performance_data = json.load(f)

            stats = {
                "experimental_models": len(experimental_models),
                "graduation_queue": len(graduation_queue),
                "total_experimental_usage": sum(m.usage_count for m in experimental_models),
                "average_success_rate": sum(m.success_rate for m in experimental_models) / len(experimental_models) if experimental_models else 0.0,
                "models_ready_for_graduation": len([m for m in experimental_models if m.graduation_eligible]),
                "api_metrics": performance_data.get("api_metrics", {}),
                "last_updated": datetime.now().isoformat()
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to generate stats: {e}")
            return {"error": str(e)}
