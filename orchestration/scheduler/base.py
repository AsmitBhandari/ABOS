from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.agent import BaseAgent
from core.agent_profile import AgentProfile
from core.task import Task


@dataclass
class CandidateScore:
    """Represents the scoring and evaluation details for a candidate Agent."""

    agent_id: str
    total_score: float = 0.0
    success_rate: float = 0.0
    latency_score: float = 0.0
    confidence_score: float = 0.0
    raw_latency_ms: float = 0.0
    eligible: bool = True
    rejection_reason: Optional[str] = None

    def __post_init__(self):
        if not self.agent_id or not str(self.agent_id).strip():
            raise ValueError("CandidateScore agent_id cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize CandidateScore to a dictionary."""
        return {
            "agent_id": self.agent_id,
            "total_score": round(self.total_score, 4),
            "success_rate": round(self.success_rate, 4),
            "latency_score": round(self.latency_score, 4),
            "confidence_score": round(self.confidence_score, 4),
            "raw_latency_ms": round(self.raw_latency_ms, 2),
            "eligible": self.eligible,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class SchedulingResult:
    """Represents the structured decision returned by a Scheduler."""

    task_id: str
    selected_agent_id: Optional[str]
    success: bool
    reason: str = ""
    score: float = 0.0
    candidates: List[CandidateScore] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.task_id or not str(self.task_id).strip():
            raise ValueError("SchedulingResult task_id cannot be empty")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("SchedulingResult score must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize SchedulingResult to a dictionary."""
        return {
            "task_id": self.task_id,
            "selected_agent_id": self.selected_agent_id,
            "success": self.success,
            "reason": self.reason,
            "score": round(self.score, 4),
            "candidates": [c.to_dict() for c in self.candidates],
            "metadata": self.metadata,
        }


class BaseScheduler(ABC):
    """Abstract base class for all ABOS schedulers."""

    @abstractmethod
    def schedule(
        self,
        task: Task,
        agents: List[BaseAgent],
        profiles: Optional[List[AgentProfile]] = None,
    ) -> SchedulingResult:
        """
        Evaluate candidate agents against task requirements and historical profiles,
        returning a structured SchedulingResult.
        """
        pass


# Canonical alias for BaseScheduler
Scheduler = BaseScheduler
