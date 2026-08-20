import unittest
from core.agent import AgentState, BaseAgent
from core.agent_profile import AgentProfile
from core.evaluation import Evaluation
from core.execution import Execution, ExecutionStatus
from core.result import Result
from core.task import Task
from orchestration.performance import PerformanceTracker
from orchestration.scheduler import DeterministicScheduler, SchedulingResult


class MockComputeAgent(BaseAgent):
    """Mock agent for end-to-end adaptive feedback testing."""

    def __init__(self, agent_id: str, name: str, will_succeed: bool = True, latency_ms: float = 100.0):
        super().__init__(name=name, capabilities=["compute"], agent_id=agent_id)
        self.will_succeed = will_succeed
        self.simulated_latency_ms = latency_ms


    def execute(self, task: Task) -> Result:
        if self.will_succeed:
            return Result(
                success=True,
                output=f"Processed by {self.name}",
                agent_id=self.id,
            )
        return Result(
            success=False,
            error=f"Failure in {self.name}",
            agent_id=self.id,
        )


class TestAdaptiveFeedback(unittest.TestCase):
    def setUp(self):
        self.scheduler = DeterministicScheduler()
        self.tracker = PerformanceTracker(confidence_saturation=20)

    def test_end_to_end_adaptive_feedback_loop(self):
        """
        Verify the complete adaptive feedback loop:
        1. Initial state: Agent Alpha has higher score than Agent Beta.
        2. Scheduler selects Agent Alpha.
        3. Agent Alpha executes task and fails with high latency.
        4. Execution -> Result -> Evaluation -> PerformanceTracker -> AgentProfile.
        5. Subsequent scheduling sees updated profile and adapts (selects Agent Beta).
        """
        # Step 1: Create Candidate Agents
        agent_alpha = MockComputeAgent(
            agent_id="agent-alpha",
            name="AlphaCompute",
            will_succeed=False,
            latency_ms=600.0,
        )
        agent_beta = MockComputeAgent(
            agent_id="agent-beta",
            name="BetaCompute",
            will_succeed=True,
            latency_ms=120.0,
        )
        agents = [agent_alpha, agent_beta]

        # Step 2: Initialize Profiles
        # Initially Alpha has 100% success (10/10) vs Beta 85% (17/20)
        profile_alpha = AgentProfile(
            agent_id="agent-alpha",
            total_executions=10,
            successful_executions=10,
            success_rate=1.0,
            avg_latency_ms=80.0,
            confidence_score=0.50,
            capabilities=["compute"],
        )
        profile_beta = AgentProfile(
            agent_id="agent-beta",
            total_executions=20,
            successful_executions=18,
            success_rate=0.90,
            avg_latency_ms=120.0,
            confidence_score=1.00,
            capabilities=["compute"],
        )
        profiles = [profile_alpha, profile_beta]

        # Step 3: Define Task
        task1 = Task(description="Execute matrix computation", required_capabilities=["compute"])

        # Step 4: First Scheduling - Alpha is selected
        result1: SchedulingResult = self.scheduler.schedule(task1, agents, profiles)
        self.assertTrue(result1.success)
        self.assertEqual(result1.selected_agent_id, "agent-alpha")
        alpha_score_initial = result1.score

        # Step 5: Execute Task using selected agent (Alpha fails)
        exec1 = Execution(task_id=task1.id, agent_id=agent_alpha.id, attempt_number=1)
        exec_result: Result = agent_alpha.execute(task1)
        exec1.status = ExecutionStatus.SUCCESS if exec_result.success else ExecutionStatus.FAILED
        exec1.result = exec_result

        # Step 6: Generate Evaluation
        evaluation1 = Evaluation(
            execution_id=exec1.id,
            task_id=task1.id,
            agent_id=agent_alpha.id,
            success=exec_result.success,
            quality_score=0.1,
            correctness_score=0.0,
            latency_ms=agent_alpha.simulated_latency_ms,
            feedback="Execution failed due to internal error",
        )

        # Step 7: Feed Evaluation into PerformanceTracker
        self.tracker.update(evaluation1, profile_alpha)

        # Verify updated Alpha profile
        self.assertEqual(profile_alpha.total_executions, 11)
        self.assertEqual(profile_alpha.successful_executions, 10)
        self.assertAlmostEqual(profile_alpha.success_rate, 10 / 11, places=5)
        # Old avg 80.0 (count 10), new lat 600.0 -> (800 + 600) / 11 = 127.27 ms
        self.assertAlmostEqual(profile_alpha.avg_latency_ms, 1400 / 11, places=2)

        # Add two more failed evaluations to simulate persistent underperformance
        for i in range(2):
            ev = Evaluation(
                execution_id=f"exec-alpha-fail-{i}",
                task_id=f"task-fail-{i}",
                agent_id=agent_alpha.id,
                success=False,
                latency_ms=700.0,
            )
            self.tracker.update(ev, profile_alpha)

        self.assertEqual(profile_alpha.total_executions, 13)
        self.assertEqual(profile_alpha.successful_executions, 10)
        self.assertAlmostEqual(profile_alpha.success_rate, 10 / 13, places=4)

        # Step 8: Subsequent Scheduling for a new task
        task2 = Task(description="Execute second computation", required_capabilities=["compute"])
        result2: SchedulingResult = self.scheduler.schedule(task2, agents, profiles)

        # Verify adaptation: Beta is now selected over degraded Alpha
        self.assertTrue(result2.success)
        self.assertEqual(result2.selected_agent_id, "agent-beta")
        self.assertGreater(result2.score, 0.0)

        # Find Alpha's new score in candidate breakdown
        cand_alpha = next(c for c in result2.candidates if c.agent_id == "agent-alpha")
        cand_beta = next(c for c in result2.candidates if c.agent_id == "agent-beta")
        self.assertLess(cand_alpha.total_score, cand_beta.total_score)
        self.assertLess(cand_alpha.total_score, alpha_score_initial)

    def test_adaptation_measurably_adjusts_score_without_winner_change(self):
        """
        Verify that performance tracking measurably adjusts scoring even when
        the top agent remains the winner.
        """
        agent_alpha = MockComputeAgent(agent_id="agent-alpha", name="AlphaCompute")
        agent_beta = MockComputeAgent(agent_id="agent-beta", name="BetaCompute")
        agents = [agent_alpha, agent_beta]

        # Alpha is significantly better than Beta
        profile_alpha = AgentProfile(
            agent_id="agent-alpha",
            total_executions=20,
            successful_executions=20,
            success_rate=1.0,
            avg_latency_ms=50.0,
            confidence_score=1.0,
            capabilities=["compute"],
        )
        profile_beta = AgentProfile(
            agent_id="agent-beta",
            total_executions=20,
            successful_executions=10,
            success_rate=0.50,
            avg_latency_ms=300.0,
            confidence_score=1.0,
            capabilities=["compute"],
        )
        profiles = [profile_alpha, profile_beta]

        task = Task(description="Task 1", required_capabilities=["compute"])

        # Initial schedule
        res1 = self.scheduler.schedule(task, agents, profiles)
        self.assertEqual(res1.selected_agent_id, "agent-alpha")
        initial_alpha_score = res1.score

        # Feed a single failed execution for Alpha (success drops from 1.0 to 20/21 = 0.952)
        eval_failed = Evaluation(
            execution_id="exec-fail",
            task_id="t-fail",
            agent_id="agent-alpha",
            success=False,
            latency_ms=100.0,
        )
        self.tracker.update(eval_failed, profile_alpha)

        # Second schedule
        res2 = self.scheduler.schedule(task, agents, profiles)
        self.assertEqual(res2.selected_agent_id, "agent-alpha")  # Still winner
        self.assertLess(res2.score, initial_alpha_score)  # But score dropped (e.g. from 1.0 to ~0.976)


    def test_scheduler_policy_weights_remain_fixed(self):
        """Verify scheduler policy weights are not mutated during adaptive feedback."""
        self.assertEqual(self.scheduler.scoring_policy.success_rate_weight, 0.50)
        self.assertEqual(self.scheduler.scoring_policy.latency_weight, 0.20)
        self.assertEqual(self.scheduler.scoring_policy.confidence_weight, 0.30)


if __name__ == "__main__":
    unittest.main()
