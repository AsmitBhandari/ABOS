from typing import Any, Dict, Optional
from core.agent import AgentState, BaseAgent
from core.result import Result
from core.task import Task


class TextAnalysisAgent(BaseAgent):
    """
    Agent capable of performing deterministic text analysis operations (such as word counting).
    Inherits from BaseAgent and exposes the 'text_analysis' capability.
    """

    def __init__(self, agent_id: str = "agent-text-analysis-01", name: str = "TextAnalysisAgent"):
        super().__init__(
            name=name,
            capabilities=["text_analysis"],
            agent_id=agent_id,
        )

    def execute(self, task: Task) -> Result:
        """
        Execute text analysis (word count) on the provided task input.
        """
        raw_input = task.input_data
        text_to_analyze: Optional[str] = None

        if raw_input is not None:
            if isinstance(raw_input, str):
                text_to_analyze = raw_input
            elif isinstance(raw_input, dict) and "text" in raw_input:
                val = raw_input["text"]
                if isinstance(val, str):
                    text_to_analyze = val
                elif val is not None:
                    text_to_analyze = str(val)
                else:
                    text_to_analyze = ""
            elif isinstance(raw_input, (int, float)):
                text_to_analyze = str(raw_input)
            else:
                return Result(
                    success=False,
                    output=None,
                    error=f"Invalid input type: expected string or dict with 'text', got {type(raw_input).__name__}",
                    agent_id=self.id,
                )
        else:
            # Fallback to task description if input_data is not provided
            text_to_analyze = task.description or ""

        try:
            # Clean and count words
            cleaned = text_to_analyze.strip()
            if not cleaned:
                word_count = 0
            else:
                words = cleaned.split()
                word_count = len(words)

            return Result(
                success=True,
                output=word_count,
                agent_id=self.id,
                metadata={
                    "operation": "word_count",
                    "char_count": len(cleaned),
                    "word_count": word_count,
                },
            )
        except Exception as e:
            return Result(
                success=False,
                output=None,
                error=f"Text analysis error: {str(e)}",
                agent_id=self.id,
            )
