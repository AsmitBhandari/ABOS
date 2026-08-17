from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from core.task import Task


@dataclass
class PlanningResult:
    """Represents the structured decision returned by a Planner."""

    task_id: str
    should_decompose: bool
    subtasks: List[Task] = field(default_factory=list)
    reason: str = ""
    confidence: float = 1.0
    valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.task_id or not str(self.task_id).strip():
            raise ValueError("PlanningResult task_id cannot be empty")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize PlanningResult to a dictionary."""
        return {
            "task_id": self.task_id,
            "should_decompose": self.should_decompose,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "reason": self.reason,
            "confidence": self.confidence,
            "valid": self.valid,
            "metadata": self.metadata,
        }


class BasePlanner(ABC):
    """Abstract base class for all ABOS planners."""

    @abstractmethod
    def plan(self, task: Task) -> PlanningResult:
        """
        Assess task and determine whether decomposition is required.
        Returns a structured PlanningResult.
        """
        pass


# Canonical alias for BasePlanner
Planner = BasePlanner
