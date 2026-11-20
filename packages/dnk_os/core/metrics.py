# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/metrics.py"
# purpose: "Metrics collector for DNK OS tracking request counts, latencies, errors, task execution, and agent utilization"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Metrics collector for DNK OS."""

from typing import Dict, Any, List
from datetime import datetime, timezone
import time
from collections import defaultdict


class MetricsCollector:
    """
    Metrics collector for DNK OS.
    
    Collects:
    - Request count
    - Request latency
    - Error rate
    - Task execution time
    - Agent utilization
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.request_count: int = 0
        self.request_latencies: List[float] = []
        self.error_count: int = 0
        self.task_execution_times: List[float] = []
        self.agent_utilization: Dict[str, float] = defaultdict(float)
        self.start_time: float = time.time()
    
    def record_request(self, latency_ms: float):
        """
        Record request metrics.
        
        Args:
            latency_ms: Request latency in milliseconds
        """
        self.request_count += 1
        self.request_latencies.append(latency_ms)
    
    def record_error(self):
        """Record error occurrence."""
        self.error_count += 1
    
    def record_task_execution(self, execution_time_ms: float):
        """
        Record task execution metrics.
        
        Args:
            execution_time_ms: Task execution time in milliseconds
        """
        self.task_execution_times.append(execution_time_ms)
    
    def record_agent_utilization(self, agent_name: str, utilization: float):
        """
        Record agent utilization.
        
        Args:
            agent_name: Agent name
            utilization: Utilization percentage (0-100)
        """
        self.agent_utilization[agent_name] = utilization
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.
        
        Returns:
            Metrics dict
        """
        avg_latency = sum(self.request_latencies) / len(self.request_latencies) if self.request_latencies else 0.0
        avg_task_time = sum(self.task_execution_times) / len(self.task_execution_times) if self.task_execution_times else 0.0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0.0
        uptime_seconds = time.time() - self.start_time
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "avg_task_execution_time_ms": avg_task_time,
            "agent_utilization": dict(self.agent_utilization),
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.request_count = 0
        self.request_latencies = []
        self.error_count = 0
        self.task_execution_times = []
        self.agent_utilization = defaultdict(float)
        self.start_time = time.time()
