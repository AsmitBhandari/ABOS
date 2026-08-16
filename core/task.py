import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from core.result import Result


class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a unit of work within ABOS."""
    description: str
    input_data: Any
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Result] = None
