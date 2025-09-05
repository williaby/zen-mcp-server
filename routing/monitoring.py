"""
Monitoring and Metrics Collection for Dynamic Model Routing

This module provides comprehensive monitoring, metrics collection, and
health checking capabilities for the model routing system.
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class RoutingEvent:
    """Individual routing event for tracking."""
    timestamp: float
    tool_name: str
    prompt_hash: str
    original_model: str
    selected_model: str
    routing_used: bool
    confidence: float
    complexity_level: str
    task_type: str
    estimated_cost: float
    actual_cost: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    response_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

@dataclass
class ModelPerformance:
    """Performance metrics for a specific model."""
    model_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    total_response_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    last_used: Optional[float] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests

    @property
    def average_cost(self) -> float:
        """Calculate average cost per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests

class RoutingMonitor:
    """
    Central monitoring system for model routing.
    
    Features:
    - Real-time event tracking
    - Performance metrics collection
    - Cost analysis and optimization tracking
    - Health monitoring and alerting
    - Historical data persistence
    """

    def __init__(self,
                 metrics_dir: str = "metrics",
                 max_events: int = 10000,
                 persist_interval: int = 300):  # 5 minutes
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)

        self.max_events = max_events
        self.persist_interval = persist_interval

        # Event storage
        self.events: deque[RoutingEvent] = deque(maxlen=max_events)
        self.model_performance: Dict[str, ModelPerformance] = {}

        # Aggregated metrics
        self.hourly_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.daily_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Threading for background tasks
        self._lock = threading.RLock()
        self._stop_background = threading.Event()
        self._background_thread: Optional[threading.Thread] = None

        # Health thresholds
        self.health_thresholds = {
            "min_success_rate": 0.85,
            "max_error_rate": 0.15,
            "max_avg_response_time": 2.0,  # seconds
            "min_free_model_usage": 0.3  # 30% of requests should use free models
        }

        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        self._background_thread = threading.Thread(
            target=self._background_worker,
            daemon=True,
            name="RoutingMonitor"
        )
        self._background_thread.start()

    def _background_worker(self):
        """Background worker for periodic tasks."""
        last_persist = time.time()
        last_cleanup = time.time()

        while not self._stop_background.wait(60):  # Check every minute
            current_time = time.time()

            try:
                # Persist metrics periodically
                if current_time - last_persist >= self.persist_interval:
                    self._persist_metrics()
                    last_persist = current_time

                # Cleanup old data hourly
                if current_time - last_cleanup >= 3600:  # 1 hour
                    self._cleanup_old_data()
                    last_cleanup = current_time

                # Update aggregated stats
                self._update_aggregated_stats()

            except Exception as e:
                logger.error(f"Error in routing monitor background task: {e}")

    def record_routing_event(self, event: RoutingEvent):
        """Record a routing event for monitoring."""
        with self._lock:
            self.events.append(event)

            # Update model performance
            model_name = event.selected_model
            if model_name not in self.model_performance:
                self.model_performance[model_name] = ModelPerformance(model_name)

            perf = self.model_performance[model_name]
            perf.total_requests += 1
            perf.last_used = event.timestamp
            perf.total_cost += event.actual_cost or event.estimated_cost

            if event.success:
                perf.successful_requests += 1
                perf.total_response_time += event.response_time
            else:
                perf.failed_requests += 1
                perf.error_count += 1
                perf.last_error = event.error_message

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current routing metrics."""
        with self._lock:
            now = time.time()
            hour_ago = now - 3600
            day_ago = now - 86400

            # Recent events
            recent_events = [e for e in self.events if e.timestamp > hour_ago]
            daily_events = [e for e in self.events if e.timestamp > day_ago]

            # Basic counts
            total_events = len(self.events)
            recent_count = len(recent_events)
            daily_count = len(daily_events)

            # Success rates
            recent_successes = sum(1 for e in recent_events if e.success)
            daily_successes = sum(1 for e in daily_events if e.success)

            # Cost metrics
            total_cost = sum(e.actual_cost or e.estimated_cost for e in daily_events)
            free_model_usage = sum(1 for e in daily_events if e.estimated_cost == 0)

            # Routing effectiveness
            routing_used_count = sum(1 for e in daily_events if e.routing_used)

            return {
                "timestamp": now,
                "total_events": total_events,
                "recent_activity": {
                    "last_hour": recent_count,
                    "last_24h": daily_count,
                    "success_rate_hour": recent_successes / recent_count if recent_count > 0 else 1.0,
                    "success_rate_day": daily_successes / daily_count if daily_count > 0 else 1.0
                },
                "cost_metrics": {
                    "total_cost_24h": total_cost,
                    "free_model_usage": free_model_usage,
                    "free_model_rate": free_model_usage / daily_count if daily_count > 0 else 0.0
                },
                "routing_effectiveness": {
                    "routing_used_count": routing_used_count,
                    "routing_used_rate": routing_used_count / daily_count if daily_count > 0 else 0.0
                },
                "model_performance": {
                    name: {
                        "success_rate": perf.success_rate,
                        "avg_response_time": perf.average_response_time,
                        "avg_cost": perf.average_cost,
                        "total_requests": perf.total_requests,
                        "last_error": perf.last_error
                    }
                    for name, perf in self.model_performance.items()
                }
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status based on metrics."""
        metrics = self.get_current_metrics()
        health_checks = {}
        overall_healthy = True

        # Check success rate
        success_rate = metrics["recent_activity"]["success_rate_day"]
        health_checks["success_rate"] = {
            "healthy": success_rate >= self.health_thresholds["min_success_rate"],
            "value": success_rate,
            "threshold": self.health_thresholds["min_success_rate"],
            "message": f"Success rate: {success_rate:.1%}"
        }

        # Check free model usage
        free_rate = metrics["cost_metrics"]["free_model_rate"]
        health_checks["cost_optimization"] = {
            "healthy": free_rate >= self.health_thresholds["min_free_model_usage"],
            "value": free_rate,
            "threshold": self.health_thresholds["min_free_model_usage"],
            "message": f"Free model usage: {free_rate:.1%}"
        }

        # Check model performance
        unhealthy_models = []
        for name, perf in metrics["model_performance"].items():
            if perf["success_rate"] < self.health_thresholds["min_success_rate"]:
                unhealthy_models.append(name)

        health_checks["model_performance"] = {
            "healthy": len(unhealthy_models) == 0,
            "value": len(unhealthy_models),
            "message": f"Unhealthy models: {unhealthy_models}" if unhealthy_models else "All models performing well"
        }

        # Overall health
        overall_healthy = all(check["healthy"] for check in health_checks.values())

        return {
            "overall_healthy": overall_healthy,
            "timestamp": time.time(),
            "checks": health_checks,
            "summary": "System healthy" if overall_healthy else "Issues detected"
        }

    def get_cost_analysis(self) -> Dict[str, Any]:
        """Get detailed cost analysis."""
        with self._lock:
            now = time.time()
            day_ago = now - 86400
            week_ago = now - 604800

            daily_events = [e for e in self.events if e.timestamp > day_ago]
            weekly_events = [e for e in self.events if e.timestamp > week_ago]

            # Daily costs
            daily_free = sum(1 for e in daily_events if e.estimated_cost == 0)
            daily_paid = len(daily_events) - daily_free
            daily_cost = sum(e.actual_cost or e.estimated_cost for e in daily_events)

            # Weekly costs
            weekly_free = sum(1 for e in weekly_events if e.estimated_cost == 0)
            weekly_paid = len(weekly_events) - weekly_free
            weekly_cost = sum(e.actual_cost or e.estimated_cost for e in weekly_events)

            # Cost by tool
            tool_costs = defaultdict(float)
            for event in daily_events:
                tool_costs[event.tool_name] += event.actual_cost or event.estimated_cost

            # Cost by model
            model_costs = defaultdict(float)
            for event in daily_events:
                model_costs[event.selected_model] += event.actual_cost or event.estimated_cost

            return {
                "daily_analysis": {
                    "total_requests": len(daily_events),
                    "free_requests": daily_free,
                    "paid_requests": daily_paid,
                    "total_cost": daily_cost,
                    "cost_per_request": daily_cost / len(daily_events) if daily_events else 0
                },
                "weekly_analysis": {
                    "total_requests": len(weekly_events),
                    "free_requests": weekly_free,
                    "paid_requests": weekly_paid,
                    "total_cost": weekly_cost,
                    "cost_per_request": weekly_cost / len(weekly_events) if weekly_events else 0
                },
                "cost_by_tool": dict(tool_costs),
                "cost_by_model": dict(model_costs),
                "optimization_opportunities": self._identify_cost_optimizations()
            }

    def _identify_cost_optimizations(self) -> List[str]:
        """Identify potential cost optimization opportunities."""
        opportunities = []

        with self._lock:
            now = time.time()
            day_ago = now - 86400
            daily_events = [e for e in self.events if e.timestamp > day_ago]

            if not daily_events:
                return opportunities

            # Check for overuse of expensive models on simple tasks
            simple_tasks_expensive = [
                e for e in daily_events
                if e.complexity_level == "simple" and e.estimated_cost > 0.001
            ]

            if simple_tasks_expensive:
                opportunities.append(
                    f"Found {len(simple_tasks_expensive)} simple tasks using expensive models"
                )

            # Check for low free model usage
            free_usage = sum(1 for e in daily_events if e.estimated_cost == 0)
            free_rate = free_usage / len(daily_events)

            if free_rate < 0.5:
                opportunities.append(
                    f"Free model usage is only {free_rate:.1%} - consider prioritizing free models"
                )

            # Check for failed expensive model usage
            expensive_failures = [
                e for e in daily_events
                if not e.success and e.estimated_cost > 0.01
            ]

            if expensive_failures:
                opportunities.append(
                    f"Found {len(expensive_failures)} expensive model failures - consider fallback strategy"
                )

        return opportunities

    def _update_aggregated_stats(self):
        """Update hourly and daily aggregated statistics."""
        with self._lock:
            now = datetime.now()
            current_hour = now.strftime("%Y-%m-%d-%H")
            current_day = now.strftime("%Y-%m-%d")

            # Get events for current hour and day
            hour_start = now.replace(minute=0, second=0, microsecond=0).timestamp()
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

            hour_events = [e for e in self.events if e.timestamp >= hour_start]
            day_events = [e for e in self.events if e.timestamp >= day_start]

            # Update hourly stats
            if hour_events:
                self.hourly_stats[current_hour] = self._calculate_period_stats(hour_events)

            # Update daily stats
            if day_events:
                self.daily_stats[current_day] = self._calculate_period_stats(day_events)

    def _calculate_period_stats(self, events: List[RoutingEvent]) -> Dict[str, Any]:
        """Calculate statistics for a period of events."""
        if not events:
            return {}

        total_events = len(events)
        successful_events = sum(1 for e in events if e.success)
        free_model_events = sum(1 for e in events if e.estimated_cost == 0)
        routing_used_events = sum(1 for e in events if e.routing_used)

        total_cost = sum(e.actual_cost or e.estimated_cost for e in events)
        avg_confidence = sum(e.confidence for e in events) / total_events
        avg_response_time = sum(e.response_time for e in events) / total_events

        # Tool distribution
        tool_counts = defaultdict(int)
        for event in events:
            tool_counts[event.tool_name] += 1

        # Complexity distribution
        complexity_counts = defaultdict(int)
        for event in events:
            complexity_counts[event.complexity_level] += 1

        return {
            "total_events": total_events,
            "success_rate": successful_events / total_events,
            "free_model_rate": free_model_events / total_events,
            "routing_used_rate": routing_used_events / total_events,
            "total_cost": total_cost,
            "avg_cost_per_request": total_cost / total_events,
            "avg_confidence": avg_confidence,
            "avg_response_time": avg_response_time,
            "tool_distribution": dict(tool_counts),
            "complexity_distribution": dict(complexity_counts)
        }

    def _persist_metrics(self):
        """Persist current metrics to disk."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save current metrics
            metrics_file = self.metrics_dir / f"metrics_{timestamp}.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.get_current_metrics(), f, indent=2)

            # Save health status
            health_file = self.metrics_dir / f"health_{timestamp}.json"
            with open(health_file, 'w') as f:
                json.dump(self.get_health_status(), f, indent=2)

            # Save cost analysis
            cost_file = self.metrics_dir / f"cost_{timestamp}.json"
            with open(cost_file, 'w') as f:
                json.dump(self.get_cost_analysis(), f, indent=2)

            logger.debug(f"Persisted routing metrics to {self.metrics_dir}")

        except Exception as e:
            logger.error(f"Failed to persist routing metrics: {e}")

    def _cleanup_old_data(self):
        """Clean up old metrics files."""
        try:
            # Keep metrics files for 7 days
            cutoff = time.time() - (7 * 24 * 3600)

            for file_path in self.metrics_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff:
                    file_path.unlink()
                    logger.debug(f"Deleted old metrics file: {file_path}")

            # Clean up old hourly stats (keep 48 hours)
            hours_to_keep = 48
            cutoff_hour = datetime.now() - timedelta(hours=hours_to_keep)
            cutoff_hour_str = cutoff_hour.strftime("%Y-%m-%d-%H")

            old_hours = [
                hour for hour in self.hourly_stats.keys()
                if hour < cutoff_hour_str
            ]

            for hour in old_hours:
                del self.hourly_stats[hour]

            # Clean up old daily stats (keep 30 days)
            days_to_keep = 30
            cutoff_day = datetime.now() - timedelta(days=days_to_keep)
            cutoff_day_str = cutoff_day.strftime("%Y-%m-%d")

            old_days = [
                day for day in self.daily_stats.keys()
                if day < cutoff_day_str
            ]

            for day in old_days:
                del self.daily_stats[day]

        except Exception as e:
            logger.error(f"Failed to cleanup old routing data: {e}")

    def export_metrics(self,
                      format: str = "json",
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None) -> Dict[str, Any]:
        """Export metrics data for analysis."""
        with self._lock:
            # Filter events by time range
            events = list(self.events)
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]

            export_data = {
                "metadata": {
                    "export_time": time.time(),
                    "start_time": start_time,
                    "end_time": end_time,
                    "event_count": len(events),
                    "format": format
                },
                "events": [e.to_dict() for e in events],
                "model_performance": {
                    name: asdict(perf)
                    for name, perf in self.model_performance.items()
                },
                "aggregated_stats": {
                    "hourly": dict(self.hourly_stats),
                    "daily": dict(self.daily_stats)
                }
            }

            return export_data

    def shutdown(self):
        """Shutdown the monitoring system."""
        self._stop_background.set()
        if self._background_thread:
            self._background_thread.join(timeout=5)

        # Final persist
        self._persist_metrics()
        logger.info("Routing monitor shutdown complete")


# Global monitor instance
_global_monitor: Optional[RoutingMonitor] = None

def get_global_monitor() -> RoutingMonitor:
    """Get the global routing monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RoutingMonitor()
    return _global_monitor

def record_routing_event(**kwargs):
    """Convenience function to record a routing event."""
    event = RoutingEvent(**kwargs)
    monitor = get_global_monitor()
    monitor.record_routing_event(event)
