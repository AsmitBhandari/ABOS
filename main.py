"""
ABOS Entry Point Demonstration
Demonstrates:
1. Multi-Agent Execution Flow (CalculatorAgent, TextAnalysisAgent, UnitConversionAgent)
2. Capability-Based Routing via Orchestrator & DeterministicScheduler
3. ABOS v0.5 Adaptive Feedback Loop (Evaluation -> PerformanceTracker -> AgentProfile -> Scheduler)
"""

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
from orchestration.scheduler import DeterministicScheduler, Scheduler, SchedulingResult


def demonstrate_multi_agent_execution():
    print("=== ABOS Multi-Agent Execution Demonstration ===")
    print()

    orchestrator = Orchestrator()
    calculator = CalculatorAgent(agent_id="agent-calculator-01")
    text_agent = TextAnalysisAgent(agent_id="agent-text-01")
    unit_agent = UnitConversionAgent(agent_id="agent-unit-01")

    orchestrator.register_agent(calculator)
    orchestrator.register_agent(text_agent)
    orchestrator.register_agent(unit_agent)

    # 1. Math Task -> CalculatorAgent
    task_math = Task(
        description="Calculate 25 * 37",
        input_data="25 * 37",
        required_capabilities=["math"],
        priority=TaskPriority.HIGH,
    )
    agent_math = orchestrator.select_agent(task_math)
    res_math = orchestrator.execute_task(task_math)
    print(f"1. Task: {task_math.description}")
    print(f"   Selected Agent: {agent_math.name} ({agent_math.id})")
    print(f"   Result: Success={res_math.success}, Output={res_math.output}, Status={task_math.status.value}")
    print()

    # 2. Text Analysis Task -> TextAnalysisAgent
    task_text = Task(
        description="Count words in sentence",
        input_data="ABOS is an adaptive operating system",
        required_capabilities=["text_analysis"],
        priority=TaskPriority.MEDIUM,
    )
    agent_text = orchestrator.select_agent(task_text)
    res_text = orchestrator.execute_task(task_text)
    print(f"2. Task: {task_text.description} (Input: '{task_text.input_data}')")
    print(f"   Selected Agent: {agent_text.name} ({agent_text.id})")
    print(f"   Result: Success={res_text.success}, Output={res_text.output} words, Status={task_text.status.value}")
    print()

    # 3. Unit Conversion Task -> UnitConversionAgent
    task_unit = Task(
        description="Convert 5 km to m",
        input_data="5 km to m",
        required_capabilities=["unit_conversion"],
        priority=TaskPriority.MEDIUM,
    )
    agent_unit = orchestrator.select_agent(task_unit)
    res_unit = orchestrator.execute_task(task_unit)
    print(f"3. Task: {task_unit.description} (Input: '{task_unit.input_data}')")
    print(f"   Selected Agent: {agent_unit.name} ({agent_unit.id})")
    print(f"   Result: Success={res_unit.success}, Output={res_unit.output} m, Status={task_unit.status.value}")
    print()


def demonstrate_v05_adaptive_feedback():
    print("=== ABOS v0.5: Adaptive Feedback Loop & Performance Tracking ===")
    print()

    # Define Candidate Agents sharing the same capability
    agent_alpha = TextAnalysisAgent(agent_id="agent-text-alpha", name="TextProcessor-Alpha")
    agent_beta = TextAnalysisAgent(agent_id="agent-text-beta", name="TextProcessor-Beta")
    agents = [agent_alpha, agent_beta]

    # Initial profiles: Alpha has a slight historical advantage over Beta
    profile_alpha = AgentProfile(
        agent_id="agent-text-alpha",
        total_executions=10,
        successful_executions=10,
        success_rate=1.00,
        avg_latency_ms=40.0,
        confidence_score=0.50,
        capabilities=["text_analysis"],
    )
    profile_beta = AgentProfile(
        agent_id="agent-text-beta",
        total_executions=20,
        successful_executions=18,
        success_rate=0.90,
        avg_latency_ms=75.0,
        confidence_score=1.00,
        capabilities=["text_analysis"],
    )
    profiles = [profile_alpha, profile_beta]

    scheduler: Scheduler = DeterministicScheduler()
    tracker = PerformanceTracker(confidence_saturation=20)

    task1 = Task(
        description="Process text stream",
        input_data="Telemetry chunk to analyze",
        required_capabilities=["text_analysis"],
    )

    # Initial Scheduling Decision
    initial_schedule: SchedulingResult = scheduler.schedule(task1, agents, profiles)
    print(f"1. Initial Scheduling Decision: Selected '{initial_schedule.selected_agent_id}' (Score: {initial_schedule.score:.4f})")
    print(f"   Alpha Profile: Success={profile_alpha.success_rate:.0%}, Latency={profile_alpha.avg_latency_ms:.1f}ms, Conf={profile_alpha.confidence_score:.2f}")
    print(f"   Beta Profile:  Success={profile_beta.success_rate:.0%}, Latency={profile_beta.avg_latency_ms:.1f}ms, Conf={profile_beta.confidence_score:.2f}")
    print()

    # Simulated Execution failure by Alpha
    exec1 = Execution(task_id=task1.id, agent_id=agent_alpha.id)
    exec1.status = ExecutionStatus.FAILED
    evaluation1 = Evaluation(
        execution_id=exec1.id,
        task_id=task1.id,
        agent_id=agent_alpha.id,
        success=False,
        quality_score=0.10,
        correctness_score=0.00,
        latency_ms=350.0,
        feedback="Text processing timeout.",
    )
    evaluation2 = Evaluation(
        execution_id="exec-alpha-retry-fail",
        task_id=task1.id,
        agent_id=agent_alpha.id,
        success=False,
        quality_score=0.00,
        correctness_score=0.00,
        latency_ms=400.0,
        feedback="Pipeline exception during parsing.",
    )
    print(f"2. Execution Failures & Evaluations Ingested for '{agent_alpha.id}' (Success=False, Latency=350ms, 400ms)")

    # Ingest Evaluations into PerformanceTracker -> Updates AgentProfile
    tracker.update(evaluation1, profile_alpha)
    tracker.update(evaluation2, profile_alpha)
    print(f"3. PerformanceTracker Updated AgentProfile '{profile_alpha.agent_id}':")
    print(f"   Updated Alpha: Success={profile_alpha.success_rate:.1%}, Latency={profile_alpha.avg_latency_ms:.1f}ms, Conf={profile_alpha.confidence_score:.2f}")
    print()

    # Subsequent Scheduling demonstrates adaptation
    task2 = Task(
        description="Process next text stream",
        input_data="Another text batch",
        required_capabilities=["text_analysis"],
    )
    adapted_schedule: SchedulingResult = scheduler.schedule(task2, agents, profiles)
    print(f"4. Adapted Scheduling Decision: Selected '{adapted_schedule.selected_agent_id}' (Score: {adapted_schedule.score:.4f})")
    print(f"   Reason: {adapted_schedule.reason}")
    print()



def main():
    demonstrate_multi_agent_execution()
    demonstrate_v05_adaptive_feedback()
    print("=== ABOS Demonstration Complete ===")


if __name__ == "__main__":
    main()
