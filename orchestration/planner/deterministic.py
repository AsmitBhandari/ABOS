import re
from typing import List, Optional
from core.task import Task
from orchestration.planner.base import BasePlanner, PlanningResult
from orchestration.planner.validator import DecompositionValidator


class DeterministicPlanner(BasePlanner):
    """
    Deterministic rule-based planner for task decomposition.
    Analyzes task descriptions for explicit multi-step sequences.
    """

    def __init__(self, validator: Optional[DecompositionValidator] = None):
        self.validator = validator or DecompositionValidator()

    def _extract_steps(self, text: str) -> List[str]:
        """Extract sequential subtask descriptions from text if explicit multi-step patterns exist."""
        cleaned = text.strip()
        if not cleaned:
            return []

        # 1. Numbered lists (e.g. '1. Step one\n2. Step two' or '1) Step one 2) Step two')
        numbered_pattern = r'(?:^|\n|\s+)(?:\d+[\.\)]|Step\s+\d+:?)\s+([^\n\d]+?)(?=(?:\n|\s+)(?:\d+[\.\)]|Step\s+\d+:?)|$)'
        numbered_matches = re.findall(numbered_pattern, cleaned, flags=re.IGNORECASE)
        if len(numbered_matches) >= 2:
            steps = [m.strip().rstrip(".,;") for m in numbered_matches if m.strip()]
            if len(steps) >= 2:
                return steps

        # 2. Semicolon or newline-separated lists
        if "\n" in cleaned or ";" in cleaned:
            delimiter = "\n" if "\n" in cleaned else ";"
            raw_parts = [p.strip().rstrip(".,") for p in cleaned.split(delimiter)]
            parts = [re.sub(r'^[-*•]\s*', '', p).strip() for p in raw_parts if p.strip()]
            if len(parts) >= 2:
                return parts

        # 3. Explicit sequential connectives: ' then ', ' and then ', ' followed by '
        seq_pattern = r'\s+(?:and\s+then|then|followed\s+by)\s+'
        if re.search(seq_pattern, cleaned, flags=re.IGNORECASE):
            parts = [p.strip().rstrip(".,") for p in re.split(seq_pattern, cleaned, flags=re.IGNORECASE) if p.strip()]
            if len(parts) >= 2:
                return parts

        # 4. Oxford comma / conjunction lists: "A, B, and C" or "A, and B"
        if ", and " in cleaned.lower() or ", & " in cleaned:
            raw_segments = cleaned.split(",")
            if len(raw_segments) >= 2:
                steps = []
                for seg in raw_segments:
                    s = seg.strip()
                    if s.lower().startswith("and "):
                        s = s[4:].strip()
                    elif s.startswith("& "):
                        s = s[2:].strip()
                    s = s.rstrip(".,")
                    if s:
                        steps.append(s)
                if len(steps) >= 2:
                    return steps

        return []

    def plan(self, task: Task) -> PlanningResult:
        """
        Assess task description/input_data and generate subtasks if multi-step structure exists.
        """
        text_to_analyze = task.description or ""
        if isinstance(task.input_data, str) and len(task.input_data) > len(text_to_analyze):
            extracted_from_input = self._extract_steps(task.input_data)
            if extracted_from_input:
                raw_steps = extracted_from_input
            else:
                raw_steps = self._extract_steps(text_to_analyze)
        else:
            raw_steps = self._extract_steps(text_to_analyze)

        if not raw_steps or len(raw_steps) < 2:
            return PlanningResult(
                task_id=task.id,
                should_decompose=False,
                subtasks=[],
                reason="Task is atomic; decomposition not required.",
                confidence=1.0,
                valid=True,
                metadata={"strategy": "deterministic"},
            )

        # Generate child subtasks
        subtasks: List[Task] = []
        for step_desc in raw_steps:
            child_task = Task(
                description=step_desc,
                input_data=None,
                priority=task.priority,
                parent_task_id=task.id,
                required_capabilities=[],
                assigned_agent_id=None,
            )
            subtasks.append(child_task)

        # Attach child IDs to parent task
        task.child_task_ids = [child.id for child in subtasks]

        # Validate decomposition
        is_valid, validation_errors = self.validator.validate(task, subtasks)
        if not is_valid:
            return PlanningResult(
                task_id=task.id,
                should_decompose=True,
                subtasks=[],
                reason=f"Decomposition validation failed: {'; '.join(validation_errors)}",
                confidence=0.0,
                valid=False,
                metadata={"errors": validation_errors, "strategy": "deterministic"},
            )

        return PlanningResult(
            task_id=task.id,
            should_decompose=True,
            subtasks=subtasks,
            reason=f"Decomposed task into {len(subtasks)} sequential subtasks.",
            confidence=1.0,
            valid=True,
            metadata={"strategy": "deterministic", "subtask_count": len(subtasks)},
        )
