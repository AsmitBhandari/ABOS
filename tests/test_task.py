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
        self.assertIsNone(task.result)

    def test_task_custom_priority(self):
        task = Task(description="Urgent task", input_data=123, priority=TaskPriority.HIGH)
        self.assertEqual(task.priority, TaskPriority.HIGH)

    def test_task_result_assignment(self):
        task = Task(description="Task with result", input_data="expression")
        result = Result(success=True, output=42, agent_id="agent-1")
        task.result = result
        task.status = TaskStatus.COMPLETED

        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.result)
        self.assertTrue(task.result.success)
        self.assertEqual(task.result.output, 42)


if __name__ == "__main__":
    unittest.main()
