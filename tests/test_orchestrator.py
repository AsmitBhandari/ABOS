import unittest
from agents.calculator_agent import CalculatorAgent
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        self.calc_agent = CalculatorAgent(agent_id="calc-1")

    def test_agent_registration(self):
        self.orchestrator.register_agent(self.calc_agent)
        self.assertIn("calc-1", self.orchestrator.agents)

    def test_agent_selection_and_execution(self):
        self.orchestrator.register_agent(self.calc_agent)
        task = Task(description="Calculate 25 * 37", input_data="25 * 37")
        
        result = self.orchestrator.execute_task(task)
        self.assertTrue(result.success)
        self.assertEqual(result.output, 925)
        self.assertEqual(result.agent_id, "calc-1")
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.result)

    def test_unsupported_task_handling(self):
        # Empty orchestrator, no agents registered
        task = Task(description="Unknown action", input_data="abc")
        result = self.orchestrator.execute_task(task)
        
        self.assertFalse(result.success)
        self.assertIn("No suitable agent found", result.error)
        self.assertEqual(task.status, TaskStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
