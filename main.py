"""
ABOS Entry Point Demonstration
Demonstrates:
1. ABOS v0.4: Performance-Aware Scheduler & Agent Selection
2. ABOS v0.1: CalculatorAgent Task Execution Flow
"""

from agents.calculator_agent import CalculatorAgent
from core import AgentProfile, AgentState, BaseAgent, Orchestrator, Result, Task, TaskPriority
from orchestration.scheduler import DeterministicScheduler, Scheduler, SchedulingResult


class MockWorkerAgent(BaseAgent):
    """Worker agent for scheduling demonstration."""

    def execute(self, task: Task) -> Result:
        return Result(
            success=True,
            output=f"Executed task: {task.description}",
            agent_id=self.id,
        )


def demonstrate_v04_scheduler():
    print("=== ABOS v0.4: Scheduler & Performance-Aware Agent Selection ===")
    print()

    # 1. Define Task with required capabilities
    task = Task(
        description="Analyze telemetry data and compute statistics",
        required_capabilities=["python"],
        priority=TaskPriority.HIGH,
    )
    print(f"Task: '{task.description}'")
    print(f"  Required Capabilities: {task.required_capabilities}")
    print()

    # 2. Define Candidate Agents
    agent_a = MockWorkerAgent(
        name="DataProcessor-Alpha",
        capabilities=["python", "math"],
        agent_id="agent-python-alpha",
    )
    agent_b = MockWorkerAgent(
        name="DataProcessor-Beta",
        capabilities=["python"],
        agent_id="agent-python-beta",
    )
    agent_c = MockWorkerAgent(
        name="ResearchAgent-Gamma",
        capabilities=["research"],
        agent_id="agent-research-gamma",
    )

    agents = [agent_a, agent_b, agent_c]

    # 3. Define Historical Performance Profiles
    profile_a = AgentProfile(
        agent_id="agent-python-alpha",
        total_executions=50,
        successful_executions=49,
        success_rate=0.98,
        avg_latency_ms=85.0,
        confidence_score=0.95,
        capabilities=["python", "math"],
    )
    profile_b = AgentProfile(
        agent_id="agent-python-beta",
        total_executions=50,
        successful_executions=38,
        success_rate=0.76,
        avg_latency_ms=320.0,
        confidence_score=0.70,
        capabilities=["python"],
    )
    profile_c = AgentProfile(
        agent_id="agent-research-gamma",
        total_executions=20,
        successful_executions=19,
        success_rate=0.95,
        avg_latency_ms=110.0,
        confidence_score=0.90,
        capabilities=["research"],
    )

    profiles = [profile_a, profile_b, profile_c]

    print("Candidate Agents & Historical Profiles:")
    for a in agents:
        p = next((prof for prof in profiles if prof.agent_id == a.id), None)
        prof_info = (
            f"Success: {p.success_rate:.0%}, Latency: {p.avg_latency_ms}ms, Conf: {p.confidence_score}"
            if p
            else "No profile"
        )
        print(f"  - [{a.id}] {a.name}: caps={a.capabilities}, state={a.state.value} | {prof_info}")
    print()

    # 4. Schedule Task using DeterministicScheduler
    scheduler: Scheduler = DeterministicScheduler()
    scheduling_result: SchedulingResult = scheduler.schedule(task, agents, profiles)

    print("Scheduling Result:")
    print(f"  Success:           {scheduling_result.success}")
    print(f"  Selected Agent ID: {scheduling_result.selected_agent_id}")
    print(f"  Score:             {scheduling_result.score}")
    print(f"  Reason:            {scheduling_result.reason}")
    print()
    print("Candidate Breakdown:")
    for cand in scheduling_result.candidates:
        elig_str = "ELIGIBLE" if cand.eligible else f"REJECTED ({cand.rejection_reason})"
        print(f"  - [{cand.agent_id}] Total Score: {cand.total_score:.4f} | {elig_str}")
    print()


def demonstrate_v01_execution():
    print("=== ABOS v0.1: CalculatorAgent Task Execution Flow ===")
    print()

    orchestrator = Orchestrator()
    calculator = CalculatorAgent()
    orchestrator.register_agent(calculator)

    expression = "25 * 37"
    task = Task(
        description=f"Calculate {expression}",
        input_data=expression,
        priority=TaskPriority.HIGH,
    )

    print(f"Task: {task.description} (Input: {task.input_data})")
    selected_agent = orchestrator.select_agent(task)
    if selected_agent:
        print(f"Selected Agent: {selected_agent.name} ({selected_agent.id})")
        result = orchestrator.execute_task(task)
        print(f"Result: Success={result.success}, Output={result.output}, Error={result.error}")
        print(f"Task Status: {task.status.value}")
    print()


def main():
    demonstrate_v04_scheduler()
    demonstrate_v01_execution()
    print("=== ABOS Demonstration Complete ===")


if __name__ == "__main__":
    main()
