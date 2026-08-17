import unittest
from core.execution import Execution, ExecutionStatus
from core.result import Result


class TestExecution(unittest.TestCase):
    def test_execution_creation_defaults(self):
        execution = Execution(task_id="task-001", agent_id="agent-001")
        self.assertIsNotNone(execution.id)
        self.assertEqual(execution.task_id, "task-001")
        self.assertEqual(execution.agent_id, "agent-001")
        self.assertEqual(execution.status, ExecutionStatus.RUNNING)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNone(execution.completed_at)
        self.assertIsNone(execution.result)
        self.assertEqual(execution.attempt_number, 1)
        self.assertIsNone(execution.error)
        self.assertEqual(execution.metadata, {})

    def test_execution_with_result_linkage(self):
        execution = Execution(
            task_id="task-002",
            agent_id="agent-002",
            attempt_number=2,
            status=ExecutionStatus.SUCCESS,
        )
        res = Result(success=True, output=100, agent_id="agent-002", execution_id=execution.id)
        execution.result = res

        self.assertEqual(execution.attempt_number, 2)
        self.assertEqual(execution.status, ExecutionStatus.SUCCESS)
        self.assertIsNotNone(execution.result)
        self.assertEqual(execution.result.execution_id, execution.id)

    def test_execution_validation_empty_ids(self):
        with self.assertRaises(ValueError):
            Execution(task_id="", agent_id="agent-001")
        with self.assertRaises(ValueError):
            Execution(task_id="task-001", agent_id="")
        with self.assertRaises(ValueError):
            Execution(task_id="task-001", agent_id="agent-001", id="")

    def test_execution_validation_invalid_attempt(self):
        with self.assertRaises(ValueError):
            Execution(task_id="task-001", agent_id="agent-001", attempt_number=0)

    def test_execution_serialization(self):
        execution = Execution(task_id="task-001", agent_id="agent-001", metadata={"retry": True})
        execution_dict = execution.to_dict()
        self.assertEqual(execution_dict["id"], execution.id)
        self.assertEqual(execution_dict["task_id"], "task-001")
        self.assertEqual(execution_dict["agent_id"], "agent-001")
        self.assertEqual(execution_dict["status"], "RUNNING")
        self.assertEqual(execution_dict["metadata"], {"retry": True})


if __name__ == "__main__":
    unittest.main()
