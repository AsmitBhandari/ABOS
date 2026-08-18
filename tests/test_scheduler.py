import unittest
from core.agent import AgentState, BaseAgent
from core.agent_profile import AgentProfile
from core.result import Result
from core.task import Task, TaskPriority, TaskStatus
from orchestration.scheduler import (
    BaseScheduler,
    CandidateScore,
    DeterministicScheduler,
    Scheduler,
    SchedulingResult,
    ScoringPolicy,
)


class DummyAgent(BaseAgent):
    """Minimal concrete implementation of BaseAgent for testing scheduler behavior."""

    def execute(self, task: Task) -> Result:
        return Result(success=True, output="executed", agent_id=self.id)


class TestSchedulerContracts(unittest.TestCase):
    """Test scheduler class contracts, aliases, and data structures."""

    def test_alias(self):
        self.assertIs(Scheduler, BaseScheduler)

    def test_candidate_score_validation(self):
        score = CandidateScore(agent_id="agent-1", total_score=0.85)
        self.assertEqual(score.agent_id, "agent-1")
        self.assertTrue(score.eligible)
        self.assertIsNone(score.rejection_reason)

        with self.assertRaises(ValueError):
            CandidateScore(agent_id="")

    def test_candidate_score_to_dict(self):
        score = CandidateScore(
            agent_id="agent-1",
            total_score=0.85432,
            success_rate=0.9,
            latency_score=0.8,
            confidence_score=0.75,
            raw_latency_ms=120.456,
        )
        d = score.to_dict()
        self.assertEqual(d["agent_id"], "agent-1")
        self.assertEqual(d["total_score"], 0.8543)
        self.assertEqual(d["raw_latency_ms"], 120.46)
        self.assertTrue(d["eligible"])

    def test_scheduling_result_validation(self):
        result = SchedulingResult(
            task_id="task-1",
            selected_agent_id="agent-1",
            success=True,
            reason="Selected",
            score=0.85,
        )
        self.assertEqual(result.task_id, "task-1")
        self.assertEqual(result.selected_agent_id, "agent-1")
        self.assertTrue(result.success)

        with self.assertRaises(ValueError):
            SchedulingResult(task_id="", selected_agent_id="agent-1", success=True)

        with self.assertRaises(ValueError):
            SchedulingResult(
                task_id="task-1", selected_agent_id="agent-1", success=True, score=1.5
            )

        with self.assertRaises(ValueError):
            SchedulingResult(
                task_id="task-1", selected_agent_id="agent-1", success=True, score=-0.1
            )

    def test_scheduling_result_to_dict(self):
        cand = CandidateScore(agent_id="agent-1", total_score=0.9)
        result = SchedulingResult(
            task_id="task-100",
            selected_agent_id="agent-1",
            success=True,
            reason="Best candidate",
            score=0.9,
            candidates=[cand],
            metadata={"test": 123},
        )
        d = result.to_dict()
        self.assertEqual(d["task_id"], "task-100")
        self.assertEqual(d["selected_agent_id"], "agent-1")
        self.assertTrue(d["success"])
        self.assertEqual(d["score"], 0.9)
        self.assertEqual(len(d["candidates"]), 1)
        self.assertEqual(d["metadata"]["test"], 123)


class TestScoringPolicy(unittest.TestCase):
    """Test ScoringPolicy configuration, weight validation, and calculations."""

    def test_default_weights(self):
        policy = ScoringPolicy()
        self.assertAlmostEqual(policy.success_rate_weight, 0.50)
        self.assertAlmostEqual(policy.latency_weight, 0.20)
        self.assertAlmostEqual(policy.confidence_weight, 0.30)

    def test_custom_weights(self):
        policy = ScoringPolicy(
            success_rate_weight=0.60,
            latency_weight=0.10,
            confidence_weight=0.30,
        )
        self.assertAlmostEqual(policy.success_rate_weight, 0.60)

    def test_negative_weights_rejected(self):
        with self.assertRaises(ValueError):
            ScoringPolicy(
                success_rate_weight=-0.1,
                latency_weight=0.5,
                confidence_weight=0.6,
            )

    def test_invalid_weight_sum_rejected(self):
        with self.assertRaises(ValueError):
            ScoringPolicy(
                success_rate_weight=0.5,
                latency_weight=0.5,
                confidence_weight=0.5,
            )

    def test_score_calculation(self):
        policy = ScoringPolicy(
            success_rate_weight=0.50,
            latency_weight=0.20,
            confidence_weight=0.30,
        )
        score = policy.calculate_score(
            success_rate=1.0,
            latency_score=1.0,
            confidence_score=1.0,
        )
        self.assertAlmostEqual(score, 1.0)

        score_zero = policy.calculate_score(
            success_rate=0.0,
            latency_score=0.0,
            confidence_score=0.0,
        )
        self.assertAlmostEqual(score_zero, 0.0)

        score_mixed = policy.calculate_score(
            success_rate=0.8,
            latency_score=0.5,
            confidence_score=0.9,
        )
        # 0.8 * 0.5 + 0.5 * 0.2 + 0.9 * 0.3 = 0.40 + 0.10 + 0.27 = 0.77
        self.assertAlmostEqual(score_mixed, 0.77)

    def test_latency_normalization_varied(self):
        latencies = {"a1": 100.0, "a2": 200.0, "a3": 300.0}
        scores = ScoringPolicy.normalize_latencies(latencies)
        self.assertAlmostEqual(scores["a1"], 1.0)  # Lowest latency = best score
        self.assertAlmostEqual(scores["a2"], 0.5)
        self.assertAlmostEqual(scores["a3"], 0.0)  # Highest latency = lowest score

    def test_latency_normalization_identical(self):
        latencies = {"a1": 150.0, "a2": 150.0}
        scores = ScoringPolicy.normalize_latencies(latencies)
        self.assertAlmostEqual(scores["a1"], 1.0)
        self.assertAlmostEqual(scores["a2"], 1.0)

    def test_latency_normalization_missing(self):
        latencies = {"a1": None, "a2": 100.0, "a3": 200.0}
        scores = ScoringPolicy.normalize_latencies(latencies)
        self.assertAlmostEqual(scores["a1"], 0.5)  # Missing gets neutral
        self.assertAlmostEqual(scores["a2"], 1.0)
        self.assertAlmostEqual(scores["a3"], 0.0)


class TestDeterministicSchedulerSelection(unittest.TestCase):
    """Test capability matching, state filtering, and performance selection."""

    def setUp(self):
        self.scheduler = DeterministicScheduler()

    def test_capability_matching_single_compatible(self):
        task = Task(
            description="Run Python script",
            required_capabilities=["python", "math"],
        )
        agent1 = DummyAgent("Agent1", ["python", "math", "db"], agent_id="a1")
        agent2 = DummyAgent("Agent2", ["python"], agent_id="a2")

        result = self.scheduler.schedule(task, [agent1, agent2])
        self.assertTrue(result.success)
        self.assertEqual(result.selected_agent_id, "a1")

    def test_capability_matching_incompatible_rejected(self):
        task = Task(
            description="Run Python script",
            required_capabilities=["python"],
        )
        agent1 = DummyAgent("Agent1", ["sql"], agent_id="a1")
        result = self.scheduler.schedule(task, [agent1])
        self.assertFalse(result.success)
        self.assertIsNone(result.selected_agent_id)
        self.assertIn("capabilities", result.reason.lower())

    def test_state_filtering_busy_rejected(self):
        task = Task(description="Calculate", required_capabilities=["math"])
        agent1 = DummyAgent("Agent1", ["math"], agent_id="a1")
        agent1.state = AgentState.BUSY
        agent2 = DummyAgent("Agent2", ["math"], agent_id="a2")
        agent2.state = AgentState.IDLE

        result = self.scheduler.schedule(task, [agent1, agent2])
        self.assertTrue(result.success)
        self.assertEqual(result.selected_agent_id, "a2")

    def test_state_filtering_error_and_terminated_rejected(self):
        task = Task(description="Calculate", required_capabilities=["math"])
        agent1 = DummyAgent("Agent1", ["math"], agent_id="a1")
        agent1.state = AgentState.ERROR
        agent2 = DummyAgent("Agent2", ["math"], agent_id="a2")
        agent2.state = AgentState.TERMINATED

        result = self.scheduler.schedule(task, [agent1, agent2])
        self.assertFalse(result.success)
        self.assertIsNone(result.selected_agent_id)
        self.assertIn("IDLE", result.reason)

    def test_performance_scoring_selects_higher_score(self):
        task = Task(description="Data processing", required_capabilities=["python"])
        agent_strong = DummyAgent("Strong", ["python"], agent_id="a_strong")
        agent_weak = DummyAgent("Weak", ["python"], agent_id="a_weak")

        prof_strong = AgentProfile(
            agent_id="a_strong",
            total_executions=10,
            successful_executions=10,
            success_rate=1.0,
            avg_latency_ms=100.0,
            confidence_score=0.9,
        )
        prof_weak = AgentProfile(
            agent_id="a_weak",
            total_executions=10,
            successful_executions=6,
            success_rate=0.6,
            avg_latency_ms=500.0,
            confidence_score=0.5,
        )

        result = self.scheduler.schedule(
            task,
            [agent_weak, agent_strong],
            profiles=[prof_weak, prof_strong],
        )
        self.assertTrue(result.success)
        self.assertEqual(result.selected_agent_id, "a_strong")
        self.assertGreater(result.score, 0.8)

    def test_success_rate_impact(self):
        task = Task(description="Task", required_capabilities=["cap"])
        a1 = DummyAgent("A1", ["cap"], agent_id="a1")
        a2 = DummyAgent("A2", ["cap"], agent_id="a2")

        # Same latency and confidence, different success_rate
        p1 = AgentProfile(agent_id="a1", success_rate=0.95, avg_latency_ms=100.0, confidence_score=0.8)
        p2 = AgentProfile(agent_id="a2", success_rate=0.70, avg_latency_ms=100.0, confidence_score=0.8)

        result = self.scheduler.schedule(task, [a1, a2], [p1, p2])
        self.assertEqual(result.selected_agent_id, "a1")

    def test_latency_impact(self):
        task = Task(description="Task", required_capabilities=["cap"])
        a1 = DummyAgent("A1", ["cap"], agent_id="a1")
        a2 = DummyAgent("A2", ["cap"], agent_id="a2")

        # Same success rate and confidence, a1 is much faster
        p1 = AgentProfile(agent_id="a1", success_rate=0.9, avg_latency_ms=50.0, confidence_score=0.8)
        p2 = AgentProfile(agent_id="a2", success_rate=0.9, avg_latency_ms=500.0, confidence_score=0.8)

        result = self.scheduler.schedule(task, [a1, a2], [p1, p2])
        self.assertEqual(result.selected_agent_id, "a1")

    def test_confidence_impact(self):
        task = Task(description="Task", required_capabilities=["cap"])
        a1 = DummyAgent("A1", ["cap"], agent_id="a1")
        a2 = DummyAgent("A2", ["cap"], agent_id="a2")

        # Same success rate and latency, a1 has higher confidence
        p1 = AgentProfile(agent_id="a1", success_rate=0.9, avg_latency_ms=100.0, confidence_score=0.95)
        p2 = AgentProfile(agent_id="a2", success_rate=0.9, avg_latency_ms=100.0, confidence_score=0.50)

        result = self.scheduler.schedule(task, [a1, a2], [p1, p2])
        self.assertEqual(result.selected_agent_id, "a1")

    def test_tie_breaking_order(self):
        task = Task(description="Task", required_capabilities=["cap"])
        # Exactly identical profiles but different agent IDs
        a_first = DummyAgent("Agent A", ["cap"], agent_id="agent-a")
        a_second = DummyAgent("Agent B", ["cap"], agent_id="agent-b")

        p_a = AgentProfile(agent_id="agent-a", success_rate=0.9, avg_latency_ms=100.0, confidence_score=0.8)
        p_b = AgentProfile(agent_id="agent-b", success_rate=0.9, avg_latency_ms=100.0, confidence_score=0.8)

        # Lexicographical tie break should pick agent-a regardless of input order
        res1 = self.scheduler.schedule(task, [a_first, a_second], [p_a, p_b])
        res2 = self.scheduler.schedule(task, [a_second, a_first], [p_b, p_a])
        self.assertEqual(res1.selected_agent_id, "agent-a")
        self.assertEqual(res2.selected_agent_id, "agent-a")

    def test_missing_agent_profile_handled_safely(self):
        task = Task(description="Task", required_capabilities=["cap"])
        a1 = DummyAgent("A1", ["cap"], agent_id="a1")
        # No profile passed for a1
        result = self.scheduler.schedule(task, [a1], profiles=[])
        self.assertTrue(result.success)
        self.assertEqual(result.selected_agent_id, "a1")
        # Neutral assumptions: success_rate 0.5 * 0.5 + latency 0.5 * 0.2 + conf 0.5 * 0.3 = 0.50
        self.assertAlmostEqual(result.score, 0.50)

    def test_no_candidate_agents_provided(self):
        task = Task(description="Task")
        result = self.scheduler.schedule(task, [])
        self.assertFalse(result.success)
        self.assertIsNone(result.selected_agent_id)
        self.assertEqual(result.score, 0.0)

    def test_empty_task_capabilities(self):
        task = Task(description="Generic task", required_capabilities=[])
        a1 = DummyAgent("A1", ["python"], agent_id="a1")
        a2 = DummyAgent("A2", [], agent_id="a2")
        result = self.scheduler.schedule(task, [a1, a2])
        self.assertTrue(result.success)
        self.assertIsNotNone(result.selected_agent_id)

    def test_agent_with_no_capabilities_eligible_only_for_empty_task_reqs(self):
        task_empty = Task(description="Generic task", required_capabilities=[])
        task_specific = Task(description="Specific", required_capabilities=["python"])
        agent_no_caps = DummyAgent("A0", [], agent_id="a0")

        res_empty = self.scheduler.schedule(task_empty, [agent_no_caps])
        self.assertTrue(res_empty.success)
        self.assertEqual(res_empty.selected_agent_id, "a0")

        res_specific = self.scheduler.schedule(task_specific, [agent_no_caps])
        self.assertFalse(res_specific.success)
        self.assertIsNone(res_specific.selected_agent_id)

    def test_mutation_safety(self):
        task = Task(
            description="Compute",
            required_capabilities=["math"],
            assigned_agent_id=None,
            status=TaskStatus.PENDING,
        )
        agent = DummyAgent("MathAgent", ["math"], agent_id="math-1")
        agent.state = AgentState.IDLE
        profile = AgentProfile(
            agent_id="math-1",
            total_executions=5,
            successful_executions=5,
            success_rate=1.0,
            avg_latency_ms=50.0,
            confidence_score=0.9,
        )

        result = self.scheduler.schedule(task, [agent], [profile])
        self.assertTrue(result.success)
        self.assertEqual(result.selected_agent_id, "math-1")

        # Verify NO mutation occurred on domain objects
        self.assertIsNone(task.assigned_agent_id)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(agent.state, AgentState.IDLE)
        self.assertEqual(profile.total_executions, 5)
        self.assertEqual(profile.successful_executions, 5)


if __name__ == "__main__":
    unittest.main()
