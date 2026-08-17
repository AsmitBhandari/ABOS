import unittest
from core.task import Task, TaskPriority
from orchestration.planner import (
    BasePlanner,
    DecompositionValidator,
    DeterministicPlanner,
    Planner,
    PlanningResult,
)


class TestPlanningResult(unittest.TestCase):
    def test_planning_result_creation_and_defaults(self):
        res = PlanningResult(
            task_id="task-001",
            should_decompose=False,
            subtasks=[],
            reason="Atomic task",
        )
        self.assertEqual(res.task_id, "task-001")
        self.assertFalse(res.should_decompose)
        self.assertEqual(res.subtasks, [])
        self.assertEqual(res.reason, "Atomic task")
        self.assertEqual(res.confidence, 1.0)
        self.assertTrue(res.valid)
        self.assertEqual(res.metadata, {})

    def test_planning_result_validation(self):
        with self.assertRaises(ValueError) as ctx:
            PlanningResult(task_id="", should_decompose=False)
        self.assertIn("task_id cannot be empty", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            PlanningResult(task_id="t1", should_decompose=False, confidence=1.5)
        self.assertIn("confidence must be between 0.0 and 1.0", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            PlanningResult(task_id="t1", should_decompose=False, confidence=-0.1)
        self.assertIn("confidence must be between 0.0 and 1.0", str(ctx.exception))

    def test_planning_result_serialization(self):
        child = Task(description="Step 1", input_data=None)
        res = PlanningResult(
            task_id="parent-001",
            should_decompose=True,
            subtasks=[child],
            reason="Decomposed",
            confidence=0.9,
            metadata={"source": "test"},
        )
        d = res.to_dict()
        self.assertEqual(d["task_id"], "parent-001")
        self.assertTrue(d["should_decompose"])
        self.assertEqual(len(d["subtasks"]), 1)
        self.assertEqual(d["subtasks"][0]["description"], "Step 1")
        self.assertEqual(d["confidence"], 0.9)
        self.assertEqual(d["metadata"], {"source": "test"})


class TestDecompositionValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DecompositionValidator()

    def test_valid_decomposition(self):
        parent = Task(description="Parent task", input_data=None)
        child1 = Task(description="Child 1", input_data=None, parent_task_id=parent.id)
        child2 = Task(description="Child 2", input_data=None, parent_task_id=parent.id)
        parent.child_task_ids = [child1.id, child2.id]

        is_valid, errors = self.validator.validate(parent, [child1, child2])
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

    def test_empty_subtasks(self):
        parent = Task(description="Parent task", input_data=None)
        is_valid, errors = self.validator.validate(parent, [])
        self.assertFalse(is_valid)
        self.assertIn("Decomposition must produce at least one subtask.", errors)

    def test_duplicate_child_ids(self):
        parent = Task(description="Parent task", input_data=None)
        child1 = Task(description="Child 1", input_data=None, parent_task_id=parent.id, id="dup-id")
        child2 = Task(description="Child 2", input_data=None, parent_task_id=parent.id, id="dup-id")
        parent.child_task_ids = ["dup-id"]

        is_valid, errors = self.validator.validate(parent, [child1, child2])
        self.assertFalse(is_valid)
        self.assertTrue(any("unique" in e for e in errors))

    def test_mismatched_parent_id(self):
        parent = Task(description="Parent task", input_data=None)
        child = Task(description="Child", input_data=None, parent_task_id="wrong-parent-id")
        parent.child_task_ids = [child.id]

        is_valid, errors = self.validator.validate(parent, [child])
        self.assertFalse(is_valid)
        self.assertTrue(any("does not match parent ID" in e for e in errors))

    def test_child_assigned_agent_id_fails(self):
        parent = Task(description="Parent task", input_data=None)
        child = Task(
            description="Child",
            input_data=None,
            parent_task_id=parent.id,
            assigned_agent_id="agent-007",
        )
        parent.child_task_ids = [child.id]

        is_valid, errors = self.validator.validate(parent, [child])
        self.assertFalse(is_valid)
        self.assertTrue(any("must not have assigned_agent_id" in e for e in errors))

    def test_empty_child_description(self):
        parent = Task(description="Parent task", input_data=None)
        child = Task(description="", input_data=None, parent_task_id=parent.id)
        parent.child_task_ids = [child.id]

        is_valid, errors = self.validator.validate(parent, [child])
        self.assertFalse(is_valid)
        self.assertTrue(any("description cannot be empty" in e for e in errors))

    def test_inconsistent_parent_child_task_ids(self):
        parent = Task(description="Parent task", input_data=None)
        child = Task(description="Child 1", input_data=None, parent_task_id=parent.id)
        # Parent child_task_ids not updated
        parent.child_task_ids = []

        is_valid, errors = self.validator.validate(parent, [child])
        self.assertFalse(is_valid)
        self.assertTrue(any("does not match generated subtasks" in e for e in errors))


class TestDeterministicPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = DeterministicPlanner()

    def test_planner_contract_inheritance(self):
        self.assertIsInstance(self.planner, Planner)
        self.assertIsInstance(self.planner, BasePlanner)

    def test_atomic_task_no_decomposition(self):
        task = Task(description="Calculate 25 * 37", input_data="25 * 37")
        result = self.planner.plan(task)

        self.assertEqual(result.task_id, task.id)
        self.assertFalse(result.should_decompose)
        self.assertEqual(result.subtasks, [])
        self.assertEqual(result.confidence, 1.0)
        self.assertTrue(result.valid)
        self.assertIn("atomic", result.reason.lower())
        self.assertEqual(task.child_task_ids, [])

    def test_decomposable_task_oxford_comma_example_1(self):
        task = Task(
            description="Research competitors, compare pricing, and prepare a report.",
            priority=TaskPriority.HIGH,
        )
        result = self.planner.plan(task)

        self.assertTrue(result.should_decompose)
        self.assertEqual(len(result.subtasks), 3)
        self.assertEqual(result.subtasks[0].description, "Research competitors")
        self.assertEqual(result.subtasks[1].description, "compare pricing")
        self.assertEqual(result.subtasks[2].description, "prepare a report")

        # Verify parent-child hierarchy
        self.assertEqual(task.child_task_ids, [c.id for c in result.subtasks])
        for child in result.subtasks:
            self.assertEqual(child.parent_task_id, task.id)
            self.assertIsNone(child.assigned_agent_id)
            self.assertEqual(child.priority, TaskPriority.HIGH)

    def test_decomposable_task_oxford_comma_example_2(self):
        task = Task(
            description="Collect data, analyze the data, and summarize the findings.",
            priority=TaskPriority.MEDIUM,
        )
        result = self.planner.plan(task)

        self.assertTrue(result.should_decompose)
        self.assertEqual(len(result.subtasks), 3)
        self.assertEqual(result.subtasks[0].description, "Collect data")
        self.assertEqual(result.subtasks[1].description, "analyze the data")
        self.assertEqual(result.subtasks[2].description, "summarize the findings")

        self.assertEqual(task.child_task_ids, [c.id for c in result.subtasks])
        for child in result.subtasks:
            self.assertEqual(child.parent_task_id, task.id)
            self.assertIsNone(child.assigned_agent_id)

    def test_decomposable_task_numbered_steps(self):
        task = Task(
            description="Execute deployment pipeline",
            input_data="1. Run unit tests\n2. Build container image\n3. Deploy to staging",
        )
        result = self.planner.plan(task)

        self.assertTrue(result.should_decompose)
        self.assertEqual(len(result.subtasks), 3)
        self.assertEqual(result.subtasks[0].description, "Run unit tests")
        self.assertEqual(result.subtasks[1].description, "Build container image")
        self.assertEqual(result.subtasks[2].description, "Deploy to staging")

    def test_decomposable_task_sequential_connectives(self):
        task = Task(description="Fetch server logs then filter error entries and then notify admin")
        result = self.planner.plan(task)

        self.assertTrue(result.should_decompose)
        self.assertEqual(len(result.subtasks), 3)
        self.assertEqual(result.subtasks[0].description, "Fetch server logs")
        self.assertEqual(result.subtasks[1].description, "filter error entries")
        self.assertEqual(result.subtasks[2].description, "notify admin")

    def test_planner_does_not_execute_task(self):
        task = Task(description="Calculate 25 * 37", input_data="25 * 37")
        result = self.planner.plan(task)
        # Verify that task status and result remain untouched
        self.assertIsNone(task.result)
        self.assertIsNone(result.metadata.get("execution"))


if __name__ == "__main__":
    unittest.main()
