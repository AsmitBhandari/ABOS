import unittest
from agents import CalculatorAgent, TextAnalysisAgent, UnitConversionAgent
from core import (
    AgentProfile,
    Evaluation,
    Execution,
    ExecutionStatus,
    Orchestrator,
    Result,
    Task,
    TaskPriority,
)
from orchestration.performance import PerformanceTracker
from orchestration.scheduler import DeterministicScheduler, SchedulingResult


class TestMultiAgentRouting(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        self.scheduler = DeterministicScheduler()
        self.tracker = PerformanceTracker(confidence_saturation=20)

        # Instantiate all three canonical agents
        self.calc_agent = CalculatorAgent(agent_id="agent-calculator-01")
        self.text_agent = TextAnalysisAgent(agent_id="agent-text-01")
        self.unit_agent = UnitConversionAgent(agent_id="agent-unit-01")

        self.agents = [self.calc_agent, self.text_agent, self.unit_agent]

        for agent in self.agents:
            self.orchestrator.register_agent(agent)

    def test_capability_based_filtering_and_scheduling(self):
        """
        Verify that tasks requiring specific capabilities select the matching agent
        and reject the non-matching agents.
        """
        # 1. Math Task -> CalculatorAgent
        task_math = Task(
            description="Calculate arithmetic",
            input_data="12 * 8",
            required_capabilities=["math"],
        )
        res_math = self.scheduler.schedule(task_math, self.agents)
        self.assertTrue(res_math.success)
        self.assertEqual(res_math.selected_agent_id, "agent-calculator-01")

        # Verify other agents were rejected for missing capabilities
        cands_math = {c.agent_id: c for c in res_math.candidates}
        self.assertTrue(cands_math["agent-calculator-01"].eligible)
        self.assertFalse(cands_math["agent-text-01"].eligible)
        self.assertFalse(cands_math["agent-unit-01"].eligible)

        # 2. Text Analysis Task -> TextAnalysisAgent
        task_text = Task(
            description="Count words in text",
            input_data="ABOS supports heterogeneous agents",
            required_capabilities=["text_analysis"],
        )
        res_text = self.scheduler.schedule(task_text, self.agents)
        self.assertTrue(res_text.success)
        self.assertEqual(res_text.selected_agent_id, "agent-text-01")

        cands_text = {c.agent_id: c for c in res_text.candidates}
        self.assertFalse(cands_text["agent-calculator-01"].eligible)
        self.assertTrue(cands_text["agent-text-01"].eligible)
        self.assertFalse(cands_text["agent-unit-01"].eligible)

        # 3. Unit Conversion Task -> UnitConversionAgent
        task_unit = Task(
            description="Convert distance",
            input_data="5 km to m",
            required_capabilities=["unit_conversion"],
        )
        res_unit = self.scheduler.schedule(task_unit, self.agents)
        self.assertTrue(res_unit.success)
        self.assertEqual(res_unit.selected_agent_id, "agent-unit-01")

        cands_unit = {c.agent_id: c for c in res_unit.candidates}
        self.assertFalse(cands_unit["agent-calculator-01"].eligible)
        self.assertFalse(cands_unit["agent-text-01"].eligible)
        self.assertTrue(cands_unit["agent-unit-01"].eligible)

    def test_multi_agent_execution_via_orchestrator(self):
        """
        Verify end-to-end execution of distinct task types by all three specialized agents.
        """
        # Task 1: Calculator
        task1 = Task(
            description="Calculate 25 * 37",
            input_data="25 * 37",
            required_capabilities=["math"],
        )
        agent1 = self.orchestrator.select_agent(task1)
        self.assertEqual(agent1.id, "agent-calculator-01")
        res1 = self.orchestrator.execute_task(task1)
        self.assertTrue(res1.success)
        self.assertEqual(res1.output, 925)

        # Task 2: Text Analysis
        task2 = Task(
            description="Count words in sentence",
            input_data="ABOS is an adaptive operating system",
            required_capabilities=["text_analysis"],
        )
        agent2 = self.orchestrator.select_agent(task2)
        self.assertEqual(agent2.id, "agent-text-01")
        res2 = self.orchestrator.execute_task(task2)
        self.assertTrue(res2.success)
        self.assertEqual(res2.output, 6)


        # Task 3: Unit Conversion
        task3 = Task(
            description="Convert 5 km to m",
            input_data="5 km to m",
            required_capabilities=["unit_conversion"],
        )
        agent3 = self.orchestrator.select_agent(task3)
        self.assertEqual(agent3.id, "agent-unit-01")
        res3 = self.orchestrator.execute_task(task3)
        self.assertTrue(res3.success)
        self.assertEqual(res3.output, 5000)

    def test_performance_aware_routing_between_same_capability_agents(self):
        """
        Verify that when multiple agents share the same capability, Scheduler uses
        AgentProfile performance metrics to select the best agent, and adapts when
        PerformanceTracker updates historical profiles.
        """
        # Two text analysis agents
        text_agent_alpha = TextAnalysisAgent(agent_id="agent-text-alpha", name="TextAgent-Alpha")
        text_agent_beta = TextAnalysisAgent(agent_id="agent-text-beta", name="TextAgent-Beta")
        candidate_agents = [text_agent_alpha, text_agent_beta]

        # Initial profiles: Alpha has higher success rate and lower latency
        profile_alpha = AgentProfile(
            agent_id="agent-text-alpha",
            total_executions=20,
            successful_executions=20,
            success_rate=1.00,
            avg_latency_ms=40.0,
            confidence_score=1.00,
            capabilities=["text_analysis"],
        )
        profile_beta = AgentProfile(
            agent_id="agent-text-beta",
            total_executions=20,
            successful_executions=16,
            success_rate=0.80,
            avg_latency_ms=100.0,
            confidence_score=1.00,
            capabilities=["text_analysis"],
        )
        profiles = [profile_alpha, profile_beta]

        task = Task(
            description="Analyze log line",
            input_data="ERROR 404 resource not found",
            required_capabilities=["text_analysis"],
        )

        # 1. Initial Schedule -> Alpha is selected
        sched1: SchedulingResult = self.scheduler.schedule(task, candidate_agents, profiles)
        self.assertTrue(sched1.success)
        self.assertEqual(sched1.selected_agent_id, "agent-text-alpha")

        # 2. Alpha encounters multiple failures and slow latency
        for i in range(5):
            eval_alpha_fail = Evaluation(
                execution_id=f"exec-alpha-fail-{i}",
                task_id=f"task-text-{i}",
                agent_id="agent-text-alpha",
                success=False,
                latency_ms=450.0,
            )
            self.tracker.update(eval_alpha_fail, profile_alpha)

        # Verify Alpha profile has degraded
        self.assertEqual(profile_alpha.total_executions, 25)
        self.assertEqual(profile_alpha.successful_executions, 20)
        self.assertEqual(profile_alpha.success_rate, 20 / 25)  # 0.80

        # 3. Subsequent Schedule -> Beta is now selected due to better latency
        sched2: SchedulingResult = self.scheduler.schedule(task, candidate_agents, profiles)
        self.assertTrue(sched2.success)
        self.assertEqual(sched2.selected_agent_id, "agent-text-beta")


if __name__ == "__main__":
    unittest.main()
