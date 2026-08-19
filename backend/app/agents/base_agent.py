"""
Base Agent — Abstract base class for all agents in the multi-agent system.

All agents inherit from this class and implement the `run` method.
The base class provides common functionality like logging, error handling,
and configuration access.

Reference: architecture_final.md §5.2 (§5.4) (Agent Specifications)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Each agent has a single responsibility and communicates via shared context.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            agent_name: Human-readable name for the agent
            config: Optional configuration dictionary
        """
        self.agent_name = agent_name
        self.config = config or {}
        logger.info(f"Initialized agent: {agent_name}")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        Execute the agent's primary task.
        
        This method must be implemented by all subclasses.
        
        Returns:
            The agent's output (specific to each agent type)
        """
        pass
    
    def log_start(self, task: str):
        """Log the start of an agent task."""
        logger.info(f"[{self.agent_name}] Starting: {task} at {datetime.utcnow().isoformat()}")
    
    def log_complete(self, task: str, duration_ms: int):
        """Log the completion of an agent task."""
        logger.info(f"[{self.agent_name}] Completed: {task} in {duration_ms}ms")
    
    def log_error(self, task: str, error: Exception):
        """Log an error during an agent task."""
        logger.error(f"[{self.agent_name}] Error in {task}: {str(error)}")
