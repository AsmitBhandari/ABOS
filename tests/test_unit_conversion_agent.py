import unittest
from agents.unit_conversion_agent import UnitConversionAgent
from core.agent import AgentState
from core.result import Result
from core.task import Task


class TestUnitConversionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = UnitConversionAgent(agent_id="test-unit-agent-01")

    def test_agent_initialization_and_capabilities(self):
        self.assertEqual(self.agent.id, "test-unit-agent-01")
        self.assertEqual(self.agent.name, "UnitConversionAgent")
        self.assertIn("unit_conversion", self.agent.capabilities)
        self.assertEqual(self.agent.state, AgentState.IDLE)

    def test_km_to_m_conversion(self):
        task = Task(
            description="Convert 5 km to m",
            input_data="5 km to m",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 5000)
        self.assertEqual(result.agent_id, self.agent.id)
        self.assertEqual(result.metadata["from_unit"], "km")
        self.assertEqual(result.metadata["to_unit"], "m")
        self.assertEqual(result.metadata["converted_value"], 5000)

    def test_m_to_km_conversion(self):
        task = Task(
            description="Convert 5000 m to km",
            input_data="5000 m to km",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 5)

    def test_m_to_cm_conversion(self):
        task = Task(
            description="Convert 2 m to cm",
            input_data="2 m to cm",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 200)

    def test_cm_to_m_conversion(self):
        task = Task(
            description="Convert 300 cm to m",
            input_data="300 cm to m",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 3)

    def test_arrow_and_case_insensitive_formatting(self):
        task = Task(
            description="Convert 2.5 KM -> M",
            input_data="convert 2.5 KM -> M",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 2500)

    def test_dict_input_format(self):
        task = Task(
            description="Unit conversion via dict",
            input_data={"value": 1500, "from_unit": "m", "to_unit": "km"},
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 1.5)

    def test_unsupported_unit_conversion(self):
        task = Task(
            description="Convert 5 miles to km",
            input_data="5 miles to km",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertFalse(result.success)
        self.assertIsNone(result.output)
        self.assertIn("Unsupported unit", result.error)
        self.assertEqual(result.agent_id, self.agent.id)

    def test_unsupported_conversion_pair(self):
        task = Task(
            description="Convert 5 km to cm",
            input_data={"value": 5, "from_unit": "km", "to_unit": "cm"},
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertFalse(result.success)
        self.assertIn("Unsupported conversion pair", result.error)

    def test_malformed_input(self):
        task = Task(
            description="Nonsense text without numbers",
            input_data="invalid conversion request without units",
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertFalse(result.success)
        self.assertIn("Malformed input", result.error)

    def test_invalid_numeric_input_in_dict(self):
        task = Task(
            description="Invalid numeric",
            input_data={"value": "abc", "from_unit": "km", "to_unit": "m"},
            required_capabilities=["unit_conversion"],
        )
        result = self.agent.execute(task)

        self.assertFalse(result.success)
        self.assertIn("Invalid numeric value", result.error)


if __name__ == "__main__":
    unittest.main()
