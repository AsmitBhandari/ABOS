import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Evaluation:
    """Represents ABOS's assessment of an Execution."""

    execution_id: str
    task_id: str
    agent_id: str
    success: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    quality_score: Optional[float] = None
    correctness_score: Optional[float] = None
    latency_ms: float = 0.0
    feedback: Optional[str] = None
    error_type: Optional[str] = None
    evaluator: str = "system"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id or not str(self.id).strip():
            raise ValueError("Evaluation ID cannot be empty")
        if not self.execution_id or not str(self.execution_id).strip():
            raise ValueError("execution_id cannot be empty")
        if not self.task_id or not str(self.task_id).strip():
            raise ValueError("task_id cannot be empty")
        if not self.agent_id or not str(self.agent_id).strip():
            raise ValueError("agent_id cannot be empty")
        if self.quality_score is not None and not (0.0 <= self.quality_score <= 1.0):
            raise ValueError("quality_score must be between 0.0 and 1.0")
        if self.correctness_score is not None and not (0.0 <= self.correctness_score <= 1.0):
            raise ValueError("correctness_score must be between 0.0 and 1.0")
        if self.latency_ms < 0.0:
            raise ValueError("latency_ms cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Evaluation object to a dictionary."""
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "quality_score": self.quality_score,
            "correctness_score": self.correctness_score,
            "latency_ms": self.latency_ms,
            "feedback": self.feedback,
            "error_type": self.error_type,
            "evaluator": self.evaluator,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
