import unittest
from agents.calculator_agent import CalculatorAgent
from core.task import Task


class TestCalculatorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = CalculatorAgent(agent_id="test-calc")

    def test_valid_multiplication(self):
        task = Task(description="Calculate multiplication", input_data="25 * 37")
        res = self.agent.execute(task)
        self.assertTrue(res.success)
        self.assertEqual(res.output, 925)
        self.assertEqual(res.agent_id, "test-calc")
        self.assertIsNone(res.error)

    def test_valid_complex_arithmetic(self):
        task = Task(description="Complex expression", input_data="(10 + 20) * 3 - 50 / 2")
        res = self.agent.execute(task)
        self.assertTrue(res.success)
        self.assertEqual(res.output, 65)

    def test_division_by_zero(self):
        task = Task(description="Div zero", input_data="100 / 0")
        res = self.agent.execute(task)
        self.assertFalse(res.success)
        self.assertIsNone(res.output)
        self.assertIn("Division by zero", res.error)

    def test_invalid_syntax(self):
        task = Task(description="Bad syntax", input_data="25 * * 37")
        res = self.agent.execute(task)
        self.assertFalse(res.success)
        self.assertIsNone(res.output)
        self.assertIsNotNone(res.error)

    def test_disallowed_code_injection(self):
        task = Task(description="Injection test", input_data="__import__('os').system('dir')")
        res = self.agent.execute(task)
        self.assertFalse(res.success)
        self.assertIsNone(res.output)
        self.assertIn("Disallowed expression node", res.error)


if __name__ == "__main__":
    unittest.main()
