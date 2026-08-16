import unittest
from core.result import Result


class TestResult(unittest.TestCase):
    def test_successful_result(self):
        res = Result(success=True, output=925, agent_id="calc-agent")
        self.assertTrue(res.success)
        self.assertEqual(res.output, 925)
        self.assertIsNone(res.error)
        self.assertEqual(res.agent_id, "calc-agent")
        self.assertEqual(res.metadata, {})

    def test_failed_result(self):
        res = Result(
            success=False,
            output=None,
            error="Syntax Error",
            agent_id="calc-agent",
            metadata={"code": 400}
        )
        self.assertFalse(res.success)
        self.assertIsNone(res.output)
        self.assertEqual(res.error, "Syntax Error")
        self.assertEqual(res.metadata["code"], 400)

    def test_to_dict_serialization(self):
        res = Result(success=True, output="OK", agent_id="agent-xyz", metadata={"env": "test"})
        res_dict = res.to_dict()
        self.assertEqual(res_dict["success"], True)
        self.assertEqual(res_dict["output"], "OK")
        self.assertEqual(res_dict["agent_id"], "agent-xyz")
        self.assertEqual(res_dict["metadata"], {"env": "test"})


if __name__ == "__main__":
    unittest.main()
