import unittest
from core.agent_profile import AgentProfile


class TestAgentProfile(unittest.TestCase):
    def test_agent_profile_defaults(self):
        profile = AgentProfile(agent_id="calc-agent-1")
        self.assertEqual(profile.agent_id, "calc-agent-1")
        self.assertEqual(profile.total_executions, 0)
        self.assertEqual(profile.successful_executions, 0)
        self.assertEqual(profile.success_rate, 0.0)
        self.assertEqual(profile.avg_latency_ms, 0.0)
        self.assertEqual(profile.confidence_score, 0.5)
        self.assertEqual(profile.capabilities, [])
        self.assertIsNone(profile.last_execution_at)

    def test_agent_profile_custom_metrics(self):
        profile = AgentProfile(
            agent_id="calc-agent-2",
            total_executions=10,
            successful_executions=9,
            success_rate=0.9,
            avg_latency_ms=45.2,
            confidence_score=0.88,
            capabilities=["math", "calculation"],
        )
        self.assertEqual(profile.total_executions, 10)
        self.assertEqual(profile.successful_executions, 9)
        self.assertEqual(profile.success_rate, 0.9)
        self.assertEqual(profile.confidence_score, 0.88)
        self.assertEqual(profile.capabilities, ["math", "calculation"])

    def test_agent_profile_validation_negative_executions(self):
        with self.assertRaises(ValueError) as ctx:
            AgentProfile(agent_id="a1", total_executions=-1)
        self.assertIn("total_executions cannot be negative", str(ctx.exception))

    def test_agent_profile_validation_successful_exceeds_total(self):
        with self.assertRaises(ValueError) as ctx:
            AgentProfile(agent_id="a1", total_executions=5, successful_executions=6)
        self.assertIn("successful_executions cannot exceed total_executions", str(ctx.exception))

    def test_agent_profile_validation_score_bounds(self):
        with self.assertRaises(ValueError) as ctx:
            AgentProfile(agent_id="a1", confidence_score=1.2)
        self.assertIn("confidence_score must be between 0.0 and 1.0", str(ctx.exception))

    def test_agent_profile_serialization(self):
        profile = AgentProfile(agent_id="a1", confidence_score=0.75)
        prof_dict = profile.to_dict()
        self.assertEqual(prof_dict["agent_id"], "a1")
        self.assertEqual(prof_dict["confidence_score"], 0.75)


if __name__ == "__main__":
    unittest.main()
