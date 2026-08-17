import unittest
from core.result import Result
from core.task import Task, TaskPriority, TaskStatus


class TestTask(unittest.TestCase):
    def test_task_creation_defaults(self):
        task = Task(description="Test task", input_data="data")
        self.assertIsNotNone(task.id)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.input_data, "data")
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.required_capabilities, [])
        self.assertIsNone(task.assigned_agent_id)
        self.assertIsNone(task.parent_task_id)
        self.assertEqual(task.child_task_ids, [])
        self.assertIsNotNone(task.created_at)
        self.assertEqual(task.metadata, {})
        self.assertIsNone(task.result)

    def test_task_custom_priority_and_capabilities(self):
        task = Task(
            description="Urgent task",
            input_data=123,
            priority=TaskPriority.HIGH,
            required_capabilities=["math", "finance"],
        )
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.required_capabilities, ["math", "finance"])

    def test_task_result_assignment(self):
        task = Task(description="Task with result", input_data="expression")
        result = Result(success=True, output=42, agent_id="agent-1")
        task.result = result
        task.status = TaskStatus.COMPLETED

        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.result)
        self.assertTrue(task.result.success)
        self.assertEqual(task.result.output, 42)

    def test_composite_hierarchical_task(self):
        parent = Task(description="Parent task", input_data=None)
        child1 = Task(description="Child task 1", input_data=1, parent_task_id=parent.id)
        child2 = Task(description="Child task 2", input_data=2, parent_task_id=parent.id)

        parent.child_task_ids = [child1.id, child2.id]

        self.assertEqual(child1.parent_task_id, parent.id)
        self.assertEqual(child2.parent_task_id, parent.id)
        self.assertEqual(len(parent.child_task_ids), 2)
        self.assertIn(child1.id, parent.child_task_ids)
        self.assertIn(child2.id, parent.child_task_ids)

    def test_task_validation_empty_id(self):
        with self.assertRaises(ValueError) as ctx:
            Task(description="Test", input_data=None, id="")
        self.assertIn("Task ID cannot be empty", str(ctx.exception))

    def test_task_validation_parent_equals_own_id(self):
        with self.assertRaises(ValueError) as ctx:
            Task(description="Self parent", input_data=None, id="task-100", parent_task_id="task-100")
        self.assertIn("parent_task_id cannot equal task ID", str(ctx.exception))

    def test_task_validation_duplicate_child_ids(self):
        with self.assertRaises(ValueError) as ctx:
            Task(description="Parent", input_data=None, child_task_ids=["child-1", "child-1"])
        self.assertIn("child_task_ids cannot contain duplicates", str(ctx.exception))

    def test_task_serialization(self):
        task = Task(description="Serializable task", input_data={"expr": "1+1"})
        task_dict = task.to_dict()
        self.assertEqual(task_dict["id"], task.id)
        self.assertEqual(task_dict["description"], "Serializable task")
        self.assertEqual(task_dict["status"], "PENDING")
        self.assertEqual(task_dict["priority"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()
