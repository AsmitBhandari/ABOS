import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from core.result import Result


class ExecutionStatus(Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


@dataclass
class Execution:
    """Represents ONE attempt to execute ONE Task."""

    task_id: str
    agent_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ExecutionStatus = ExecutionStatus.RUNNING
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    result: Optional[Result] = None
    attempt_number: int = 1
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id or not str(self.id).strip():
            raise ValueError("Execution ID cannot be empty")
        if not self.task_id or not str(self.task_id).strip():
            raise ValueError("task_id cannot be empty")
        if not self.agent_id or not str(self.agent_id).strip():
            raise ValueError("agent_id cannot be empty")
        if self.attempt_number < 1:
            raise ValueError("attempt_number must be >= 1")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Execution object to a dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result.to_dict() if self.result else None,
            "attempt_number": self.attempt_number,
            "error": self.error,
            "metadata": self.metadata,
        }
