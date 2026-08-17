import unittest
from core.evaluation import Evaluation


class TestEvaluation(unittest.TestCase):
    def test_evaluation_creation(self):
        eval_obj = Evaluation(
            execution_id="exec-100",
            task_id="task-100",
            agent_id="agent-100",
            success=True,
            quality_score=0.95,
            correctness_score=1.0,
            latency_ms=120.5,
            feedback="Execution clean and fast",
            evaluator="system_evaluator",
        )
        self.assertIsNotNone(eval_obj.id)
        self.assertEqual(eval_obj.execution_id, "exec-100")
        self.assertEqual(eval_obj.quality_score, 0.95)
        self.assertEqual(eval_obj.correctness_score, 1.0)
        self.assertEqual(eval_obj.latency_ms, 120.5)
        self.assertEqual(eval_obj.feedback, "Execution clean and fast")
        self.assertEqual(eval_obj.evaluator, "system_evaluator")

    def test_evaluation_quality_score_bounds_validation(self):
        with self.assertRaises(ValueError) as ctx:
            Evaluation(
                execution_id="e1",
                task_id="t1",
                agent_id="a1",
                success=True,
                quality_score=1.5,
            )
        self.assertIn("quality_score must be between 0.0 and 1.0", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            Evaluation(
                execution_id="e1",
                task_id="t1",
                agent_id="a1",
                success=True,
                correctness_score=-0.1,
            )
        self.assertIn("correctness_score must be between 0.0 and 1.0", str(ctx.exception))

    def test_evaluation_latency_validation(self):
        with self.assertRaises(ValueError) as ctx:
            Evaluation(
                execution_id="e1",
                task_id="t1",
                agent_id="a1",
                success=False,
                latency_ms=-10.0,
            )
        self.assertIn("latency_ms cannot be negative", str(ctx.exception))

    def test_evaluation_empty_ids_validation(self):
        with self.assertRaises(ValueError):
            Evaluation(execution_id="", task_id="t1", agent_id="a1", success=True)
        with self.assertRaises(ValueError):
            Evaluation(execution_id="e1", task_id="", agent_id="a1", success=True)
        with self.assertRaises(ValueError):
            Evaluation(execution_id="e1", task_id="t1", agent_id="", success=True)

    def test_evaluation_serialization(self):
        eval_obj = Evaluation(
            execution_id="e1",
            task_id="t1",
            agent_id="a1",
            success=True,
            quality_score=0.9,
        )
        eval_dict = eval_obj.to_dict()
        self.assertEqual(eval_dict["execution_id"], "e1")
        self.assertEqual(eval_dict["quality_score"], 0.9)
        self.assertEqual(eval_dict["success"], True)


if __name__ == "__main__":
    unittest.main()
