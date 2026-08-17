from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Provisional minimal contract for external tool capabilities."""

    def __init__(self, name: str, description: str, input_schema: Optional[Dict[str, Any]] = None):
        if not name or not str(name).strip():
            raise ValueError("Tool name cannot be empty")
        self.name: str = name
        self.description: str = description
        self.input_schema: Dict[str, Any] = input_schema or {}

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute tool capability with provided keyword arguments."""
        pass
