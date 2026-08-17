import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from core.result import Result
from core.task import Task


class AgentState(Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    ERROR = "ERROR"
    TERMINATED = "TERMINATED"


class BaseAgent(ABC):
    """Abstract Base Class for all ABOS agents."""

    def __init__(self, name: str, capabilities: List[str], agent_id: Optional[str] = None):
        self.id: str = agent_id or str(uuid.uuid4())
        if not self.id or not str(self.id).strip():
            raise ValueError("Agent ID cannot be empty")
        self.name: str = name
        self.capabilities: List[str] = capabilities or []
        self.state: AgentState = AgentState.IDLE

    @abstractmethod
    def execute(self, task: Task) -> Result:
        """Execute the assigned task and return a structured Result."""
        pass
