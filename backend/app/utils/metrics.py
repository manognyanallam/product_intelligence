"""
Performance metrics tracking for the AI Product Intelligence Platform.

Tracks:
- Response times per endpoint
- Agent processing times
- Cache hit rates
- Error rates
- Gemini API call counts
"""
import time
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict


class MetricsTracker:
    """
    Simple metrics tracker for monitoring application performance.
    
    In production, this would be replaced with a proper monitoring
    solution (Prometheus, DataDog, etc.).
    """
    
    def __init__(self):
        """Initialize metrics storage."""
        self._metrics = defaultdict(list)
        self._counters = defaultdict(int)
        self._start_time = datetime.utcnow()
    
    def track_request(self, endpoint: str, duration_ms: int, status_code: int):
        """
        Track an API request.
        
        Args:
            endpoint: The API endpoint called
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
        """
        self._metrics[f"request.{endpoint}"].append({
            "duration_ms": duration_ms,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._counters[f"requests.{endpoint}"] += 1
    
    def track_agent(self, agent: str, duration_ms: int, success: bool):
        """
        Track an agent execution.
        
        Args:
            agent: Agent name
            duration_ms: Agent execution duration
            success: Whether the agent succeeded
        """
        self._metrics[f"agent.{agent}"].append({
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._counters[f"agent_runs.{agent}"] += 1
    
    def track_cache_hit(self, collection: str):
        """Track a cache hit."""
        self._counters[f"cache_hit.{collection}"] += 1
    
    def track_cache_miss(self, collection: str):
        """Track a cache miss."""
        self._counters[f"cache_miss.{collection}"] += 1
    
    def track_gemini_call(self, model: str, tokens: int):
        """Track a Gemini API call."""
        self._metrics["gemini.calls"].append({
            "model": model,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._counters["gemini.total_calls"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all tracked metrics."""
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self._counters.get(k, 0) for k in self._counters if k.startswith("requests.")),
            "total_agent_runs": sum(self._counters.get(k, 0) for k in self._counters if k.startswith("agent_runs.")),
            "gemini_calls": self._counters.get("gemini.total_calls", 0),
            "counters": dict(self._counters),
        }


# Global metrics tracker instance
metrics = MetricsTracker()
