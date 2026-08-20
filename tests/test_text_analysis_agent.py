import unittest
from agents.text_analysis_agent import TextAnalysisAgent
from core.agent import AgentState
from core.result import Result
from core.task import Task


class TestTextAnalysisAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TextAnalysisAgent(agent_id="test-text-agent-01")

    def test_agent_initialization_and_capabilities(self):
        self.assertEqual(self.agent.id, "test-text-agent-01")
        self.assertEqual(self.agent.name, "TextAnalysisAgent")
        self.assertIn("text_analysis", self.agent.capabilities)
        self.assertEqual(self.agent.state, AgentState.IDLE)

    def test_valid_word_count(self):
        task = Task(
            description="Word count task",
            input_data="ABOS is an adaptive operating system",
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 6)
        self.assertEqual(result.agent_id, self.agent.id)
        self.assertIsNone(result.error)
        self.assertEqual(result.metadata["operation"], "word_count")
        self.assertEqual(result.metadata["word_count"], 6)

    def test_multiple_spaces_and_newlines(self):
        task = Task(
            description="Word count with multiple spaces",
            input_data="  ABOS   is \n  an   adaptive \t operating \n\n system  ",
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 6)

    def test_empty_string_input(self):
        task = Task(
            description="Word count with empty input",
            input_data="",
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 0)

    def test_whitespace_only_input(self):
        task = Task(
            description="Word count with whitespace",
            input_data="     \t \n ",
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 0)

    def test_dict_input_format(self):
        task = Task(
            description="Word count with dict",
            input_data={"text": "Hello world from ABOS agents"},
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 5)

    def test_fallback_to_description(self):
        task = Task(
            description="Three words here",
            input_data=None,
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertTrue(result.success)
        self.assertEqual(result.output, 3)

    def test_invalid_input_type(self):
        task = Task(
            description="Invalid input",
            input_data=["list", "of", "words"],  # Invalid type
            required_capabilities=["text_analysis"],
        )
        result = self.agent.execute(task)

        self.assertFalse(result.success)
        self.assertIsNone(result.output)
        self.assertIn("Invalid input type", result.error)
        self.assertEqual(result.agent_id, self.agent.id)


if __name__ == "__main__":
    unittest.main()
