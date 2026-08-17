import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from core.result import Result


class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a unit of work within ABOS."""

    description: str
    input_data: Any = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: TaskPriority = TaskPriority.MEDIUM
    required_capabilities: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    child_task_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Result] = None

    def __post_init__(self):
        if not self.id or not str(self.id).strip():
            raise ValueError("Task ID cannot be empty")
        if self.parent_task_id is not None and str(self.parent_task_id) == str(self.id):
            raise ValueError("parent_task_id cannot equal task ID")
        if len(self.child_task_ids) != len(set(self.child_task_ids)):
            raise ValueError("child_task_ids cannot contain duplicates")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Task object to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "input_data": self.input_data,
            "priority": self.priority.name,
            "required_capabilities": self.required_capabilities,
            "status": self.status.value,
            "assigned_agent_id": self.assigned_agent_id,
            "parent_task_id": self.parent_task_id,
            "child_task_ids": self.child_task_ids,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "result": self.result.to_dict() if self.result else None,
        }
