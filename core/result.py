from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Result:
    """Structured outcome of a task execution."""

    success: bool
    output: Any = None
    error: Optional[str] = None
    agent_id: str = ""
    execution_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Result object to a dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "agent_id": self.agent_id,
            "execution_id": self.execution_id,
            "metadata": self.metadata,
        }
