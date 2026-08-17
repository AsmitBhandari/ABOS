from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentProfile:
    """Represents historical quantitative performance information about an Agent."""

    agent_id: str
    total_executions: int = 0
    successful_executions: int = 0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    confidence_score: float = 0.5
    capabilities: List[str] = field(default_factory=list)
    last_execution_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.agent_id or not str(self.agent_id).strip():
            raise ValueError("agent_id cannot be empty")
        if self.total_executions < 0:
            raise ValueError("total_executions cannot be negative")
        if self.successful_executions < 0:
            raise ValueError("successful_executions cannot be negative")
        if self.successful_executions > self.total_executions:
            raise ValueError("successful_executions cannot exceed total_executions")
        if not (0.0 <= self.success_rate <= 1.0):
            raise ValueError("success_rate must be between 0.0 and 1.0")
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if self.avg_latency_ms < 0.0:
            raise ValueError("avg_latency_ms cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize AgentProfile object to a dictionary."""
        return {
            "agent_id": self.agent_id,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "confidence_score": self.confidence_score,
            "capabilities": self.capabilities,
            "last_execution_at": self.last_execution_at,
            "metadata": self.metadata,
        }
