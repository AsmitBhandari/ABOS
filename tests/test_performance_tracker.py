import unittest
from datetime import datetime, timezone
from core.agent_profile import AgentProfile
from core.evaluation import Evaluation
from orchestration.performance import PerformanceTracker


class TestPerformanceTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = PerformanceTracker(confidence_saturation=20)

    def test_tracker_initialization_defaults_and_validation(self):
        tracker = PerformanceTracker()
        self.assertEqual(tracker.confidence_saturation, 20)
        self.assertEqual(tracker.processed_count(), 0)

        with self.assertRaises(ValueError):
            PerformanceTracker(confidence_saturation=0)
        with self.assertRaises(ValueError):
            PerformanceTracker(confidence_saturation=-5)

    def test_first_successful_execution(self):
        profile = AgentProfile(agent_id="agent-01")
        timestamp = datetime.now(timezone.utc).isoformat()
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-01",
            success=True,
            quality_score=0.9,
            correctness_score=1.0,
            latency_ms=100.0,
            created_at=timestamp,
        )

        updated_profile = self.tracker.update(evaluation, profile)

        self.assertEqual(updated_profile.total_executions, 1)
        self.assertEqual(updated_profile.successful_executions, 1)
        self.assertEqual(updated_profile.success_rate, 1.0)
        self.assertEqual(updated_profile.avg_latency_ms, 100.0)
        self.assertEqual(updated_profile.confidence_score, 1 / 20)
        self.assertEqual(updated_profile.last_execution_at, timestamp)
        self.assertIn("performance", updated_profile.metadata)
        self.assertEqual(updated_profile.metadata["performance"]["evaluation_count"], 1)
        self.assertEqual(updated_profile.metadata["performance"]["average_quality"], 0.9)
        self.assertEqual(updated_profile.metadata["performance"]["average_correctness"], 1.0)

    def test_first_failed_execution(self):
        profile = AgentProfile(agent_id="agent-01")
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-01",
            success=False,
            latency_ms=250.0,
        )

        updated_profile = self.tracker.update(evaluation, profile)

        self.assertEqual(updated_profile.total_executions, 1)
        self.assertEqual(updated_profile.successful_executions, 0)
        self.assertEqual(updated_profile.success_rate, 0.0)
        self.assertEqual(updated_profile.avg_latency_ms, 250.0)
        self.assertEqual(updated_profile.confidence_score, 1 / 20)

    def test_cumulative_success_rate_updates(self):
        profile = AgentProfile(
            agent_id="agent-01",
            total_executions=10,
            successful_executions=8,
            success_rate=0.80,
            avg_latency_ms=150.0,
            confidence_score=0.50,
        )

        # 1. Successful execution: 9 / 11 = ~0.8182
        eval_success = Evaluation(
            execution_id="exec-11",
            task_id="task-11",
            agent_id="agent-01",
            success=True,
            latency_ms=100.0,
        )
        self.tracker.update(eval_success, profile)
        self.assertEqual(profile.total_executions, 11)
        self.assertEqual(profile.successful_executions, 9)
        self.assertAlmostEqual(profile.success_rate, 9 / 11, places=5)

        # 2. Failed execution: 9 / 12 = 0.75
        eval_fail = Evaluation(
            execution_id="exec-12",
            task_id="task-12",
            agent_id="agent-01",
            success=False,
            latency_ms=200.0,
        )
        self.tracker.update(eval_fail, profile)
        self.assertEqual(profile.total_executions, 12)
        self.assertEqual(profile.successful_executions, 9)
        self.assertEqual(profile.success_rate, 9 / 12)

    def test_incremental_latency_cumulative_average(self):
        profile = AgentProfile(
            agent_id="agent-01",
            total_executions=2,
            successful_executions=2,
            success_rate=1.0,
            avg_latency_ms=100.0,  # 100 * 2 = 200 total ms
        )

        # Add 3rd execution with latency 40.0 ms -> (200 + 40) / 3 = 80.0 ms
        eval1 = Evaluation(
            execution_id="exec-03",
            task_id="task-03",
            agent_id="agent-01",
            success=True,
            latency_ms=40.0,
        )
        self.tracker.update(eval1, profile)
        self.assertEqual(profile.total_executions, 3)
        self.assertAlmostEqual(profile.avg_latency_ms, 80.0, places=5)

        # Add 4th execution with latency 160.0 ms -> (240 + 160) / 4 = 100.0 ms
        eval2 = Evaluation(
            execution_id="exec-04",
            task_id="task-04",
            agent_id="agent-01",
            success=True,
            latency_ms=160.0,
        )
        self.tracker.update(eval2, profile)
        self.assertEqual(profile.total_executions, 4)
        self.assertAlmostEqual(profile.avg_latency_ms, 100.0, places=5)

    def test_confidence_score_progression(self):
        tracker = PerformanceTracker(confidence_saturation=20)
        profile = AgentProfile(agent_id="agent-01")

        # 0 executions (initial default)
        self.assertEqual(profile.total_executions, 0)

        # Test at 5 executions -> 5 / 20 = 0.25
        for i in range(1, 6):
            ev = Evaluation(
                execution_id=f"exec-{i}",
                task_id=f"task-{i}",
                agent_id="agent-01",
                success=True,
                latency_ms=50.0,
            )
            tracker.update(ev, profile)
        self.assertEqual(profile.total_executions, 5)
        self.assertAlmostEqual(profile.confidence_score, 0.25, places=5)

        # Test at 10 executions -> 10 / 20 = 0.50
        for i in range(6, 11):
            ev = Evaluation(
                execution_id=f"exec-{i}",
                task_id=f"task-{i}",
                agent_id="agent-01",
                success=True,
                latency_ms=50.0,
            )
            tracker.update(ev, profile)
        self.assertEqual(profile.total_executions, 10)
        self.assertAlmostEqual(profile.confidence_score, 0.50, places=5)

        # Test at 20 executions -> 20 / 20 = 1.00
        for i in range(11, 21):
            ev = Evaluation(
                execution_id=f"exec-{i}",
                task_id=f"task-{i}",
                agent_id="agent-01",
                success=True,
                latency_ms=50.0,
            )
            tracker.update(ev, profile)
        self.assertEqual(profile.total_executions, 20)
        self.assertAlmostEqual(profile.confidence_score, 1.00, places=5)

        # Test at 30 executions -> min(1.0, 30 / 20) = 1.00
        for i in range(21, 31):
            ev = Evaluation(
                execution_id=f"exec-{i}",
                task_id=f"task-{i}",
                agent_id="agent-01",
                success=True,
                latency_ms=50.0,
            )
            tracker.update(ev, profile)
        self.assertEqual(profile.total_executions, 30)
        self.assertAlmostEqual(profile.confidence_score, 1.00, places=5)

    def test_quality_and_correctness_score_aggregation(self):
        profile = AgentProfile(agent_id="agent-01")

        # Eval 1: quality=0.8, correctness=0.9
        ev1 = Evaluation(
            execution_id="e1",
            task_id="t1",
            agent_id="agent-01",
            success=True,
            quality_score=0.8,
            correctness_score=0.9,
        )
        self.tracker.update(ev1, profile)
        perf_meta = profile.metadata["performance"]
        self.assertEqual(perf_meta["quality_eval_count"], 1)
        self.assertEqual(perf_meta["correctness_eval_count"], 1)
        self.assertAlmostEqual(perf_meta["average_quality"], 0.8)
        self.assertAlmostEqual(perf_meta["average_correctness"], 0.9)

        # Eval 2: quality=1.0, correctness=0.7
        ev2 = Evaluation(
            execution_id="e2",
            task_id="t2",
            agent_id="agent-01",
            success=True,
            quality_score=1.0,
            correctness_score=0.7,
        )
        self.tracker.update(ev2, profile)
        self.assertEqual(perf_meta["quality_eval_count"], 2)
        self.assertEqual(perf_meta["correctness_eval_count"], 2)
        self.assertAlmostEqual(perf_meta["average_quality"], 0.9)  # (0.8 + 1.0) / 2
        self.assertAlmostEqual(perf_meta["average_correctness"], 0.8)  # (0.9 + 0.7) / 2

        # Eval 3: quality=None, correctness=None
        ev3 = Evaluation(
            execution_id="e3",
            task_id="t3",
            agent_id="agent-01",
            success=True,
        )
        self.tracker.update(ev3, profile)
        self.assertEqual(perf_meta["evaluation_count"], 3)
        self.assertEqual(perf_meta["quality_eval_count"], 2)
        self.assertEqual(perf_meta["correctness_eval_count"], 2)
        self.assertAlmostEqual(perf_meta["average_quality"], 0.9)
        self.assertAlmostEqual(perf_meta["average_correctness"], 0.8)

    def test_agent_id_mismatch_rejected(self):
        profile = AgentProfile(agent_id="agent-alpha")
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-beta",
            success=True,
        )

        with self.assertRaises(ValueError) as ctx:
            self.tracker.update(evaluation, profile)
        self.assertIn("Agent ID mismatch", str(ctx.exception))
        self.assertEqual(profile.total_executions, 0)

    def test_idempotency_same_evaluation_submitted_twice(self):
        profile = AgentProfile(agent_id="agent-01")
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-01",
            success=True,
            quality_score=0.9,
            correctness_score=1.0,
            latency_ms=100.0,
        )

        # First submission
        self.tracker.update(evaluation, profile)
        self.assertEqual(profile.total_executions, 1)
        self.assertEqual(profile.successful_executions, 1)
        self.assertEqual(profile.success_rate, 1.0)
        self.assertEqual(profile.avg_latency_ms, 100.0)
        self.assertEqual(self.tracker.processed_count(), 1)
        self.assertTrue(self.tracker.is_processed(evaluation.id))

        # Second submission of the EXACT SAME evaluation
        self.tracker.update(evaluation, profile)
        self.assertEqual(profile.total_executions, 1)
        self.assertEqual(profile.successful_executions, 1)
        self.assertEqual(profile.success_rate, 1.0)
        self.assertEqual(profile.avg_latency_ms, 100.0)
        self.assertEqual(self.tracker.processed_count(), 1)

    def test_type_validation(self):
        profile = AgentProfile(agent_id="agent-01")
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-01",
            success=True,
        )

        with self.assertRaises(TypeError):
            self.tracker.update("not-an-evaluation", profile)  # type: ignore

        with self.assertRaises(TypeError):
            self.tracker.update(evaluation, "not-a-profile")  # type: ignore

    def test_tracker_reset(self):
        profile = AgentProfile(agent_id="agent-01")
        evaluation = Evaluation(
            execution_id="exec-01",
            task_id="task-01",
            agent_id="agent-01",
            success=True,
        )
        self.tracker.update(evaluation, profile)
        self.assertEqual(self.tracker.processed_count(), 1)
        self.tracker.reset()
        self.assertEqual(self.tracker.processed_count(), 0)
        self.assertFalse(self.tracker.is_processed(evaluation.id))


if __name__ == "__main__":
    unittest.main()
