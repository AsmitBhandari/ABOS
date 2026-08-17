from typing import List, Tuple
from core.task import Task


class DecompositionValidator:
    """Lightweight validator for task decompositions."""

    @staticmethod
    def validate(parent_task: Task, subtasks: List[Task]) -> Tuple[bool, List[str]]:
        """
        Validates the parent-child relationship and integrity of generated subtasks.
        Returns (is_valid, list_of_error_messages).
        """
        errors: List[str] = []

        if not subtasks:
            errors.append("Decomposition must produce at least one subtask.")
            return False, errors

        child_ids = [child.id for child in subtasks]
        if len(child_ids) != len(set(child_ids)):
            errors.append("Child task IDs must be unique.")

        for idx, child in enumerate(subtasks):
            if not child.id or not str(child.id).strip():
                errors.append(f"Subtask at index {idx} has an empty ID.")
            if child.id == parent_task.id:
                errors.append(f"Subtask ID '{child.id}' cannot be identical to parent task ID.")
            if child.parent_task_id != parent_task.id:
                errors.append(
                    f"Subtask '{child.id}' parent_task_id '{child.parent_task_id}' does not match parent ID '{parent_task.id}'."
                )
            if not child.description or not str(child.description).strip():
                errors.append(f"Subtask '{child.id}' description cannot be empty.")
            if child.assigned_agent_id is not None:
                errors.append(
                    f"Subtask '{child.id}' must not have assigned_agent_id set by Planner."
                )

        # Check if parent_task.child_task_ids matches generated subtask IDs
        if set(parent_task.child_task_ids) != set(child_ids):
            errors.append(
                f"Parent child_task_ids {parent_task.child_task_ids} does not match generated subtasks {child_ids}."
            )

        is_valid = len(errors) == 0
        return is_valid, errors
